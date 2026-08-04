import json
import random
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.test import Client
from django.utils.text import slugify

from products.constants import APPAREL_CATEGORY_SLUGS, FEATURED_PRODUCT_LIMIT
from products.models import Category, Product, ProductVariant

DEFAULT_CATEGORY_NAME = "Áo"
PANTS_CATEGORY_NAME = "Quần"
ACCESSORY_CATEGORY_NAME = "Phụ Kiện"
CATEGORY_DISPLAY_ORDER = (DEFAULT_CATEGORY_NAME, PANTS_CATEGORY_NAME, ACCESSORY_CATEGORY_NAME)
CATEGORY_ALIASES = {
    "Quầ": PANTS_CATEGORY_NAME,
    "Quầnn": PANTS_CATEGORY_NAME,
    "Quần": PANTS_CATEGORY_NAME,
    "Phụ kiện SWE": ACCESSORY_CATEGORY_NAME,
    "Phụ kiện": ACCESSORY_CATEGORY_NAME,
    "Phụ Kiện": ACCESSORY_CATEGORY_NAME,
    "Áo": DEFAULT_CATEGORY_NAME,
    "Ao": DEFAULT_CATEGORY_NAME,
}
DEFAULT_VARIANT_COLORS = [("Đen", "#111111"), ("Trắng", "#F5F5F5")]
APPAREL_SIZES = ["M", "L", "XL"]
ACCESSORY_SIZES = ["FREE"]
FEATURED_PER_CATEGORY = FEATURED_PRODUCT_LIMIT // len(CATEGORY_DISPLAY_ORDER)
DEFAULT_VARIANT_STOCK = 50
LOADTEST_REQUESTS_PER_USER = 10


class Command(BaseCommand):
    help = (
        "Công cụ quản lý dữ liệu sản phẩm: sync, export, random HOT, "
        "inspect DB, load test."
    )

    def add_arguments(self, parser):
        parser.add_argument("--sync", action="store_true", help="Đồng bộ từ JSON vào database.")
        parser.add_argument("--export", action="store_true", help="Xuất database ra file JSON.")
        parser.add_argument("--random-hot", action="store_true", help="Ngẫu nhiên 12 sản phẩm HOT trong file JSON.")
        parser.add_argument(
            "--shuffle-hot",
            type=int,
            nargs="?",
            const=12,
            help="Reset và chọn ngẫu nhiên N sản phẩm HOT trực tiếp trong DB.",
        )
        parser.add_argument("--inspect", action="store_true", help="Xem bảng dữ liệu.")
        parser.add_argument("--loadtest", action="store_true", help="Chạy kiểm thử tải.")
        parser.add_argument("--path", type=str, default="/", help="Route cần test, ví dụ: /")
        parser.add_argument("--users", type=int, default=50, help="Số user đồng thời cho load test")

    def handle(self, *args, **options):
        json_path = Path(settings.BASE_DIR) / "database" / "seed" / "products_to_sync.json"
        db_path = Path(settings.DATABASES["default"]["NAME"])

        if options["sync"]:
            self._sync_from_json(json_path)
        elif options["export"]:
            self._export_to_json(json_path)
        elif options["random_hot"]:
            self._randomize_hot_json(json_path)
        elif options["shuffle_hot"] is not None:
            self._shuffle_hot_db(options["shuffle_hot"])
        elif options["inspect"]:
            self._inspect_db(str(db_path))
        elif options["loadtest"]:
            self._run_loadtest(options["path"], options["users"])
        else:
            self.stdout.write(self.style.WARNING("Vui lòng chọn tham số. Gõ --help để xem chi tiết."))

    def _normalize_category_name(self, category_name):
        cat_name = (category_name or DEFAULT_CATEGORY_NAME).strip()
        return CATEGORY_ALIASES.get(cat_name, cat_name)

    def _sync_from_json(self, json_path):
        if not json_path.exists():
            self.stdout.write(self.style.ERROR(f"Không thấy file: {json_path}"))
            return

        data = json.loads(json_path.read_text(encoding="utf-8"))

        db_slugs = {product.slug: product for product in Product.objects.all()}
        json_slugs = {item.get("slug") or slugify(item["name"]) for item in data}

        to_delete = set(db_slugs.keys()) - json_slugs
        if to_delete:
            Product.objects.filter(slug__in=to_delete).delete()

        for item in data:
            name = item["name"].strip()
            slug = item.get("slug") or slugify(name)
            cat_name = self._normalize_category_name(item.get("category_name", DEFAULT_CATEGORY_NAME))

            category, _ = Category.objects.get_or_create(
                slug=slugify(cat_name),
                defaults={"name": cat_name},
            )
            if category.name != cat_name:
                category.name = cat_name
                category.save(update_fields=["name"])

            product, _ = Product.objects.update_or_create(
                slug=slug,
                defaults={
                    "category": category,
                    "name": name,
                    "price": item.get("price", 0),
                    "featured": bool(item.get("featured")),
                    "image_url": item.get("image_url", ""),
                    "available": True,
                },
            )
            self._seed_variants_minimal(product)

        self.stdout.write(self.style.SUCCESS(f"Đã đồng bộ {len(data)} sản phẩm."))

    def _export_to_json(self, json_path):
        products = Product.objects.all().select_related("category")
        data = [
            {
                "id": product.id,
                "name": product.name,
                "slug": product.slug,
                "price": float(product.price),
                "featured": 1 if product.featured else 0,
                "category_name": product.category.name,
            }
            for product in products
        ]
        json_path.write_text(json.dumps(data, ensure_ascii=False, indent=4), encoding="utf-8")
        self.stdout.write(self.style.SUCCESS(f"Đã xuất {len(data)} sản phẩm."))

    def _randomize_hot_json(self, json_path):
        if not json_path.exists():
            return

        data = json.loads(json_path.read_text(encoding="utf-8"))

        for item in data:
            item["featured"] = 0

        grouped = {}
        for item in data:
            cat_name = self._normalize_category_name(item.get("category_name", DEFAULT_CATEGORY_NAME))
            item["category_name"] = cat_name
            grouped.setdefault(cat_name, []).append(item)

        hot_items = []
        for cat_name in CATEGORY_DISPLAY_ORDER:
            if cat_name in grouped:
                items = grouped[cat_name]
                random.shuffle(items)
                hot_items.extend(items[:FEATURED_PER_CATEGORY])

        for item in hot_items:
            item["featured"] = 1

        json_path.write_text(json.dumps(data, ensure_ascii=False, indent=4), encoding="utf-8")
        self.stdout.write(self.style.SUCCESS("Đã ngẫu nhiên 12 sản phẩm HOT trong JSON. Hãy chạy --sync để áp dụng."))

    def _shuffle_hot_db(self, count):
        Product.objects.update(featured=False)
        ids = list(Product.objects.filter(available=True).order_by("?").values_list("id", flat=True)[:count])
        if ids:
            Product.objects.filter(id__in=ids).update(featured=True)
        self.stdout.write(self.style.SUCCESS(f"Đã chọn ngẫu nhiên {len(ids)} sản phẩm HOT trực tiếp trong DB."))

    def _inspect_db(self, db_path):
        from django.db import connection as db_conn
        tables = db_conn.introspection.table_names()
        for index, table_name in enumerate(tables, 1):
            self.stdout.write(f"{index}. {table_name}")

    def _run_loadtest(self, path, users):
        self.stdout.write(self.style.NOTICE(f"Đang load test: path={path}, users={users}"))

        def worker():
            client = Client()
            latencies = []
            for _ in range(LOADTEST_REQUESTS_PER_USER):
                start = time.perf_counter()
                client.get(path)
                latencies.append((time.perf_counter() - start) * 1000)
            return latencies

        with ThreadPoolExecutor(max_workers=users) as executor:
            results = list(executor.map(lambda _: worker(), range(users)))

        all_latencies = [item for sublist in results for item in sublist]
        avg = statistics.mean(all_latencies)
        p95 = statistics.quantiles(all_latencies, n=100)[94]
        self.stdout.write(self.style.SUCCESS(f"Kết quả: Avg={avg:.1f}ms, P95={p95:.1f}ms"))

    def _seed_variants_minimal(self, product):
        if product.variants.exists():
            return

        sizes = APPAREL_SIZES if product.category.slug in APPAREL_CATEGORY_SLUGS else ACCESSORY_SIZES
        for color_name, color_code in DEFAULT_VARIANT_COLORS:
            for size in sizes:
                ProductVariant.objects.get_or_create(
                    product=product,
                    color_name=color_name,
                    color_code=color_code,
                    size=size,
                    defaults={"stock": DEFAULT_VARIANT_STOCK, "is_active": True},
                )

        product.stock = DEFAULT_VARIANT_STOCK * len(DEFAULT_VARIANT_COLORS) * len(sizes)
        product.save(update_fields=["stock"])
