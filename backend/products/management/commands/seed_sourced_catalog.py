"""Import the verified local catalog without deleting products or order history."""

import hashlib
import json
import re
from collections import Counter
from html import unescape
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.html import strip_tags
from django.utils.text import slugify

from core.demo_data import refuse_demo_seed_in_production
from products.models import Brand, Category, Product, ProductImage
from products.validators import validate_product_image


def descriptor_text(descriptors):
    sections = []
    for item in descriptors.values():
        value = item.get("value", "")
        value = re.sub(r"<(?:br\s*/?|/p|/div|/li)>", "\n", value, flags=re.I)
        text = unescape(strip_tags(value)).strip()
        if text:
            sections.append(text)
    return "\n\n".join(sections)


class Command(BaseCommand):
    help = "Nhập đúng 30 áo, 40 quần, 20 phụ kiện thật từ catalog local đã kiểm tra."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            default=str(
                settings.BASE_DIR / "database/seed/local_products_to_sync.json"
            ),
        )

    def handle(self, *args, **options):
        refuse_demo_seed_in_production()
        try:
            products = json.loads(Path(options["file"]).read_text(encoding="utf-8"))
            if Counter(item["category_slug"] for item in products) != {
                "ao": 30,
                "quan": 40,
                "phu-kien": 20,
            }:
                raise ValueError("Catalog phải có đúng 30 áo, 40 quần, 20 phụ kiện.")
            if (
                len({item["sku"] for item in products}) != 90
                or len({item["name"] for item in products}) != 90
            ):
                raise ValueError("Catalog có tên hoặc mã sản phẩm trùng.")
            media = Path(settings.MEDIA_ROOT).resolve()
            for item in products:
                attributes = item["attributes"]
                source_id = attributes["source_id"]
                if (
                    not str(source_id).isdigit()
                    or item["sku"] != f"MYNTRA-{source_id}"
                    or item["slug"] != f"myntra-{source_id}"
                    or item["name"] != attributes["source_name"]
                ):
                    raise ValueError("Tên hoặc mã sản phẩm không khớp nguồn.")
                minimum = 2 if item["category_slug"] == "phu-kien" else 4
                if not minimum <= len(item["images"]) <= 6:
                    raise ValueError("Sản phẩm thiếu ảnh gốc.")
                for image in item["images"]:
                    relative = Path(image["file"])
                    path = (media / relative).resolve()
                    if relative.is_absolute() or not path.is_relative_to(
                        media / "products/sourced/myntra" / str(source_id)
                    ):
                        raise ValueError("Đường dẫn ảnh không khớp mã sản phẩm.")
                    if hashlib.sha256(path.read_bytes()).hexdigest() != image["sha256"]:
                        raise ValueError("Ảnh bị thay đổi so với bản đã kiểm tra.")
                    with path.open("rb") as stream:
                        validate_product_image(File(stream, name=path.name))
        except (OSError, ValueError, KeyError, TypeError, ValidationError) as error:
            raise CommandError(f"Catalog không hợp lệ: {error}") from error

        with transaction.atomic():
            for index, item in enumerate(products):
                category, _ = Category.objects.get_or_create(
                    slug=item["category_slug"], defaults={"name": item["category_name"]}
                )
                brand, _ = Brand.objects.get_or_create(
                    name=item["brand"], defaults={"slug": slugify(item["brand"])}
                )
                product, _ = Product.objects.get_or_create(
                    sku=item["sku"],
                    defaults={
                        "category": category,
                        "name": item["name"],
                        "slug": item["slug"],
                        "price": item["price"],
                        "stock": 0,
                    },
                )
                product.category = category
                product.brand = brand
                product.name = item["name"]
                product.slug = item["slug"]
                product.image = item["images"][0]["file"]
                product.image_url = ""
                product.description = descriptor_text(item["descriptors"])
                product.spec_bullets = item["spec_bullets"]
                product.attributes = {**product.attributes, **item["attributes"]}
                product.available = True
                product.featured = index in {
                    0,
                    8,
                    16,
                    26,
                    30,
                    42,
                    54,
                    62,
                    70,
                    74,
                    81,
                    87,
                }
                product.save()
                product.gallery_images.all().delete()
                ProductImage.objects.bulk_create(
                    [
                        ProductImage(
                            product=product, image=image["file"], sort_order=position
                        )
                        for position, image in enumerate(item["images"][1:], start=1)
                    ]
                )
            Product.objects.exclude(sku__in=[item["sku"] for item in products]).update(
                available=False, featured=False
            )
        self.stdout.write(
            self.style.SUCCESS(
                f"Đã nhập 90 sản phẩm: 30 áo, 40 quần, 20 phụ kiện; {sum(len(p['images']) for p in products)} ảnh gốc. Không tạo tồn kho giả."
            )
        )
