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

Website bán thời trang xây dựng bằng Django, giao diện editorial, quản trị đơn giản.

---

## Trạng thái dự án (09/2026)

| Thành phần | Trạng thái |
|---|---|
| **Backend (Django 5.2)** | Có các luồng cửa hàng và bộ test; xem kết quả CI mới nhất trước khi phát hành |
| **Database (SQL Server)** | Có backend SQL Server; cần kiểm tra kết nối, migration và full test trên đúng SQL Server triển khai |
| **Frontend (HTML5/CSS3/JS)** | Giao diện responsive; cần kiểm tra lại trên thiết bị và trình duyệt mục tiêu |
| **Thanh toán** | Có code VNPay và VietQR; VNPay cần merchant/callback thật. VietQR là chuyển khoản cần nhân viên đối soát, không có IPN ngân hàng |
| **Email** | Có code gửi email; cần SMTP thật và kiểm tra nhận email trước khi mở bán |
| **Admin Dashboard** | Có dashboard, CRUD, bulk actions và export CSV |
| **HTTPS** | Cấu hình HTTPS production tại reverse proxy; chứng chỉ local không thay cho domain/SSL public |
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
| **Giỏ hàng** | Session-based, cập nhật SL, coupon, phí ship |
| **Thanh toán** | COD; VietQR chờ nhân viên đối soát; VNPay redirect + xác minh chữ ký callback/IPN khi đã cấu hình merchant |
| **Email** | Mẫu xác nhận, thanh toán, hủy, giao; chỉ gửi được khi SMTP và địa chỉ nhận hợp lệ |
| **Tra cứu đơn** | Mã đơn + SĐT, hủy đơn + hoàn stock |
| **Tìm kiếm** | Gợi ý debounce 250ms, không phân biệt dấu |
| **Đăng nhập** | Email / SĐT / username |
| **Support chat** | FAQ, size gợi ý |
| **Admin** | Dashboard doanh thu 7 ngày, CRUD SP/dơn/coupon, bulk actions, export CSV, báo cáo tháng |
| **So sánh SP** | Toggle trên card/detail, bảng so sánh max 4 SP |
| **Timeline đơn** | 4 bước: Xác nhận → Đóng gói → Đang giao → Đã giao |
| **Nhắc giỏ** | Email tự động (`send_cart_reminders`) |

---

## Cấu trúc thư mục

```
Fashion-Website/
├── backend/               # Django project
│   ├── core/              # Settings, URLs, utilities, middleware
│   ├── orders/            # Cart, checkout, payment, admin
│   ├── products/          # Catalog, detail, search, reviews
│   ├── users/             # Auth, profiles, activity, referral
│   ├── certs/             # SSL certs (dev)
│   └── manage.py
├── frontend/              # Static + templates
│   ├── static/            # CSS (~5.4K lines), JS ES5, fonts, images
│   └── templates/         # HTML templates
├── database/
│   ├── sql/               # 01_CREATE_TABLES.sql, 02_DEMO_DATA.sql
│   └── seed/              # products_to_sync.json
├── scripts/               # Utility scripts
│   ├── start.ps1          # HTTPS server + auto-open browser (khuyên dùng)
│   ├── start.bat          # Wrapper cho start.ps1
│   ├── dev_server.py      # Dev server helper
│   └── local_smoke_test.ps1
├── chay-web.bat           # Double-click chạy (gọi scripts/start.ps1)
├── backup-db.bat          # Backup DB tự động (giữ 7 ngày)
├── backups/               # .bak files (gitignored, OneDrive sync)
├── .github/workflows/     # CI: ci.yml + codeql.yml
├── docs/                  # Tài liệu
├── .env                   # Cấu hình (gitignored)
└── requirements.txt
```

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
| `orders` | Cart, checkout COD/bank/VNPay, callback, admin, coupon, export |
| `products` | Catalog, detail, variant, search, review, wishlist, compare, size guide |
| `users` | Auth, profile, role sync, activity |
| `core` | API, CSP, rate limit, cache, SEO, invoice |

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

---

## License

MIT — Bản quyền © 2026 HuuGiau
