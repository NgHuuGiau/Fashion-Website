"""Form/matrix builders tach tu admin_product_dashboard (P1.1).

Chi chua logic thuan tuy (khong query nang ngoai from_instance),
de file dashboard 1286 dong giam con ~1/2 va de test rieng.
"""

import re

from products.models import MAX_PRODUCT_GALLERY_IMAGES

from .cart import safe_int
from .models import OrderItem

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024

DEFAULT_MATRIX_COLORS = [{"name": "Đen", "code": "#111111"}]
DEFAULT_MATRIX_SIZES = ["S", "M", "L", "XL"]


def _validate_uploaded_file(uploaded_file, errors, label):
    if not uploaded_file:
        return
    if uploaded_file.size > MAX_IMAGE_SIZE:
        errors.append(f"{label}: File không được quá 5MB.")
        return
    try:
        from PIL import Image
        import io

        Image.open(io.BytesIO(uploaded_file.read()))
        uploaded_file.seek(0)
    except Exception:
        errors.append(f"{label}: File không phải là ảnh hợp lệ.")


def build_gallery_slot_rows(product=None):
    slots = []
    images_by_sort_order = {}
    if product:
        images_by_sort_order = {
            item.sort_order: item
            for item in product.gallery_images.order_by("sort_order", "id")[
                :MAX_PRODUCT_GALLERY_IMAGES
            ]
        }

    for index in range(MAX_PRODUCT_GALLERY_IMAGES):
        slots.append(
            {
                "slot_index": index,
                "label": f"Slot {index + 1}",
                "image": images_by_sort_order.get(index),
            }
        )
    return slots


def _size_token(size: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", (size or "").strip()) or "size"


def _matrix_post_to_arrays(post_data):
    sizes = [
        size.strip()
        for size in post_data.getlist("matrix_sizes")
        if size and size.strip()
    ]
    color_names = post_data.getlist("matrix_color_name[]")
    color_codes = post_data.getlist("matrix_color_code[]")
    active_indexes = {
        value.strip()
        for value in post_data.getlist("matrix_color_active[]")
        if value.strip()
    }

    row_keys, names, codes, size_list, stocks, active_keys = [], [], [], [], [], []
    for index, color_name in enumerate(color_names):
        color_code = color_codes[index] if index < len(color_codes) else "#111111"
        is_active = str(index) in active_indexes
        for size in sizes:
            token = _size_token(size)
            stock_raw = post_data.get(f"matrix_stock_{index}_{token}", "").strip()
            row_key = f"mat-{index}-{token}"
            row_keys.append(row_key)
            names.append(color_name.strip())
            codes.append(color_code.strip())
            size_list.append(size)
            stocks.append(stock_raw if stock_raw else "0")
            if is_active:
                active_keys.append(row_key)

    return {
        "variant_row_key": row_keys,
        "variant_color_name": names,
        "variant_color_code": codes,
        "variant_size": size_list,
        "variant_stock": stocks,
        "variant_is_active": active_keys,
    }


def build_admin_product_form_data(request=None):
    if request is None:
        return {
            "product_id": "",
            "category_id": "",
            "name": "",
            "price": "",
            "stock": "",
            "description": "",
            "image_url": "",
            "gallery_count": 0,
            "available": True,
            "featured": False,
            "variant_row_key": [
                f"row-{index + 1}" for index in range(len(DEFAULT_MATRIX_SIZES))
            ],
            "variant_color_name": [DEFAULT_MATRIX_COLORS[0]["name"]]
            * len(DEFAULT_MATRIX_SIZES),
            "variant_color_code": [DEFAULT_MATRIX_COLORS[0]["code"]]
            * len(DEFAULT_MATRIX_SIZES),
            "variant_size": list(DEFAULT_MATRIX_SIZES),
            "variant_stock": ["0"] * len(DEFAULT_MATRIX_SIZES),
            "variant_is_active": [
                f"row-{index + 1}" for index in range(len(DEFAULT_MATRIX_SIZES))
            ],
        }

    variant_arrays = (
        _matrix_post_to_arrays(request.POST)
        if "matrix_sizes" in request.POST
        else {
            "variant_row_key": request.POST.getlist("variant_row_key[]"),
            "variant_color_name": request.POST.getlist("variant_color_name[]"),
            "variant_color_code": request.POST.getlist("variant_color_code[]"),
            "variant_size": request.POST.getlist("variant_size[]"),
            "variant_stock": request.POST.getlist("variant_stock[]"),
            "variant_is_active": request.POST.getlist("variant_is_active[]"),
        }
    )

    return {
        "product_id": request.POST.get("product_id", "").strip(),
        "category_id": request.POST.get("category_id", "").strip(),
        "name": request.POST.get("name", "").strip(),
        "price": request.POST.get("price", "").strip(),
        "stock": request.POST.get("stock", "").strip(),
        "description": request.POST.get("description", "").strip(),
        "image_url": request.POST.get("image_url", "").strip(),
        "gallery_count": safe_int(
            request.POST.get("gallery_count", "0"), default=0, minimum=0
        ),
        "remove_gallery_image_ids": request.POST.getlist("remove_gallery_image_ids"),
        "available": request.POST.get("available") == "on",
        "featured": request.POST.get("featured") == "on",
        **variant_arrays,
    }


def build_admin_product_form_from_instance(product):
    all_variants = list(product.variants.order_by("color_name", "size"))
    historical_variant_ids = set(
        OrderItem.objects.filter(
            variant_id__in=[v.pk for v in all_variants]
        ).values_list("variant_id", flat=True)
    )
    variants = [
        variant
        for variant in all_variants
        if variant.is_active or variant.pk not in historical_variant_ids
    ]
    if not variants and not all_variants:
        variants = [None]

    form_data = {
        "product_id": str(product.id),
        "category_id": str(product.category_id),
        "name": product.name,
        "price": str(int(product.price)),
        "stock": str(product.stock),
        "description": product.description,
        "image_url": product.image_url,
        "gallery_count": product.gallery_images.count(),
        "remove_gallery_image_ids": [],
        "available": product.available,
        "featured": product.featured,
        "variant_row_key": [],
        "variant_color_name": [],
        "variant_color_code": [],
        "variant_size": [],
        "variant_stock": [],
        "variant_is_active": [],
    }

    for index, variant in enumerate(variants, start=1):
        row_key = f"row-{index}"
        form_data["variant_row_key"].append(row_key)
        form_data["variant_color_name"].append(variant.color_name if variant else "Đen")
        form_data["variant_color_code"].append(
            variant.color_code if variant else "#111111"
        )
        form_data["variant_size"].append(variant.size if variant else "M")
        form_data["variant_stock"].append(str(variant.stock) if variant else "0")
        if variant is None or variant.is_active:
            form_data["variant_is_active"].append(row_key)

    return form_data


def build_variant_rows(form_data):
    variant_rows = []
    max_rows = max(
        len(form_data["variant_row_key"]),
        len(form_data["variant_color_name"]),
        len(form_data["variant_color_code"]),
        len(form_data["variant_size"]),
        len(form_data["variant_stock"]),
        1,
    )
    active_keys = set(form_data["variant_is_active"])
    for index in range(max_rows):
        row_key = (
            form_data["variant_row_key"][index]
            if index < len(form_data["variant_row_key"])
            else f"row-{index + 1}"
        )
        variant_rows.append(
            {
                "row_key": row_key,
                "color_name": form_data["variant_color_name"][index]
                if index < len(form_data["variant_color_name"])
                else "",
                "color_code": form_data["variant_color_code"][index]
                if index < len(form_data["variant_color_code"])
                else "#111111",
                "size": form_data["variant_size"][index]
                if index < len(form_data["variant_size"])
                else "",
                "stock": form_data["variant_stock"][index]
                if index < len(form_data["variant_stock"])
                else "0",
                "is_active": row_key in active_keys,
            }
        )
    return variant_rows


def build_variant_matrix(form_data):
    rows = build_variant_rows(form_data)

    color_rows = []
    color_index_by_key = {}
    size_index_by_key = {}
    sizes = []
    cell_stock = {}

    for row in rows:
        color_name = row["color_name"].strip()
        size = row["size"].strip().upper()
        if not any([color_name, size, row["stock"]]):
            continue
        color_key = color_name.casefold()
        if color_key not in color_index_by_key:
            color_index_by_key[color_key] = len(color_rows)
            color_rows.append(
                {
                    "index": len(color_rows),
                    "name": color_name,
                    "code": row["color_code"].strip() or "#111111",
                    "is_active": row["is_active"],
                }
            )
        if size and size not in size_index_by_key:
            size_index_by_key[size] = len(sizes)
            sizes.append(size)
        if size:
            cell_stock[(color_index_by_key[color_key], size_index_by_key[size])] = str(
                row["stock"]
            )

    for color in color_rows:
        color["stocks"] = [
            {
                "size": size,
                "token": _size_token(size),
                "stock": cell_stock.get((color["index"], index), "0"),
            }
            for index, size in enumerate(sizes)
        ]

    return {"colors": color_rows, "sizes": sizes}
