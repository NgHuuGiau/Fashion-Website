"""Download 90 real, ID-matched products; never generate names or product photos."""

import csv
import hashlib
import json
import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal, ROUND_HALF_UP
from io import BytesIO
from pathlib import Path
from urllib.parse import quote, urlparse

import requests
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".tmp-catalog"
MEDIA = ROOT / "frontend/static/images"
SOURCE = "https://www.kaggle.com/datasets/paramaggarwal/fashion-product-images-dataset"
DOWNLOAD = "https://www.kaggle.com/api/v1/datasets/download/paramaggarwal/fashion-product-images-dataset/"
# shortcut: archived INR prices converted for display only; enter shop prices before selling.
RATE = Decimal("272.0287")
RATE_SOURCE = "https://www.investing.com/currencies/inr-vnd-historical-data"
PLAN = {
    "ao": {
        "Shirts": 8,
        "Tshirts": 8,
        "Tops": 4,
        "Sweatshirts": 3,
        "Sweaters": 3,
        "Jackets": 4,
    },
    "quan": {"Jeans": 12, "Trousers": 12, "Track Pants": 8, "Shorts": 8},
    "phu-kien": {
        "Caps": 4,
        "Backpacks": 4,
        "Handbags": 3,
        "Wallets": 3,
        "Belts": 3,
        "Sunglasses": 3,
    },
}
CATEGORIES = {"ao": "Áo", "quan": "Quần", "phu-kien": "Phụ kiện"}
TYPES = {
    "Shirts": "Áo sơ mi",
    "Tshirts": "Áo thun",
    "Tops": "Áo kiểu",
    "Sweatshirts": "Áo nỉ",
    "Sweaters": "Áo len",
    "Jackets": "Áo khoác",
    "Jeans": "Quần jeans",
    "Trousers": "Quần dài",
    "Track Pants": "Quần thể thao",
    "Shorts": "Quần short",
    "Caps": "Mũ lưỡi trai",
    "Backpacks": "Ba lô",
    "Handbags": "Túi xách",
    "Wallets": "Ví",
    "Belts": "Thắt lưng",
    "Sunglasses": "Kính mát",
}
LABELS = {
    "Fabric": "Chất liệu",
    "Material": "Chất liệu",
    "Fit": "Phom dáng",
    "Pattern": "Họa tiết",
    "Sleeve Length": "Độ dài tay",
    "Collar": "Cổ áo",
    "Neck": "Kiểu cổ",
    "Length": "Chiều dài",
    "Waist Rise": "Cạp quần",
    "Closure": "Kiểu khóa",
    "Number of Pockets": "Số túi",
    "Occasion": "Dịp sử dụng",
    "Lens Colour": "Màu tròng kính",
    "Frame Material": "Chất liệu gọng",
    "Frame Colour": "Màu gọng",
    "Type": "Kiểu",
    "Multipack Set": "Quy cách",
}
VALUES = {
    "Men": "Nam",
    "Women": "Nữ",
    "Unisex": "Unisex",
    "Casual": "Hằng ngày",
    "Sports": "Thể thao",
    "Formal": "Trang trọng",
    "Black": "Đen",
    "Blue": "Xanh dương",
    "Navy Blue": "Xanh navy",
    "White": "Trắng",
    "Grey": "Xám",
    "Brown": "Nâu",
    "Green": "Xanh lá",
    "Red": "Đỏ",
    "Pink": "Hồng",
    "Purple": "Tím",
    "Beige": "Be",
    "Yellow": "Vàng",
    "Olive": "Xanh ô liu",
    "Orange": "Cam",
    "Multi": "Nhiều màu",
    "Cotton": "Cotton",
    "Polyester": "Polyester",
    "Denim": "Denim",
    "Leather": "Da",
    "Slim Fit": "Slim fit",
    "Regular Fit": "Regular fit",
    "Checked": "Kẻ ô",
    "Solid": "Trơn",
    "Striped": "Kẻ sọc",
    "Printed": "In họa tiết",
    "Long Sleeves": "Tay dài",
    "Short Sleeves": "Tay ngắn",
    "Sleeveless": "Không tay",
    "Round Neck": "Cổ tròn",
    "V-Neck": "Cổ V",
    "Spread Collar": "Cổ bẻ",
}


def fetch(url, cache_path):
    if cache_path.exists():
        return cache_path.read_bytes()
    response = requests.get(url, timeout=35)
    response.raise_for_status()
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_bytes(response.content)
    return response.content


def download_image(style_id, angle, url):
    url = url.replace("http://", "https://", 1)
    if urlparse(url).hostname != "assets.myntassets.com":
        raise ValueError("Unexpected product image host")
    relative = Path("products/sourced/myntra") / style_id / f"{angle}.jpg"
    blob = fetch(url, MEDIA / relative)
    if len(blob) > 5 * 1024 * 1024:
        raise ValueError("Image exceeds upload limit")
    with Image.open(BytesIO(blob)) as image:
        width, height = image.size
        if image.format != "JPEG" or min(width, height) < 600:
            raise ValueError("Image is not a high-resolution JPEG")
        image.verify()
    return {
        "file": relative.as_posix(),
        "url": url,
        "angle": angle,
        "width": width,
        "height": height,
        "sha256": hashlib.sha256(blob).hexdigest(),
    }


def prepare_product(row, category, expected_image):
    style_id = row["styleID"]
    path = f"fashion-dataset/styles/{style_id}.json"
    raw = fetch(DOWNLOAD + quote(path, safe=""), CACHE / "source" / f"{style_id}.json")
    data = json.loads(raw)["data"]
    if (
        str(data["id"]) != style_id
        or data["productDisplayName"].strip() != row["productDisplayName"].strip()
    ):
        raise ValueError("Source ID/name mismatch")
    article = data["articleType"]["typeName"]
    if article != row["articleType"] or data["gender"] not in {
        "Men",
        "Women",
        "Unisex",
    }:
        raise ValueError("Source type/gender mismatch")
    angles = []
    seen = set()
    for angle in (
        "default",
        "front",
        "back",
        "left",
        "right",
        "top",
        "bottom",
        "detail",
    ):
        item = data["styleImages"].get(angle)
        if (
            isinstance(item, dict)
            and item.get("imageURL")
            and item["imageURL"] not in seen
        ):
            seen.add(item["imageURL"])
            angles.append((style_id, angle, item["imageURL"]))
    if not angles or angles[0][2].replace("http:", "https:") != expected_image.replace(
        "http:", "https:"
    ):
        raise ValueError("CSV/JSON cover mismatch")
    with ThreadPoolExecutor(max_workers=4) as pool:
        images = list(pool.map(lambda args: download_image(*args), angles[:6]))
    unique = {image["sha256"]: image for image in reversed(images)}
    images = list(reversed(list(unique.values())))
    if len(images) < (2 if category == "phu-kien" else 4):
        raise ValueError("Not enough distinct source photos")
    attrs = data.get("articleAttributes", {})
    bullets = [
        f"Loại sản phẩm: {TYPES[article]}",
        f"Thương hiệu: {data['brandName']}",
        f"Dành cho: {VALUES.get(data['gender'], data['gender'])}",
        f"Màu theo nguồn: {VALUES.get(data['baseColour'], data['baseColour'])}",
    ]
    for key, value in attrs.items():
        if key in LABELS and value and value not in {"NA", "N/A"}:
            bullets.append(f"{LABELS[key]}: {VALUES.get(value, value)}")
    if data.get("usage"):
        bullets.append(f"Phong cách: {VALUES.get(data['usage'], data['usage'])}")
    source_price = Decimal(str(data.get("discountedPrice") or data["price"]))
    price = int((source_price * RATE).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    return {
        "name": data["productDisplayName"].strip(),
        "slug": f"myntra-{style_id}",
        "sku": f"MYNTRA-{style_id}",
        "category_slug": category,
        "category_name": CATEGORIES[category],
        "brand": data["brandName"],
        "price": price,
        "featured": False,
        "spec_bullets": bullets,
        "descriptors": data.get("productDescriptors", {}),
        "images": images,
        "attributes": {
            "source": "myntra-kaggle",
            "source_id": style_id,
            "source_url": "https://www.myntra.com/" + data["landingPageUrl"],
            "dataset_url": SOURCE,
            "source_json": path,
            "source_sha256": hashlib.sha256(raw).hexdigest(),
            "source_name": data["productDisplayName"].strip(),
            "article_type": article,
            "color": data["baseColour"],
            "gender": data["gender"],
            "material": attrs.get("Fabric") or attrs.get("Material", ""),
            "source_attributes": attrs,
            "source_price_inr": str(source_price),
            "price_is_reference": True,
            "inr_vnd_rate": str(RATE),
            "rate_date": "2026-10-13",
            "rate_source": RATE_SOURCE,
            "dataset_license_label": "MIT (Kaggle metadata); third-party image rights not independently verified",
            "source_archive_year": row["year"],
        },
    }


def main():
    CACHE.mkdir(exist_ok=True)
    for filename in ("styles.csv", "images.csv"):
        fetch(
            "https://raw.githubusercontent.com/dcupl-demos/fashion-products/main/dcupl/data/"
            + filename,
            CACHE / filename,
        )
    with (CACHE / "styles.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    with (CACHE / "images.csv").open(encoding="utf-8", newline="") as stream:
        covers = {row["styleID"]: row["link"] for row in csv.DictReader(stream)}
    products = []
    names = set()
    for category, groups in PLAN.items():
        for article, count in groups.items():
            selected = 0
            for row in rows:
                if (
                    row["articleType"] != article
                    or row["gender"] not in {"Men", "Women", "Unisex"}
                    or row["productDisplayName"] in names
                    or re.search(
                        r"\b(kidswear|kids|boy|boys|girl|girls|baby|infant)\b",
                        row["productDisplayName"],
                        re.I,
                    )
                ):
                    continue
                try:
                    product = prepare_product(row, category, covers[row["styleID"]])
                except (
                    requests.RequestException,
                    ValueError,
                    KeyError,
                    OSError,
                ) as error:
                    print(f"Skip {row['styleID']}: {error}", flush=True)
                    continue
                products.append(product)
                names.add(product["name"])
                selected += 1
                print(
                    f"{len(products):02d}/90 {product['sku']} {product['name']} ({len(product['images'])} photos)",
                    flush=True,
                )
                if selected == count:
                    break
            if selected != count:
                raise RuntimeError(
                    f"Not enough verified products: {article} {selected}/{count}"
                )
    assert Counter(p["category_slug"] for p in products) == {
        "ao": 30,
        "quan": 40,
        "phu-kien": 20,
    }
    assert len({p["sku"] for p in products}) == len(names) == 90
    target = ROOT / "database/seed/local_products_to_sync.json"
    target.write_text(
        json.dumps(products, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        f"Saved {len(products)} products, {sum(len(p['images']) for p in products)} source photos: {target}"
    )


if __name__ == "__main__":
    main()
