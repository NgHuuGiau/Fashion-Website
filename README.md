# HUUGIAU Atelier — Website Thời Trang

![Python](https://img.shields.io/badge/Python_3.12%2B-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django_5.2-092E20?logo=django&logoColor=white)
![SQL Server](https://img.shields.io/badge/SQL_Server-CC2927?logo=microsoftsqlserver&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-ES5-F7DF1E?logo=javascript&logoColor=black)
![Redis](https://img.shields.io/badge/Redis-DC382D?logo=redis&logoColor=white)
![VNPay](https://img.shields.io/badge/VNPay-006837)
![Pillow](https://img.shields.io/badge/Pillow-3776AB?logo=python&logoColor=white)
![Font Awesome](https://img.shields.io/badge/Font_Awesome_6.5-528DD7?logo=fontawesome&logoColor=white)
![Windows](https://img.shields.io/badge/Windows_11%2B-0078D4?logo=windows&logoColor=white)
![CI](https://img.shields.io/github/actions/workflow/status/NgHuuGiau/Fashion-Website/ci.yml?logo=githubactions&logoColor=white&label=CI)
![Coverage](https://img.shields.io/badge/coverage-measured_in_CI-success)
![License](https://img.shields.io/badge/License-MIT-green)

**HUUGIAU Atelier** là website bán thời trang: nhận đơn → kiểm tra kho → tính giá khuyến mãi → thu tiền và trả trạng thái theo dõi đơn. Ứng dụng không tự nhận đã nhận tiền khi chưa có bằng chứng, không tạo đơn trùng khi khách bấm 2 lần.

---

## Trạng thái dự án (09/2026)

| Thành phần | Trạng thái |
|---|---|
| **Backend (Django 5.2)** | ✅ Có các luồng cửa hàng và bộ test (**486 Django + 35 Playwright pass**); xem kết quả CI mới nhất trước khi phát hành |
| **Database (SQL Server)** | ✅ Có backend SQL Server (`HUUGIAU_Fashion`, migrate tới `0022`); cần full test trên đúng SQL Server triển khai |
| **Frontend (HTML5/CSS3/JS)** | ✅ Giao diện responsive, lazy ảnh + lazy bản đồ; cần kiểm tra lại trên thiết bị và trình duyệt mục tiêu |
| **Thanh toán** | ✅ COD và VietQR VietinBank đã chạy live (QR đúng STK shop); ❌ VNPay cần merchant/callback thật. VietQR là chuyển khoản cần nhân viên đối soát, không có IPN ngân hàng |
| **Email** | ✅ Gmail SMTP đã gửi thật được (xác nhận đơn, báo tồn kho); kiểm tra nhận email trước khi mở bán |
| **Admin Dashboard** | ✅ Có dashboard, CRUD, bulk actions, export CSV, nhập kho CSV, thống kê giảm giá |
| **Vận hành local** | ✅ Waitress + Redis portable + Caddy (static + proxy); xem `scripts/start-windows-web.ps1` |
| **HTTPS** | ❌ Cấu hình HTTPS production tại reverse proxy; chứng chỉ local không thay cho domain/SSL public |
| **CI (GitHub Actions)** | Workflow chạy test trên PostgreSQL và Python 3.10–3.13; không xác nhận SQL Server production. Xem trạng thái run mới nhất trên GitHub |

> **Chưa xác nhận sẵn sàng mở bán:** cần hoàn tất kết nối/test SQL Server, cấu hình và thử thanh toán/email thật hoặc sandbox phù hợp, HTTPS public, backup khôi phục và giám sát. CI xanh không thay thế các bước này.

---

## Bắt đầu nhanh

### 1. Clone & cài đặt

```powershell
git clone <repo-url> Fashion-Website
cd Fashion-Website
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Cấu hình `.env`

Sao chép `.env.example` thành `.env` ở thư mục gốc dự án. Django chỉ nạp file ở vị trí này; không đặt `.env` trong `backend/`. Mẫu production nằm ở `.env.production.example`.

```ini
SECRET_KEY=your-secret-key
DEBUG=True
DB_ENGINE=mssql
DB_HOST=.
DB_NAME=HUUGIAU_Fashion
VNPAY_TMN_CODE=your_sandbox_tmn
VNPAY_HASH_SECRET=your_sandbox_secret
BANK_TRANSFER_ENABLED=False
SHOP_BANK_CODE=ICB
SHOP_BANK_ACCOUNT=
SHOP_ACCOUNT_NAME=
```

Chuyển khoản ngân hàng mặc định bị tắt. Khi dùng VietinBank, đặt `SHOP_BANK_CODE=ICB`; điền **số tài khoản** (không phải số thẻ) vào `SHOP_BANK_ACCOUNT` và tên chủ tài khoản đúng như ngân hàng vào `SHOP_ACCOUNT_NAME`. Chỉ đặt `BANK_TRANSFER_ENABLED=True` sau khi xác minh đủ thông tin. QR luôn trỏ về ngân hàng/tài khoản của shop; khách có thể quét bằng ứng dụng ngân hàng bất kỳ. Khách báo đã chuyển không được xem là bằng chứng thanh toán, nhân viên phải đối soát trước khi cập nhật đơn.

Production dùng `.env.production` với `DEBUG=False`, HTTPS, cookie secure và HSTS. Chỉ bật HSTS `includeSubDomains`/`preload` sau khi mọi subdomain đều dùng HTTPS ổn định.

> `CSRF_TRUSTED_ORIGINS` đã cấu hình sẵn trong `core/settings.py` (localhost:8000 HTTP/HTTPS).

### 3. Khởi tạo Database

```powershell
# Chỉ dùng trên database demo bỏ được; bật cờ xác nhận trong file trước khi chạy.
database/sql/01_CREATE_TABLES.sql
database/sql/02_DEMO_DATA.sql

# Hoặc dùng Python command (chỉ môi trường demo với DEBUG=True; tạo dữ liệu giả)
cd backend
python manage.py migrate
python manage.py seed_all --no-input
```

`products_to_sync.json` và `02_DEMO_DATA.sql` giữ cùng danh mục 76 sản phẩm mẫu; đây không phải hàng thật và không tự tạo ảnh thật. Không chạy script reset/seed trên production. Khi bán thật, tạo dữ liệu hàng, biến thể/tồn kho và tải ảnh thật riêng.

### Docker Compose (PostgreSQL local/demo)

```powershell
Copy-Item .env.docker.example .env.docker
# Mở .env.docker, thay SECRET_KEY, DB_PASSWORD, REDIS_PASSWORD và PGBOUNCER_ADMIN_PASSWORD
docker compose --env-file .env.docker up --build
```

Web local được bind tại `http://127.0.0.1:8001`. PostgreSQL/PgBouncer không công khai cổng host; Compose chạy cả Celery worker và beat. Không dùng secrets mẫu trên Internet.

### 4. Chạy server

**Cách 1 (Khuyên dùng) — Double-click:**
```cmd
chay-web.bat
```

**Cách 2 — PowerShell script (tự mở trình duyệt):**
```powershell
.\scripts\start.ps1
```

**Cách 3 — Dev server (HTTP only):**
```cmd
cd backend
python manage.py runserver 8000
```

Server local chạy tại: **http://localhost:8000/** (HTTP). HTTPS production được bật ở reverse proxy.

---

## Tài khoản mặc định

| Vai trò | Username | Password |
|---|---|---|
| **Admin (superuser)** | `admin` | `admin123` |
| **Staff** | `staff1` / `staff2` / `staff3` | `staff123` |
| **User (15 tài khoản)** | `user01` → `user15` | `user123` |

> Đây là tài khoản demo chỉ được tạo bởi lệnh seed ở môi trường `DEBUG=True`. Không dùng các mật khẩu này trên production; hãy tạo tài khoản quản trị riêng và đổi mật khẩu ngay.
> Sau 10 lần sai trong 5 phút → chặn 5 phút.

---

## Tính năng chính

| Module | Tính năng |
|---|---|
| **Trang chủ** | Hero editorial + sản phẩm nổi bật |
| **Danh mục** | Lọc category/size/color/price, sort, pagination (12/sp) |
| **Chi tiết SP** | Gallery 6 ảnh, variant (color+size), đã xem, size chart, wishlist |
| **Giỏ hàng** | Session-based, cập nhật SL, coupon, phí ship, chống đặt trùng khi bấm 2 lần |
| **Thanh toán** | COD; VietQR VietinBank live (QR đúng STK shop) chờ nhân viên đối soát; VNPay redirect + xác minh chữ ký callback/IPN khi đã cấu hình merchant |
| **Email** | Mẫu xác nhận, thanh toán, hủy, giao; chỉ gửi được khi SMTP và địa chỉ nhận hợp lệ |
| **Tra cứu đơn** | Mã đơn + SĐT, hủy đơn + hoàn stock |
| **Tìm kiếm** | Gợi ý debounce 250ms, không phân biệt dấu |
| **Đăng nhập** | Email / SĐT / username |
| **Support chat** | FAQ, size gợi ý |
| **Admin** | Dashboard doanh thu 7 ngày, CRUD SP/đơn/coupon, bulk actions, export CSV, nhập kho CSV, thống kê giảm giá, báo cáo tháng |
| **So sánh SP** | Toggle trên card/detail, bảng so sánh max 4 SP |
| **Timeline đơn** | 4 bước: Xác nhận → Đóng gói → Đang giao → Đã giao |
| **Nhắc giỏ** | Email tự động (`send_cart_reminders`) |

---

## Cấu trúc thư mục

```
Fashion-Website/
├── backend/                 # Django project
│   ├── core/                # Settings, middleware, Celery beat, health check
│   │   ├── api/             # API theo domain: common/products/orders/admin/misc
│   │   ├── logging/         # Correlation/request-id + JSON formatter
│   │   └── management/      # generate_schema, runserver tùy biến
│   ├── orders/              # Giỏ, checkout idempotent, coupon, thanh toán
│   │   ├── services/        # cart_email/checkout/order_email (logic thuần)
│   │   ├── views/           # cart/payment/order/admin (re-export tường minh)
│   │   └── management/      # seed_all, send_cart_reminders, import_legacy
│   ├── products/            # Catalog, variant, review, PriceHistory, chat
│   │   ├── services/        # chat_service (FAQ/size)
│   │   ├── templatetags/    # shop_format (vnd, json an toàn)
│   │   └── management/      # seed_products/blog/reviews, optimize_images
│   ├── users/               # Auth, profile, điểm/hạng, referral
│   │   └── management/      # install_role_sync, sync_roles
│   ├── certs/               # SSL certs (dev)
│   └── manage.py
├── frontend/                # Giao diện
│   ├── static/              # CSS, JS ES5, icons, images, webfonts, manifest, sw.js
│   └── templates/           # account/admin/auth/emails/pages/shop + 404/500/base
├── database/
│   ├── sql/                 # 01_CREATE_TABLES.sql, 02_DEMO_DATA.sql
│   └── seed/                # products_to_sync.json (76 SP demo)
├── config/pgbouncer/        # Cấu hình PgBouncer (docker)
├── scripts/                 # start-windows-web/caddy, verify_prod, backup/restore, dev_server
├── docs/                    # deploy/database/https/images/troubleshooting/ci/auth + runbooks/
├── Caddyfile*               # Reverse proxy + static (prod + windows)
├── docker-compose*.yml      # Prod (Caddy) / local (nginx + Postgres + Celery)
├── backups/                 # .bak SQL Server (gitignored)
├── .env / .env.production   # Cấu hình local/prod (gitignored)
└── requirements.txt
```

---

## Bản đồ entrypoint

| Entrypoint | Vai trò |
|---|---|
| `chay-web.bat` | Double-click chạy nhanh cho người vận hành |
| `scripts/start-windows-web.ps1` | Chạy prod local: check deploy + waitress |
| `scripts/verify_prod.py` | Quét blocker go-live, exit 1 khi còn chặn |
| `scripts/backup-db.bat` | Backup SQL Server giữ 7 ngày |
| `backend/manage.py` | Mọi lệnh Django (migrate, test, seed, shell) |

### Luồng đơn hàng

| Bước | Module | Mô tả |
|---|---|---|
| Pricing | `orders/services/checkout.py` | Ship theo vùng, coupon trần 50%, điểm + hạng |
| Idempotency | `orders/views/cart.py` | Key→đơn trong session, bấm 2 lần trả đơn cũ |
| Thu tiền | `orders/views/payment.py` | COD / VietQR chờ đối soát / VNPay IPN verify |
| Mail | `orders/services/order_email.py` | Tạo/paid/hủy/giao qua Gmail SMTP |
| Báo cáo | `orders/admin_product_dashboard.py` | Doanh thu, tồn kho, export CSV |

> Thiếu `VNPAY_TMN_CODE` thì VNPay tự ẩn ở checkout, web không giả vờ thanh toán online.

---

## Testing

```powershell
cd backend

# Chạy từng app (tránh deadlock DB)
python manage.py test users
python manage.py test products
python manage.py test orders
python manage.py test core

# Coverage
coverage run --source=core,orders,products,users manage.py test products
coverage report -m
coverage html  # mở htmlcov/index.html
```

| App | Phạm vi test |
|---|---|---|
| `orders` | Cart, checkout idempotent, coupon stacking, bank/VNPay, IPN, admin, import CSV, export |
| `products` | Catalog, detail, variant, search, review, wishlist, compare, size guide, price history |
| `users` | Auth, profile, role sync, activity |
| `core` | API envelope/pagination, CSP, rate limit, cache, SEO, invoice |

> Số test và coverage thay đổi theo code; lấy kết quả của lần chạy test/CI hiện tại làm chuẩn, không dựa vào số liệu ghi cứng trong README.

---

## CI/CD Pipeline

`.github/workflows/ci.yml`:
- **Lint**: Ruff (Python) + ESLint (JS)
- **Type Check**: Mypy (bắt buộc pass)
- **Security**: Bandit + pip-audit (bắt buộc pass)
- **Tests**: Django tests trên PostgreSQL (Python 3.10–3.13, Django 5.2)
- **Build**: Django check --deploy, collectstatic, compress
- **CodeQL**: Python + JavaScript analysis trong workflow riêng

Ma trận test hiện cấu hình Python 3.10–3.13. CI dùng PostgreSQL; dự án local/production dùng SQL Server nên vẫn cần chạy test tích hợp riêng trên SQL Server.

---

## Backup & Restore

```cmd
# Backup thủ công
.\backup-db.bat

# Tự động (Windows Task Scheduler, mỗi ngày 02:00)
# Lần đầu: icacls "backups" /grant "NT SERVICE\MSSQLSERVER:(OI)(CI)M"
```

File `.bak` lưu trong `backups/` (gitignored, OneDrive sync cloud).

Khôi phục database (sẽ hỏi xác nhận và ghi đè database hiện tại):

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\restore-db.ps1 -BackupFile .\backups\HUUGIAU_Fashion_<timestamp>.bak
```

---

## SSL Development

Server local dùng HTTP để chạy ổn định với `manage.py runserver`. HTTPS production
được bật tại reverse proxy bằng certificate thật; không dùng certificate dev để mở bán.

Xem chi tiết: [docs/https-cert.md](docs/https-cert.md)

---

## Phân quyền 2 chiều

| Thao tác | Đồng bộ |
|---|---|
| Đổi role trên Django Admin | → SQL Server `[Users].role` cập nhật |
| Đổi `[Users].role` trong SSMS | → Django `is_staff/is_superuser` cập nhật |

Cài đặt 1 lần: `python manage.py install_role_sync` (chi tiết `docs/database-setup.md`).

---

## Ghi chú quan trọng

- **Database chính**: SQL Server (`DB_ENGINE=mssql`)
- **Server dev**: HTTPS cert local (`backend/certs/`) — CA đã tin cậy
- **Lỗi 403 CSRF**: Thiếu `CSRF_TRUSTED_ORIGINS` — đã config sẵn
- **CSS/JS cũ**: Hard refresh `Ctrl+F5`
- **Tạo staff**: `python manage.py createsuperuser` → đăng nhập `/dang-nhap/`
- **Chạy prod local**: Waitress + Redis portable + Caddy thay cho `runserver` (hay tự tắt)

---

## Tài liệu

- [docs/deploy-production.md](docs/deploy-production.md) — Lên máy chủ: domain, HTTPS, Redis, waitress/Caddy
- [docs/database-setup.md](docs/database-setup.md) — SQL Server, phân quyền 2 chiều, seed
- [docs/https-cert.md](docs/https-cert.md) — Chứng chỉ dev vs public
- [docs/product-images.md](docs/product-images.md) — Ảnh sản phẩm thật
- [docs/troubleshooting.md](docs/troubleshooting.md) — Lỗi thường gặp và cách xử lý
- [docs/ci_and_quality.md](docs/ci_and_quality.md) — CI pipeline và quality gate
- [docs/web_auth.md](docs/web_auth.md) — Đăng nhập, phân quyền người dùng
- [docs/runbooks/backup-restore.md](docs/runbooks/backup-restore.md) — Backup/restore định kỳ

---

## License

MIT — Bản quyền © 2026 HuuGiau
