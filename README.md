# HUUGIAU Atelier

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB)](https://www.python.org/)
[![Windows](https://img.shields.io/badge/Windows-11%2B-0078D4)](https://www.microsoft.com/windows)
[![Django](https://img.shields.io/badge/Django-5.2-092E20)](https://www.djangoproject.com/)
[![SQL Server](https://img.shields.io/badge/Database-SQL%20Server-CC2927)](https://www.microsoft.com/sql-server)
[![PostgreSQL](https://img.shields.io/badge/CI-PostgreSQL-4169E1)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-Cache%20%26%20Tasks-DC382D)](https://redis.io/)
[![Playwright](https://img.shields.io/badge/Playwright-E2E-2EAD33)](https://playwright.dev/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

**HUUGIAU Atelier** là website bán thời trang: khách xem sản phẩm → chọn biến thể → đặt hàng → theo dõi đơn. Ứng dụng không tự tạo catalog thật, không seed dữ liệu production và không tự đối soát thanh toán. Hỗ trợ SQL Server trên Windows hoặc PostgreSQL + Redis trong Docker Compose.

---

## Trạng thái hiện tại (09/2026)

| Thành phần | Trạng thái |
|---|---|
| **Catalog & admin** | ✅ Sẵn sàng — sản phẩm, biến thể, tồn kho, coupon, đánh giá, báo cáo |
| **Tài khoản & đơn hàng** | ✅ Sẵn sàng — đăng nhập username/email/SĐT, hồ sơ, wishlist, điểm, hạng |
| **Checkout & thanh toán** | ✅ COD; chuyển khoản/VietQR nhân viên đối soát; ⚠️ VNPay còn sandbox nếu chưa có merchant thật |
| **Database** | ✅ SQL Server cho triển khai Windows; PostgreSQL + Redis trong CI và Docker Compose |
| **Dữ liệu sản phẩm** | ⚠️ Database demo đã dọn sạch, hiện **0 sản phẩm**; catalog thật nhập qua admin hoặc `local_products_to_sync.json` |
| **Email** | ⚠️ Có đường gửi qua SMTP khi cấu hình, chưa test với tài khoản vận hành thật |
| **Test Django** | ✅ **515 tests** trong suite; CI chạy PostgreSQL, đã verify trên SQL Server local (30/09/2026) |
| **Test Playwright** | ✅ 6 browser spec, Chromium desktop + mobile, chạy trên PostgreSQL |
| **Backup/restore** | ✅ Đã verify trên SQL Server local |
| **Production** | ⚠️ Chưa mở bán: thiếu catalog thật, domain + HTTPS, VNPay merchant và test email thật |

> **Lưu ý**: `check --deploy` với `.env.production` còn 4 cảnh báo, tất cả do chưa có domain + HTTPS (HSTS, redirect, secure cookies).

---

## Tính năng chính

| Nhóm | Mô tả |
|---|---|
| **Cửa hàng** | Trang chủ, danh mục, tìm kiếm không dấu, bộ lọc, sắp xếp, phân trang |
| **Sản phẩm** | Chi tiết, gallery ảnh, màu/kích cỡ, bảng size, tồn kho, đánh giá, sản phẩm liên quan |
| **Giỏ hàng & checkout** | Giỏ theo session, coupon, phí giao hàng, kiểm tra tồn kho, chống tạo đơn trùng |
| **Thanh toán** | COD, chuyển khoản/VietQR cần đối soát thủ công, VNPay callback/IPN có kiểm chữ ký |
| **Tài khoản** | Đăng nhập username/email/SĐT, hồ sơ, địa chỉ, đơn hàng, wishlist, điểm và hạng |
| **Quản trị** | Sản phẩm, biến thể, tồn kho, đơn, coupon, người dùng, báo cáo |
| **Vận hành** | Email đơn hàng, giới hạn đăng nhập, rate limit, health check, backup/restore |
| **Giao diện** | Responsive, so sánh sản phẩm, timeline đơn hàng, support chat, nhắc giỏ qua email |

---

## Bắt đầu nhanh

### Yêu cầu hệ thống

- Windows 11 + SQL Server + ODBC Driver 17 cho cấu hình mặc định
- Python 3.10+ (khuyến nghị 3.12)
- Redis cho production; local dùng redis portable (`C:/redis-portable/redis.conf`, đấu qua `REDIS_URL`)
- Node.js 20+ chỉ cần khi chạy Playwright

### Cài đặt

```powershell
git clone <repo-url> Fashion-Website
cd Fashion-Website
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Đặt `SECRET_KEY` riêng và cấu hình kết nối SQL Server trong `.env` ở thư mục gốc. `backend/.env.example` chỉ là mẫu.

### Database

SQL Server cho triển khai Windows, PostgreSQL cho CI và Docker Compose. Migration và tài khoản admin:

```powershell
cd backend
python manage.py migrate
python manage.py createsuperuser
```

Dữ liệu demo chỉ chạy trên database riêng khi `DEBUG=True`:

```powershell
python manage.py seed_all          # tài khoản, đơn hàng và sản phẩm giả
python manage.py seed_products --sync
```

`seed_products --sync` đọc `database/seed/products_to_sync.json`, chỉ thêm/cập nhật sản phẩm có trong file, không xóa sản phẩm khác.

> **Lưu ý**: `backend/seed_large_demo.py` **xóa dữ liệu** — chỉ chạy với `DEBUG=True` cùng `ALLOW_DESTRUCTIVE_DEMO_RESET=YES`. Hai script SQL trong `database/sql` có cờ xác nhận reset/seed mặc định tắt. Không dùng tài khoản seed trên production.

### Chạy website local

```powershell
.\scripts\start.ps1
# Hoặc
chay-web.bat
```

Server phát triển chạy tại **http://localhost:8000/**. Không dùng `runserver` làm web server production.

### Triển khai production

```powershell
Copy-Item .env.production.example .env.production
# điền database, Redis, email, media, domain
.\scripts\verify_prod.py
.\scripts\start-windows-web.ps1
.\scripts\start-windows-caddy.ps1
```

Production cần thêm SQL Server/ODBC, Redis, reverse proxy HTTPS, DNS, thư mục media bền vững và lịch backup/restore.

---

## Bản đồ entrypoint

| Entrypoint | Vai trò |
|---|---|
| `chay-web.bat` | Mở website local qua PowerShell |
| `scripts/start.ps1` | Chạy Django runserver local, không tự migrate hoặc seed |
| `scripts/dev_server.py` | Dev server HTTPS local, dùng cert trong `backend/certs/` |
| `scripts/start-windows-web.ps1` | Kiểm tra deploy, nén/thu thập static và chạy Waitress |
| `scripts/start-windows-caddy.ps1` | Chạy Caddy reverse proxy và HTTPS trên Windows |
| `scripts/start-staging-web.ps1` | Staging local mô phỏng prod: waitress 8002 + Caddy TLS ở `https://127.0.0.1:8443/` |
| `scripts/verify_prod.py` | Kiểm tra một số điều kiện cấu hình trước go-live |
| `backend/manage.py` | Lệnh Django: migrate, test, tạo admin và tác vụ quản trị |
| `scripts/backup-db.ps1` | Backup SQL Server |
| `scripts/restore-db.ps1` | Khôi phục SQL Server sau khi xác nhận |
| `scripts/local_smoke_test.ps1` | Migrate, bật server tạm ở cổng 8010 và kiểm tra HTTP 200 |

### Luồng dữ liệu cơ bản

```text
Catalog:   products/views.py → sản phẩm + biến thể/tồn kho → template cửa hàng
Giỏ:       orders/views/cart.py → session + coupon → tổng tiền, phí giao hàng
Checkout:  orders/services/checkout.py → check tồn kho → Order + OrderItem
Thanh toán: orders/views/payment.py → COD / chuyển khoản / VNPay callback-IPN
Email:     orders/services/order_email.py → SMTP đã cấu hình
Admin:     Django admin + core/api.py → catalog, đơn hàng, báo cáo
```

---

## Store Pipeline (HUUGIAU)

| Bước | Module | Mô tả |
|---|---|---|
| Catalog | `products/views.py` | Danh mục, tìm kiếm không dấu, bộ lọc, phân trang |
| Biến thể | `products/models.py` | Màu, kích cỡ, tồn kho theo variant; bảng size tùy chọn theo thương hiệu |
| Giỏ hàng | `orders/views/cart.py` | Giỏ theo session, coupon, phí giao hàng |
| Checkout | `orders/services/checkout.py` | Check tồn kho, tạo `Order` + `OrderItem` trong transaction |
| Thanh toán | `orders/views/payment.py` | COD, chuyển khoản/VietQR, VNPay callback + IPN |
| Email | `orders/services/order_email.py` | Gửi email đơn hàng qua SMTP |
| Quản trị | `django.contrib.admin`, `core/api.py` | Catalog, tồn kho, đơn, coupon, người dùng, báo cáo |

---

## Kiểm thử

```powershell
# Django test — SQLite in-memory, không chạm SQL Server
$env:DJANGO_SETTINGS_MODULE = "core.test_settings_sqlite"
$env:SQLITE_TEST_DB = ":memory:"
$env:EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
$env:REDIS_URL = ""
cd backend
python manage.py test
```

```powershell
# Playwright E2E trên database SQLite tạm, không đụng catalog thật
$env:DJANGO_SETTINGS_MODULE = "core.test_settings_sqlite"
$env:SQLITE_TEST_DB = (Join-Path (Get-Location) ".tmp-e2e.sqlite3")
$env:REDIS_URL = ""
$env:EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
$env:BASE_URL = "http://127.0.0.1:8000"
python backend/manage.py migrate --noinput
python backend/manage.py seed_all --no-input
python scripts/prepare_e2e.py
cd frontend
npm ci
npm test -- --project=chromium --project="Mobile Chrome"
```

CI chạy Ruff, mypy, Bandit, pip-audit, frontend lint và kiểm tra build trên PostgreSQL. Kết quả phụ thuộc môi trường và thay đổi theo code.

---

## Cấu trúc thư mục

```text
Fashion-Website/
├── backend/
│   ├── core/                 # Settings, API, middleware, health check
│   ├── orders/               # Cart, checkout, payment, order, email
│   ├── products/             # Catalog, variants, reviews, search
│   └── users/                # Authentication, profile, permissions
├── frontend/
│   ├── templates/            # Django templates
│   ├── static/               # CSS, JavaScript, icons, images
│   └── tests/                # Playwright browser tests
├── database/
│   ├── seed/                 # Catalog JSON demo
│   └── sql/                  # SQL schema/seed demo có xác nhận
├── scripts/                  # Local run, deploy, backup/restore
├── docs/                     # Database, deployment, auth, runbooks
├── docker-compose.yml        # Local/demo stack PostgreSQL + Redis
└── docker-compose.production.yml
```

---

## Tài liệu tham khảo

| File | Nội dung |
|---|---|
| [docs/deploy-production.md](docs/deploy-production.md) | VPS Windows/SQL Server hoặc Docker Compose |
| [docs/database-setup.md](docs/database-setup.md) | Cài SQL Server, migration và dữ liệu legacy |
| [docs/web_auth.md](docs/web_auth.md) | Đăng nhập, vai trò và tạo admin |
| [docs/product-images.md](docs/product-images.md) | Quản lý ảnh sản phẩm |
| [docs/https-cert.md](docs/https-cert.md) | HTTPS và chứng chỉ |
| [docs/runbooks/backup-restore.md](docs/runbooks/backup-restore.md) | Sao lưu và khôi phục |
| [docs/ci_and_quality.md](docs/ci_and_quality.md) | CI và kiểm tra chất lượng |
| [docs/troubleshooting.md](docs/troubleshooting.md) | Xử lý lỗi thường gặp |
