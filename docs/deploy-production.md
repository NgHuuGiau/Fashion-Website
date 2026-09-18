# Deploy production

Hướng dẫn đưa website thời trang lên môi trường thật. Stack hiện tại: Django 5.2 trên **Windows** với **SQL Server**. Có 2 đường triển khai khả thi.

## Lựa chọn 1 — VPS Windows + SQL Server (giữ stack hiện tại)

Đây là lộ trình ít thay đổi nhất vì ứng dụng đã xác nhận kết nối SQL Server qua ODBC Driver 17 trên máy phát triển. Cần mua/thuê Windows VPS; chưa có domain hoặc máy chủ thì chưa thể bật HTTPS công khai.

1. Trên VPS cài Python 3.12 x64, ODBC Driver 17, SQL Server và Caddy. Chuẩn bị Redis production có xác thực, chỉ truy cập được qua mạng riêng (hoặc localhost nếu cùng máy); không mở Redis/SQL Server ra Internet. Tạo thư mục ứng dụng cố định, ví dụ `C:\FashionWebsite`; không đặt upload trong thư mục source.
2. Copy/clone source, tạo môi trường Python và cài Waitress:

```powershell
cd C:\FashionWebsite\backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install waitress
```

3. Tạo `C:\FashionWebsite\.env.production` từ `.env.production.example` (file thật đã được Git bỏ qua). Đặt `DEBUG=False`, domain thật, `REDIS_URL`, SMTP nếu cần email, và `MEDIA_ROOT` thành thư mục riêng, ví dụ `D:/FashionMedia`.
4. Với Windows Authentication, chạy ứng dụng bằng một tài khoản Windows riêng được cấp quyền tối thiểu trên database; dùng `DB_TRUSTED_CONNECTION=True` và không đặt `DB_USER`/`DB_PASSWORD`. Nếu dùng SQL Login thì đặt `DB_TRUSTED_CONNECTION=False` và lưu thông tin trong `.env.production`, không gửi qua chat. Không mở SQL Server cổng 1433 ra Internet.
5. Tạo staging riêng và backup database trước khi thử migration. Chỉ sau khi migration, đăng nhập, đặt/hủy đơn và restore test đạt trên staging mới tạo database production riêng. Không chạy seed demo hoặc migration lên database demo để làm bước triển khai này.
6. Sau khi cấu hình DNS trỏ domain về VPS và mở firewall **chỉ cổng 80/443**, chạy web bằng Waitress ở loopback:

```powershell
cd C:\FashionWebsite
.\scripts\start-windows-web.ps1
```

Script kiểm tra cấu hình deploy, nén/thu thập static rồi bind Waitress tại `127.0.0.1:8000`; không tự chạy migration.
7. Chạy Caddy ở cửa sổ PowerShell khác. Dùng đúng cùng đường dẫn `MEDIA_ROOT` đã đặt trong `.env.production`:

```powershell
cd C:\FashionWebsite
.\scripts\start-windows-caddy.ps1 `
  -Domain "shop.example.com" `
  -AcmeEmail "admin@example.com" `
  -MediaRoot "D:\FashionMedia"
```

`Caddyfile.windows` tự phục vụ `/static/`, `/media/`, reverse proxy request còn lại tới Waitress và xin/gia hạn HTTPS. Không công khai cổng 8000.
8. Trước khi mở bán, tạo hai tác vụ Windows Task Scheduler, trigger “At startup”, chọn “Run whether user is logged on or not”, và đặt “If the task is already running” thành “Do not start a new instance”. Dùng tài khoản Windows có quyền database cho web task.

   - Web task: Program `powershell.exe`; arguments `-NoProfile -ExecutionPolicy Bypass -File "C:\FashionWebsite\scripts\start-windows-web.ps1"`.
   - Caddy task: Program `powershell.exe`; arguments `-NoProfile -ExecutionPolicy Bypass -File "C:\FashionWebsite\scripts\start-windows-caddy.ps1" -Domain "shop.yourdomain.com" -AcmeEmail "admin@yourdomain.com" -MediaRoot "D:\FashionMedia"`.

   Thay domain/email/path mẫu bằng giá trị thật; `MEDIA_ROOT` trong `.env.production` phải trùng với `-MediaRoot`.
9. Đặt lịch `scripts/backup-db.ps1` bằng Task Scheduler, lưu backup ngoài VPS và diễn tập restore vào database staging. File `.bak` cần được SQL Server service account ghi/đọc.

Muốn phát hành bản cập nhật: backup → cập nhật source → thử migration trên staging → chạy migration production có kiểm soát → khởi động lại web. Không dùng `runserver` làm app server production.

## Lựa chọn 2 — Docker Compose + PostgreSQL

Compose đã có PostgreSQL, PgBouncer, Redis có xác thực, app, Celery worker/beat, Nginx và cấu hình Caddy TLS tùy chọn. Chuyển dữ liệu từ SQL Server sang PostgreSQL là một dự án migration riêng: map schema, kiểm tra dữ liệu và thử restore trước; không đổi `DB_ENGINE` trên dữ liệu production đang chạy.

Sau khi domain trỏ tới server, chuẩn bị `.env.production` cho Django và copy `.env.compose.production.example` thành `.env.compose.production` để cấu hình DNS/database secrets cho Compose. Thực hiện quy trình release dưới đây từ repository root; chỉ mở traffic sau khi các bước kiểm tra thành công.

Container app chỉ khởi động web; không tự chạy migration hoặc xóa/tạo lại static files mỗi lần restart. Với Compose, dùng quy trình release một lần dưới đây sau khi build image. Trước khi migrate, phải diễn tập migration trên staging riêng và xác minh backup; tuyệt đối không trỏ các lệnh này vào database demo:

```bash
docker compose --env-file .env.compose.production -f docker-compose.yml -f docker-compose.production.yml build app
docker compose --env-file .env.compose.production -f docker-compose.yml -f docker-compose.production.yml run --rm app python manage.py check --deploy
docker compose --env-file .env.compose.production -f docker-compose.yml -f docker-compose.production.yml run --rm app python manage.py migrate --noinput
docker compose --env-file .env.compose.production -f docker-compose.yml -f docker-compose.production.yml run --rm app python manage.py compress --force
docker compose --env-file .env.compose.production -f docker-compose.yml -f docker-compose.production.yml run --rm app python manage.py collectstatic --noinput --clear
docker compose --env-file .env.compose.production -f docker-compose.yml -f docker-compose.production.yml up -d --no-build
```

Production settings sẽ dừng khởi động nếu `SECRET_KEY` còn yếu/placeholder hoặc `ALLOWED_HOSTS` rỗng/dùng `*`. Có thể tạo secret riêng bằng `python -c "import secrets; print(secrets.token_urlsafe(64))"`; không dùng lại key CI hay key local.

Caddy tự xin/gia hạn TLS. Trước khi bật cấu hình này, phải đặt `DOMAIN`, `ACME_EMAIL`, `DB_PASSWORD`, `REDIS_PASSWORD`, `PGBOUNCER_ADMIN_PASSWORD`, cấu hình DNS và mở cổng 80/443. Không chạy Compose production trước khi domain trỏ đúng tới máy chủ.

## Cấu hình production (`.env`)

```env
SECRET_KEY=<một chuỗi ngẫu nhiên dài 50+ ký tự — GIỮ KÍN>
DEBUG=False
ALLOWED_HOSTS=huugiau.com,www.huugiau.com
CSRF_TRUSTED_ORIGINS=https://huugiau.com,https://www.huugiau.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000

# SQL Server production
DB_ENGINE=mssql
DB_HOST=your-sql-server-host
DB_NAME=HUUGIAU_Fashion
DB_DRIVER=ODBC Driver 17 for SQL Server
DB_TRUSTED_CONNECTION=False
DB_USER=huugiau_app
DB_PASSWORD=<mật khẩu riêng>
DB_EXTRA_PARAMS=Encrypt=yes;TrustServerCertificate=no

# Redis thật cho cache/session và tác vụ nền (bắt buộc theo cấu hình production hiện tại)
REDIS_URL=redis://127.0.0.1:6379/0

# Thư mục upload bền vững, nằm ngoài thư mục source/release.
MEDIA_ROOT=D:/FashionMedia

# Email thật
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=<App Password 16 ký tự>
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=HUUGIAU Studio <no-reply@yourdomain.com>

# Chuyển khoản thủ công — mặc định tắt; SHOP_ACCOUNT_NAME là tên chủ tài khoản.
BANK_TRANSFER_ENABLED=False
SHOP_BANK_CODE=ICB
SHOP_BANK_ACCOUNT=
SHOP_ACCOUNT_NAME=

# VNPay PRODUCTION (không dùng sandbox)
VNPAY_URL=https://pay.vnpayment.vn/paymentv2/vpcpay.html
VNPAY_REFUND_URL=<endpoint hoàn tiền do VNPay cấp>
VNPAY_TMN_CODE=<mã merchant thật>
VNPAY_HASH_SECRET=<khóa thật>

# Tùy chọn: GA4 + Zalo
GA4_MEASUREMENT_ID=G-XXXXXXXXXX
ZALO_OA_ID=<zalo oa id>
```

> `VNPAY_URL` cho production phải là `https://pay.vnpayment.vn/paymentv2/vpcpay.html` (cổng thanh toán VNPay thật, xác nhận lại khi đăng ký merchant). Sandbox dùng `https://sandbox.vnpayment.vn/paymentv2/vpcpay.html`.

> Không chạy `database/sql/01_CREATE_TABLES.sql`, `02_DEMO_DATA.sql`, `seed_all` hoặc `seed_products --sync` trên dữ liệu production. Hai file SQL và `products_to_sync.json` được giữ cho môi trường demo; lệnh đồng bộ demo có thể xóa sản phẩm không nằm trong file nguồn. Không import tài khoản, đơn hàng, đánh giá, lượt bán hay ảnh thay thế từ demo vào cửa hàng thật.

## Vận hành sau release

1. Với VPS Windows, script `scripts/start-windows-web.ps1` chạy `compress --force` và `collectstatic --noinput` trước khi mở traffic. Compose chạy các lệnh static ở bước release bên trên.
2. Tạo superuser riêng: `python manage.py createsuperuser`.
3. Cài role sync trigger: `python manage.py install_role_sync`.
4. SQL Server backup: dùng `scripts/backup-db.ps1` và đặt lịch Windows Task Scheduler sau khi thử restore vào database tạm. Với Compose/PostgreSQL, xem runbook backup-restore; repository chưa tự tạo lịch hay cảnh báo backup.
5. Tối ưu ảnh chỉ khi chủ shop bổ sung ảnh thật và đã kiểm tra bản sao lưu; không chạy công cụ tối ưu lên thư mục ảnh demo nếu muốn giữ nguyên.

## Checklist an toàn

- [ ] `DEBUG=False` và `ALLOWED_HOSTS` có giá trị cụ thể (không `*`).
- [ ] `SECRET_KEY` ngẫu nhiên + không commit.
- [ ] Redis chạy và `REDIS_URL` đúng (nếu nhiều worker, LocMemCache KHÔNG hợp lệ).
- [ ] HTTPS từ Let's Encrypt, không có cảnh báo "Not secure".
- [ ] VNPay dùng merchant thật, test 1 đơn chuyển khoản + 1 đơn VNPay từ đầu tới cuối.
- [ ] Email gửi thật (đặt đơn → nhận mail).
- [ ] Đã cấu hình lịch backup ngoài ứng dụng và thực hiện ít nhất một lần restore thử lên database tạm.
- [ ] Đã cấu hình worker và beat (`docker-compose.yml`); kiểm tra log từng service và tác vụ định kỳ trước khi bật tính năng tự động.
- [ ] Chỉ bật `SECURE_HSTS_INCLUDE_SUBDOMAINS`/`SECURE_HSTS_PRELOAD` sau khi mọi subdomain đều dùng HTTPS ổn định.
- [ ] Đã thay toàn bộ giá trị giữ chỗ bằng domain, credentials và thông tin vận hành đã xác minh.
- [ ] Phí ship, thời gian giao, địa chỉ, hotline/email và đổi trả khớp khả năng vận hành thật.
