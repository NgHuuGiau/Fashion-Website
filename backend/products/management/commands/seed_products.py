import json
import os
import random
import sqlite3
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.conf import settings
from django.test import Client
from products.models import Category, Product, ProductVariant

# -----------------------------
# | KHỐI LỚP (CLASS): COMMAND |
# -----------------------------
class Command(BaseCommand):
    help = "Siêu công cụ quản lý dự án: Sync, Export, Random HOT, Shuffle HOT, Inspect DB, SQL Shell, Run SQL, Load Test."

    # ------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): ARGUMENTS |
    # ------------------------------------
    def add_arguments(self, parser):
        # Nhóm quản lý sản phẩm (Product Management)
        parser.add_argument('--sync', action='store_true', help='Đồng bộ từ JSON vào Database.')
        parser.add_argument('--export', action='store_true', help='Xuất Database ra file JSON.')
        parser.add_argument('--random-hot', action='store_true', help='Ngẫu nhiên 12 sản phẩm HOT trong file JSON.')
        parser.add_argument('--shuffle-hot', type=int, nargs='?', const=12, help='Reset và chọn ngẫu nhiên N sản phẩm HOT trực tiếp trong DB.')

        # Nhóm công cụ Database (Database Tools)
        parser.add_argument('--inspect', action='store_true', help='Xem bảng dữ liệu tương tác.')
        parser.add_argument('--shell', action='store_true', help='Môi trường SQL Shell tương tác.')
        parser.add_argument('--run-sql', type=str, help='Chạy file SQL (VD: seed_data.sql).')

        # Nhóm kiểm thử (Developer Tools)
        parser.add_argument('--loadtest', action='store_true', help='Chạy kiểm thử tải (Load Test) hệ thống.')
        parser.add_argument('--path', type=str, default="/", help="Route cần test (VD: /)")
        parser.add_argument('--users', type=int, default=50, help="Số user đồng thời cho loadtest")

    # ---------------------------------
    # | HÀM XỬ LÝ (FUNCTION): HANDLE |
    # ---------------------------------
    def handle(self, *args, **options):
        json_path = os.path.join(settings.BASE_DIR, 'database', 'products_to_sync.json')
        db_path = settings.DATABASES['default']['NAME']

        if options['sync']:
            self._sync_from_json(json_path)
        elif options['export']:
            self._export_to_json(json_path)
        elif options['random_hot']:
            self._randomize_hot_json(json_path)
        elif options['shuffle_hot'] is not None:
            self._shuffle_hot_db(options['shuffle_hot'])
        elif options['inspect']:
            self._inspect_db(db_path)
        elif options['shell']:
            self._sql_shell(db_path)
        elif options['run_sql']:
            self._run_sql(db_path, options['run_sql'])
        elif options['loadtest']:
            self._run_loadtest(options['path'], options['users'])
        else:
            self.stdout.write(self.style.WARNING("Vui lòng chọn tham số. Gõ --help để xem chi tiết."))

    # --------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): _SYNC_LOGIC |
    # --------------------------------------
    def _sync_from_json(self, json_path):
        if not os.path.exists(json_path):
            self.stdout.write(self.style.ERROR(f"Không thấy file: {json_path}"))
            return
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        db_slugs = {p.slug: p for p in Product.objects.all()}
        json_slugs = {p.get('slug') or slugify(p['name']) for p in data}

        # Xóa sản phẩm thừa
        to_del = set(db_slugs.keys()) - json_slugs
        if to_del: Product.objects.filter(slug__in=to_del).delete()

        # Cập nhật sản phẩm
        for p in data:
            name, slug = p['name'], p.get('slug') or slugify(p['name'])
            cat_name = p.get('category_name', 'Áo')
            if cat_name == 'Quầ': cat_name = 'Quần'
            if cat_name == 'Phụ kiện SWE': cat_name = 'Phụ kiện'
            
            cat, _ = Category.objects.get_or_create(name=cat_name, defaults={'slug': slugify(cat_name)})
            prod, _ = Product.objects.update_or_create(
                slug=slug, defaults={
                    'category': cat, 'name': name, 'price': p.get('price', 0),
                    'featured': bool(p.get('featured')), 'image_url': p.get('image_url', ''), 'available': True
                }
            )
            self._seed_variants_minimal(prod)
        self.stdout.write(self.style.SUCCESS(f"Đã đồng bộ {len(data)} sản phẩm."))

    # ----------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): _EXPORT_LOGIC |
    # ----------------------------------------
    def _export_to_json(self, json_path):
        prods = Product.objects.all().select_related('category')
        data = [{'id': p.id, 'name': p.name, 'slug': p.slug, 'price': float(p.price),
                 'featured': 1 if p.featured else 0, 'category_name': p.category.name} for p in prods]
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        self.stdout.write(self.style.SUCCESS(f"Đã xuất {len(data)} sản phẩm."))

    # ------------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): _RANDOM_JSON |
    # ------------------------------------------
    def _randomize_hot_json(self, json_path):
        if not os.path.exists(json_path): return
        with open(json_path, 'r', encoding='utf-8') as f: data = json.load(f)
        for p in data: p['featured'] = 0
        cats = {}
        for p in data:
            c = p['category_name']
            if c not in cats: cats[c] = []
            cats[c].append(p)
        hot = []
        for c_name in ['Áo', 'Quần', 'Phụ kiện']:
            if c_name in cats:
                items = cats[c_name]
                random.shuffle(items)
                hot.extend(items[:4])
        for p in hot: p['featured'] = 1
        with open(json_path, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=4)
        self.stdout.write(self.style.SUCCESS("Đã ngẫu nhiên 12 HOT trong JSON. Hãy --sync để áp dụng."))

    # -----------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): _SHUFFLE_DB |
    # -----------------------------------------
    def _shuffle_hot_db(self, count):
        Product.objects.update(featured=False)
        ids = list(Product.objects.filter(available=True).order_by("?").values_list("id", flat=True)[:count])
        if ids: Product.objects.filter(id__in=ids).update(featured=True)
        self.stdout.write(self.style.SUCCESS(f"Đã chọn ngẫu nhiên {len(ids)} sản phẩm HOT trực tiếp trong DB."))

    # -----------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): _INSPECT_LOGIC |
    # -----------------------------------------
    def _inspect_db(self, db_path):
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            tables = [r[0] for r in cur.fetchall()]
            for i, t in enumerate(tables, 1): self.stdout.write(f"{i}. {t}")
            choice = input("\nNhập số bảng (Enter thoát): ").strip()
            if choice.isdigit():
                cur.execute(f"SELECT * FROM {tables[int(choice)-1]} LIMIT 10")
                for r in cur.fetchall(): self.stdout.write(str(r))

    # ---------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): _SHELL_LOGIC |
    # ---------------------------------------
    def _sql_shell(self, db_path):
        self.stdout.write(self.style.SUCCESS(f"[*] SQL Shell: {os.path.basename(db_path)}"))
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            while True:
                q = input("\nsqlite> ").strip()
                if q.lower() in ('exit', 'quit'): break
                try:
                    cur.execute(q)
                    if cur.description:
                        for r in cur.fetchall(): self.stdout.write(str(r))
                    else: conn.commit(); self.stdout.write("Thành công.")
                except Exception as e: self.stdout.write(self.style.ERROR(str(e)))

    # -----------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): _RUN_SQL_LOGIC |
    # -----------------------------------------
    def _run_sql(self, db_path, sql_file):
        sql_path = os.path.join(settings.BASE_DIR, 'database', sql_file)
        if not os.path.exists(sql_path): return
        with sqlite3.connect(db_path) as conn:
            with open(sql_path, 'r', encoding='utf-8') as f: conn.executescript(f.read())
        self.stdout.write(self.style.SUCCESS("[+] Thành công."))

    # -----------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): _LOADTEST_RUN |
    # -----------------------------------------
    def _run_loadtest(self, path, users):
        self.stdout.write(self.style.NOTICE(f"Đang Load Test: path={path}, users={users}"))
        def worker():
            c = Client(); latencies = []
            for _ in range(10):
                s = time.perf_counter(); c.get(path); latencies.append((time.perf_counter() - s)*1000)
            return latencies
        with ThreadPoolExecutor(max_workers=users) as ex:
            results = list(ex.map(lambda _: worker(), range(users)))
        all_l = [item for sub in results for item in sub]
        avg = statistics.mean(all_l); p95 = statistics.quantiles(all_l, n=100)[94]
        self.stdout.write(self.style.SUCCESS(f"Kết quả: Avg={avg:.1f}ms, P95={p95:.1f}ms"))

    # ---------------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): _VARIANTS_MINIMAL |
    # ---------------------------------------------
    def _seed_variants_minimal(self, product):
        if product.variants.exists(): return
        colors = [("Đen", "#111111"), ("Trắng", "#F5F5F5")]
        sizes = ["M", "L", "XL"] if product.category.slug in ('ao', 'quan') else ["FREE"]
        for c_name, c_code in colors:
            for s in sizes:
                ProductVariant.objects.get_or_create(product=product, color_name=c_name, color_code=c_code, size=s, defaults={'stock': 50, 'is_active': True})
        product.stock = 50 * len(colors) * len(sizes)
        product.save(update_fields=['stock'])
