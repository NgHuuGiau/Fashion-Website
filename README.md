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
| **Backend (Django 5.2)** | ✅ 435 tests được collect; coverage cần xác nhận từ CI |
| **Database (SQL Server)** | ✅ Tự động migrate + import legacy |
| **Frontend (HTML5/CSS3/JS ES5)** | ✅ Responsive, editorial design |
| **Thanh toán (VNPay + VietQR)** | ✅ Gateway + IPN + callback + HMAC verify |
| **Email (SMTP)** | ✅ Xác nhận đơn, thanh toán, hủy, giao |
| **Admin Dashboard** | ✅ Doanh thu, CRUD, bulk actions, export CSV |
| **SSL Dev (HTTPS)** | ✅ Cert local + CA tin cậy |
| **CI/CD (GitHub Actions)** | ✅ PostgreSQL + Python 3.12/3.13 + CodeQL |

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

```ini
SECRET_KEY=your-secret-key
DEBUG=True
DB_ENGINE=mssql
DB_HOST=.
DB_NAME=HUUGIAU_Fashion
VNPAY_TMN_CODE=your_sandbox_tmn
VNPAY_HASH_SECRET=your_sandbox_secret
```

Production dùng `.env.production` với `DEBUG=False`, HTTPS, cookie secure và HSTS. Thay toàn bộ giá trị `replace-me` trước khi deploy.

> `CSRF_TRUSTED_ORIGINS` đã cấu hình sẵn trong `core/settings.py` (localhost:8000 HTTP/HTTPS).

### 3. Khởi tạo Database

```powershell
# Tạo tables + 76 sản phẩm, 2 màu và dữ liệu mẫu legacy (chạy trong SSMS)
database/sql/01_CREATE_TABLES.sql
database/sql/02_DEMO_DATA.sql

# Hoặc dùng Python command (tạo 1000 orders, 155 reviews, 49 addresses)
cd backend
python manage.py migrate
python manage.py seed_all --force --no-input
```

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

> Password hash pbkdf2_sha256. Sau 10 lần sai trong 5 phút → chặn 5 phút.

---

## Tính năng chính

| Module | Tính năng |
|---|---|
| **Trang chủ** | Hero editorial + sản phẩm nổi bật |
| **Danh mục** | Lọc category/size/color/price, sort, pagination (12/sp) |
| **Chi tiết SP** | Gallery 6 ảnh, variant (color+size), đã xem, size chart, wishlist |
| **Giỏ hàng** | Session-based, cập nhật SL, coupon, phí ship |
| **Thanh toán** | COD, VietQR (polling 15p), VNPay (redirect + IPN + HMAC) |
| **Email** | Xác nhận, thanh toán, hủy, giao (tự lấy email tài khoản) |
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

| App | Tests | Phủ |
|---|---|---|
| `orders` | 181 | Cart, checkout COD/bank/VNPay, VNPay IPN/callback, admin, coupon, export |
| `products` | 117 | Catalog, detail, variant, search, review, wishlist, compare, size guide |
| `users` | 64 | Auth, profile, role sync, activity |
| `core` | 44 | API, CSP, rate limit, cache, SEO, invoice |

> **Coverage 86%** — management commands (seed/import/export) bỏ qua vì chỉ dùng dev.

---

## CI/CD Pipeline

`.github/workflows/ci.yml`:
- **Lint**: Ruff (Python) + ESLint (JS)
- **Type Check**: Mypy (continue-on-error)
- **Security**: Bandit + pip-audit (continue-on-error)
- **Tests**: Django tests trên PostgreSQL (Python 3.12/3.13, Django 5.2)
- **Build**: Django check --deploy, collectstatic, compress
- **CodeQL**: Python + JavaScript analysis

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
