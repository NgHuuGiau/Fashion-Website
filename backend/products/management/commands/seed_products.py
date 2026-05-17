import json
import os
import random
import sqlite3
import statistics
import time
from concurrent.futures import ThreadPoolExecutor

from django.conf import settings
from django.core.management.base import BaseCommand
from django.test import Client
from django.utils.text import slugify

from products.models import Category, Product, ProductVariant


class Command(BaseCommand):
    help = (
        "CĂ´ng cá»¥ quáº£n lĂ½ dá»¯ liá»‡u sáº£n pháº©m: sync, export, random HOT, "
        "inspect DB, SQL shell, run SQL, load test."
    )

    def add_arguments(self, parser):
        parser.add_argument("--sync", action="store_true", help="Äá»“ng bá»™ tá»« JSON vĂ o database.")
        parser.add_argument("--export", action="store_true", help="Xuáº¥t database ra file JSON.")
        parser.add_argument("--random-hot", action="store_true", help="Ngáº«u nhiĂªn 12 sáº£n pháº©m HOT trong file JSON.")
        parser.add_argument(
            "--shuffle-hot",
            type=int,
            nargs="?",
            const=12,
            help="Reset vĂ  chá»n ngáº«u nhiĂªn N sáº£n pháº©m HOT trá»±c tiáº¿p trong DB.",
        )
        parser.add_argument("--inspect", action="store_true", help="Xem báº£ng dá»¯ liá»‡u tÆ°Æ¡ng tĂ¡c.")
        parser.add_argument("--shell", action="store_true", help="MĂ´i trÆ°á»ng SQL shell tÆ°Æ¡ng tĂ¡c.")
        parser.add_argument("--run-sql", type=str, help="Cháº¡y file SQL trong thÆ° má»¥c database.")
        parser.add_argument("--loadtest", action="store_true", help="Cháº¡y kiá»ƒm thá»­ táº£i.")
        parser.add_argument("--path", type=str, default="/", help="Route cáº§n test, vĂ­ dá»¥: /")
        parser.add_argument("--users", type=int, default=50, help="Sá»‘ user Ä‘á»“ng thá»i cho load test")

    def handle(self, *args, **options):
        json_path = os.path.join(settings.BASE_DIR, "database", "products_to_sync.json")
        db_path = settings.DATABASES["default"]["NAME"]

        if options["sync"]:
            self._sync_from_json(json_path)
        elif options["export"]:
            self._export_to_json(json_path)
        elif options["random_hot"]:
            self._randomize_hot_json(json_path)
        elif options["shuffle_hot"] is not None:
            self._shuffle_hot_db(options["shuffle_hot"])
        elif options["inspect"]:
            self._inspect_db(db_path)
        elif options["shell"]:
            self._sql_shell(db_path)
        elif options["run_sql"]:
            self._run_sql(db_path, options["run_sql"])
        elif options["loadtest"]:
            self._run_loadtest(options["path"], options["users"])
        else:
            self.stdout.write(self.style.WARNING("Vui lĂ²ng chá»n tham sá»‘. GĂµ --help Ä‘á»ƒ xem chi tiáº¿t."))

    def _normalize_category_name(self, category_name):
        cat_name = (category_name or "Ăo").strip()
        if cat_name in {"Quáº§", "Quáº§nn", "Quáº§n"}:
            return "Quáº§n"
        if cat_name in {"Phá»¥ kiá»‡n SWE", "Phá»¥ kiá»‡n", "Phá»¥ Kiá»‡n"}:
            return "Phá»¥ Kiá»‡n"
        if cat_name in {"Ăo", "Ao"}:
            return "Ăo"
        return cat_name

    def _sync_from_json(self, json_path):
        if not os.path.exists(json_path):
            self.stdout.write(self.style.ERROR(f"KhĂ´ng tháº¥y file: {json_path}"))
            return

        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        db_slugs = {product.slug: product for product in Product.objects.all()}
        json_slugs = {item.get("slug") or slugify(item["name"]) for item in data}

        to_delete = set(db_slugs.keys()) - json_slugs
        if to_delete:
            Product.objects.filter(slug__in=to_delete).delete()

        for item in data:
            name = item["name"].strip()
            slug = item.get("slug") or slugify(name)
            cat_name = self._normalize_category_name(item.get("category_name", "Ăo"))

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

        self.stdout.write(self.style.SUCCESS(f"ÄĂ£ Ä‘á»“ng bá»™ {len(data)} sáº£n pháº©m."))

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
        with open(json_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        self.stdout.write(self.style.SUCCESS(f"ÄĂ£ xuáº¥t {len(data)} sáº£n pháº©m."))

    def _randomize_hot_json(self, json_path):
        if not os.path.exists(json_path):
            return

        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        for item in data:
            item["featured"] = 0

        grouped = {}
        for item in data:
            cat_name = self._normalize_category_name(item.get("category_name", "Ăo"))
            item["category_name"] = cat_name
            grouped.setdefault(cat_name, []).append(item)

        hot_items = []
        for cat_name in ["Ăo", "Quáº§n", "Phá»¥ Kiá»‡n"]:
            if cat_name in grouped:
                items = grouped[cat_name]
                random.shuffle(items)
                hot_items.extend(items[:4])

        for item in hot_items:
            item["featured"] = 1

        with open(json_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        self.stdout.write(self.style.SUCCESS("ÄĂ£ ngáº«u nhiĂªn 12 sáº£n pháº©m HOT trong JSON. HĂ£y cháº¡y --sync Ä‘á»ƒ Ă¡p dá»¥ng."))

    def _shuffle_hot_db(self, count):
        Product.objects.update(featured=False)
        ids = list(Product.objects.filter(available=True).order_by("?").values_list("id", flat=True)[:count])
        if ids:
            Product.objects.filter(id__in=ids).update(featured=True)
        self.stdout.write(self.style.SUCCESS(f"ÄĂ£ chá»n ngáº«u nhiĂªn {len(ids)} sáº£n pháº©m HOT trá»±c tiáº¿p trong DB."))

    def _inspect_db(self, db_path):
        with sqlite3.connect(db_path) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            tables = [row[0] for row in cursor.fetchall()]
            for index, table_name in enumerate(tables, 1):
                self.stdout.write(f"{index}. {table_name}")
            choice = input("\nNháº­p sá»‘ báº£ng (Enter Ä‘á»ƒ thoĂ¡t): ").strip()
            if choice.isdigit():
                cursor.execute(f"SELECT * FROM {tables[int(choice) - 1]} LIMIT 10")
                for row in cursor.fetchall():
                    self.stdout.write(str(row))

    def _sql_shell(self, db_path):
        self.stdout.write(self.style.SUCCESS(f"[*] SQL Shell: {os.path.basename(db_path)}"))
        with sqlite3.connect(db_path) as connection:
            cursor = connection.cursor()
            while True:
                query = input("\nsqlite> ").strip()
                if query.lower() in ("exit", "quit"):
                    break
                try:
                    cursor.execute(query)
                    if cursor.description:
                        for row in cursor.fetchall():
                            self.stdout.write(str(row))
                    else:
                        connection.commit()
                        self.stdout.write("ThĂ nh cĂ´ng.")
                except Exception as exc:
                    self.stdout.write(self.style.ERROR(str(exc)))

    def _run_sql(self, db_path, sql_file):
        sql_path = os.path.join(settings.BASE_DIR, "database", sql_file)
        if not os.path.exists(sql_path):
            return
        with sqlite3.connect(db_path) as connection:
            with open(sql_path, "r", encoding="utf-8") as file:
                connection.executescript(file.read())
        self.stdout.write(self.style.SUCCESS("[+] ThĂ nh cĂ´ng."))

    def _run_loadtest(self, path, users):
        self.stdout.write(self.style.NOTICE(f"Äang load test: path={path}, users={users}"))

        def worker():
            client = Client()
            latencies = []
            for _ in range(10):
                start = time.perf_counter()
                client.get(path)
                latencies.append((time.perf_counter() - start) * 1000)
            return latencies

        with ThreadPoolExecutor(max_workers=users) as executor:
            results = list(executor.map(lambda _: worker(), range(users)))

        all_latencies = [item for sublist in results for item in sublist]
        avg = statistics.mean(all_latencies)
        p95 = statistics.quantiles(all_latencies, n=100)[94]
        self.stdout.write(self.style.SUCCESS(f"Káº¿t quáº£: Avg={avg:.1f}ms, P95={p95:.1f}ms"))

    def _seed_variants_minimal(self, product):
        if product.variants.exists():
            return

        colors = [("Äen", "#111111"), ("Tráº¯ng", "#F5F5F5")]
        sizes = ["M", "L", "XL"] if product.category.slug in ("ao", "quan") else ["FREE"]
        for color_name, color_code in colors:
            for size in sizes:
                ProductVariant.objects.get_or_create(
                    product=product,
                    color_name=color_name,
                    color_code=color_code,
                    size=size,
                    defaults={"stock": 50, "is_active": True},
                )

        product.stock = 50 * len(colors) * len(sizes)
        product.save(update_fields=["stock"])
