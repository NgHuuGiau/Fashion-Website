# HUUGIAU Atelier — Website thời trang

![Python](https://img.shields.io/badge/Python_3.12%2B-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django_6.x-092E20?logo=django&logoColor=white)
![SQL Server](https://img.shields.io/badge/SQL_Server-CC2927?logo=microsoftsqlserver&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-ES5-F7DF1E?logo=javascript&logoColor=black)
![Redis](https://img.shields.io/badge/Redis-DC382D?logo=redis&logoColor=white)
![VNPay](https://img.shields.io/badge/VNPay-006837)
![Pillow](https://img.shields.io/badge/Pillow-3776AB?logo=python&logoColor=white)
![Font Awesome](https://img.shields.io/badge/Font_Awesome_6.5-528DD7?logo=fontawesome&logoColor=white)
![Windows](https://img.shields.io/badge/Windows_11%2B-0078D4?logo=windows&logoColor=white)
![CI](https://img.shields.io/github/actions/workflow/status/NgHuuGiau/Fashion-Website/test.yml?logo=githubactions&logoColor=white&label=CI)
![Coverage](https://img.shields.io/badge/coverage-86%25-success)
![License](https://img.shields.io/badge/License-MIT-green)

Website bán thời trang xây dựng bằng Django, giao diện editorial, quản trị đơn giản.

## Yêu cầu hệ thống

- **Python** 3.12+ | **Windows** 11+ | **PowerShell** 7+
- **SQL Server** local (MSSQLSERVER) với **ODBC Driver 18 for SQL Server**
- **Django** 6.x | **mssql-django** | **pyodbc**

## Cấu hình

File `.env` ở thư mục gốc hỗ trợ:

| Biến | Mặc định | Mô tả |
|------|---------|-------|
| `SECRET_KEY` | tự sinh | Khóa bí mật Django |
| `DEBUG` | `True` | Chế độ debug |
| `ALLOWED_HOSTS` | `127.0.0.1,localhost` | Danh sách host cho phép |
| `DB_ENGINE` | `mssql` | Database engine (chỉ hỗ trợ `mssql` = SQL Server) |
| `DB_HOST` | `.` | Host SQL Server (`.` = shared memory) |
| `DB_PORT` | *(rỗng)* | Port (để trống nếu dùng shared memory) |
| `DB_NAME` | `HUUGIAU_Fashion` | Tên database |
| `REDIS_URL` | *(rỗng)* | Redis cho cache + session |
| `COMPRESS_ENABLED` | `False` | Bật nén CSS/JS |
| `EMAIL_HOST` | *(rỗng)* | SMTP server (bỏ trống = tắt gửi mail) |
| `EMAIL_HOST_USER` | *(rỗng)* | Email gửi thông báo (Gmail App Password) |
| `EMAIL_HOST_PASSWORD` | *(rỗng)* | App Password 16 ký tự |
| `VNPAY_TMN_CODE` | *(rỗng)* | Mã merchant VNPay (sandbox) |
| `VNPAY_HASH_SECRET` | *(rỗng)* | Secret key VNPay (sandbox) |
| `GA4_MEASUREMENT_ID` | *(rỗng)* | Google Analytics 4 (để trống = tắt) |
| `ZALO_OA_ID` | *(rỗng)* | Zalo Official Account — hiện nút chat Zalo (để trống = tắt) |

> `CSRF_TRUSTED_ORIGINS` được khai báo cứng trong `core/settings.py` (gồm `https://localhost:8000`, `https://127.0.0.1:8000` và bản `http` tương ứng) — bắt buộc vì trình duyệt gửi header `Origin` khi POST; thiếu sẽ bị lỗi `403 Forbidden — Origin checking failed`.

## Công nghệ

| Layer | Công nghệ |
|-------|-----------|
| Backend | Python 3.12+ (CI chạy 3.12/3.13), Django 6.0 |
| Database | SQL Server (local) |
| Frontend | HTML5, CSS3 (~5.4K dòng), JavaScript ES5 |
| UI Icons | Font Awesome 6.5 (local + CDN dự phòng) |
| Thanh toán | VietQR (23 ngân hàng), VNPay |
| Email | SMTP (Gmail App Password) — xác nhận đơn, đã thanh toán, hủy, hoàn thành |
| Ảnh sản phẩm | `optimize_images` chuyển ảnh upload sang WebP (Pillow) |
| Analytics | Google Analytics 4 (tùy chọn), nút chat Zalo OA (tùy chọn) |
| Testing | Django TestCase — 400 tests, coverage 86% |
| CI/CD | GitHub Actions: test trên SQL Server 2022 (Docker, Python 3.12/3.13) + CodeQL |
| Export | CSV, JSON |

## Tính năng chính

- **Trang chủ editorial** — hero + sản phẩm nổi bật
- **Danh mục** — lọc theo danh mục, size, màu, giá, sắp xếp, phân trang (12/sp)
- **Chi tiết sản phẩm** — gallery (6 ảnh), biến thể (màu + size), đã xem gần đây, size chart, wishlist
- **Giỏ hàng** — session-based, cập nhật số lượng, coupon, phí ship
- **Thanh toán** — COD, chuyển khoản VietQR (polling trạng thái, tự hết hạn 15 phút), VNPay (redirect gateway + callback/IPN xác minh chữ ký HMAC)
- **Email thông báo** — gửi tự động khi đặt hàng, thanh toán thành công, hủy đơn, giao xong (bỏ trống email trong đơn → tự lấy email trong tài khoản)
- **Tra cứu đơn hàng** — khách vãng lai tra bằng mã đơn + SĐT, hủy đơn + hoàn stock
- **Tìm kiếm** — gợi ý tự động (debounce 250ms, 6 kết quả), không phân biệt dấu
- **Đăng nhập** — bằng email / SĐT / username
- **Support chat** — FAQ, gợi ý size, ngữ cảnh
- **Admin dashboard** — biểu đồ doanh thu 7 ngày, CRUD sản phẩm, gallery, variants, quản lý đơn hàng + coupon, bulk actions, xuất CSV, **báo cáo doanh thu theo tháng + xuất CSV**
- **Tối ưu ảnh** — `python manage.py optimize_images --dry-run` để xem, bỏ `--dry-run` để chuyển toàn bộ ảnh sản phẩm sang WebP

## Cài đặt nhanh

### 1. Chuẩn bị database

Chạy script tạo tables + insert dữ liệu mẫu trên SQL Server:

```powershell
# Mở SSMS, kết nối local server, mở và chạy:
database/sql/01_CREATE_TABLES.sql
database/sql/02_INSERT_DATA.sql
```

### 2. Cài đặt Python

```powershell
git clone <repo-url> Fashion-Website
cd Fashion-Website
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Chạy migrate + import dữ liệu

```powershell
cd backend
python manage.py migrate
python manage.py import_legacy
python manage.py seed_products --sync
python manage.py runserver localhost:8000
```

Server dev tự chạy **HTTPS** bằng cert trong `backend/certs`. CA `backend/certs/ca.crt` đã được cài vào Windows Trust Store → mở bằng Chrome/Edge **không còn cảnh báo** "Not secure". Nếu máy khác chưa cài CA, làm theo [docs/https-cert.md](docs/https-cert.md).

> **Cách chạy nhanh nhất:** chạy `.\scripts\start.bat` — script tự khởi động server, chờ server sẵn sàng rồi tự mở trình duyệt vào `https://localhost:8000/`.

> Lưu ý: `import_legacy` đọc từ các bảng legacy (`[Users]`, `[Products]`, ...) trong SQL Server; nếu chưa có bảng legacy thì nó bỏ qua (không lỗi). `seed_products --sync` đồng bộ sản phẩm mẫu.

## Import dữ liệu từ SQL scripts

```powershell
cd backend
python manage.py import_legacy
```

Command này đọc dữ liệu từ legacy tables (`[Users]`, `[Products]`, `[Orders]`...) và chuyển vào Django ORM tables với mapping column tự động (xem `orders/management/commands/import_legacy.py`).

## Cấu trúc thư mục

```
Fashion-Website/
├── backend/               # Django project
│   ├── core/              # Settings, URL config, utilities
│   ├── orders/            # Cart, checkout, payment, admin
│   ├── products/          # Catalog, product detail, search
│   ├── users/             # Auth, profiles, activity
│   ├── certs/             # SSL certificates (dev)
│   ├── run_local.py       # Dev server (HTTPS, thay manage.py runserver)
│   └── manage.py
├── frontend/              # Static files & templates
│   ├── static/            # CSS, JS, fonts, images
│   └── templates/         # HTML templates
├── database/
│   ├── sql/               # SQL scripts (CREATE + INSERT)
│   └── seed/              # Seed data JSON
├── scripts/               # Utility scripts
│   ├── start.ps1          # Chạy HTTP server + tự mở trình duyệt (khuyến nghị)
│   ├── start.bat          # Gọi start.ps1 (double-click là chạy)
│   ├── run_local.ps1
│   ├── dev_server.py
│   └── local_smoke_test.ps1
├── chay-web.bat           # Double-click rồi chạy — mở web tại https://127.0.0.1:8000/
├── backup-db.bat          # Backup DB tự động (giữ 7 ngày, lưu vào backups/)
├── backups/               # File backup .bak (đã gitignore, OneDrive tự đồng bộ cloud)
├── .github/workflows/     # CI: test.yml (SQL Server 2022 Docker), codeql.yml
├── docs/                  # Documentation
├── .env
└── requirements.txt
```

## Testing

```powershell
cd backend
python manage.py test
```

> Do SQL Server local, chạy cả suite 1 lệnh có thể bị timeout — chạy theo từng app:
> `python manage.py test users` / `products` / `orders` / `core` (hoặc theo tên class như `orders.tests.VNPayTest`).

**Phủ test hiện tại (400+ tests, coverage 86%):**

| App | Số test | Phủ những gì |
|-----|--------|--------------|
| `orders` | 181 | Giỏ hàng, checkout (COD/bank/VNPay), thanh toán chuyển khoản (QR, confirm, cancel, hết hạn 15p), VNPay (15 test: gateway, callback, IPN, chữ ký, auto-expire), đơn hàng của tôi, tra cứu, mua lại, admin dashboard, báo cáo doanh thu theo tháng + export CSV, coupon, export CSV |
| `products` | 117 | Danh mục, chi tiết, biến thể, tìm kiếm, gợi ý, wishlist, đánh giá (sao/trung bình), support chat, size gợi ý, model methods, nén ảnh WebP, GA4 + nút chat Zalo |
| `users` | 64 | Đăng ký, đăng nhập, hồ sơ, phân quyền, role sync, activity log |
| `core` | 44 | API đơn hàng/admin, CSP header, chống spam đăng nhập (rate limit), cache, SEO, in hóa đơn, trang lỗi |

**Đo coverage (đã có `coverage.py`):**
```powershell
coverage run --source=core,orders,products,users manage.py test products
coverage report -m          # bảng phủ từng file
coverage html               # mở htmlcov/index.html
```

> Phần chưa test chủ yếu là *management commands* (seed/export/import) — bỏ qua vì chỉ dùng phát triển, không thuộc luồng nghiệp vụ.
> Lưu ý: chạy 2 lệnh test **song song** trên cùng test DB có thể gây deadlock SQL — luôn chạy tuần tự.

## URL chính

| URL | Mô tả |
|-----|-------|
| `https://localhost:8000/` | Trang chủ / danh mục sản phẩm |
| `https://localhost:8000/admin-dashboard/` | Quản trị (chỉ staff) |
| `https://localhost:8000/dang-nhap/` | Đăng nhập |
| `https://localhost:8000/dang-ky/` | Đăng ký |
| `https://localhost:8000/gio-hang/` | Giỏ hàng |
| `https://localhost:8000/tra-cuu-don/` | Tra cứu đơn hàng |

## Tài khoản mặc định

Database `HUUGIAU_Fashion` đã có sẵn 18 tài khoản (được `seed_all.py` + `import_legacy` tạo):

| Vai trò | Username | Password |
|---------|----------|----------|
| Quản trị (superuser + staff) | `admin` | `admin123` |
| Nhân viên (staff) | `codexstaff` | `staff123` |
| Nhân viên (staff) | `readmestaff` | `readme123` |
| Khách hàng (15 user) | `nguyenvanA`, `tranthib`, `lethic`, `phamvand`, `hoangthie`, `nguyenvanE`, `phamthif`, `hoangthig`, `dothih`, `buithii`, `dangthank`, `ngothil`, `lyvanm`, `tranvann`, `vuongo` | `user123` |

> Password trong DB là hash pbkdf2 (không đọc được từ SQL). Mật khẩu đúng là như bảng trên. Sau **10 lần sai trong 5 phút**, hệ thống chặn đăng nhập 5 phút ("Quá nhiều lần đăng nhập") — restart server để reset hoặc chờ 5 phút.

## Ghi chú

- Dùng SQL Server làm database chính (`DB_ENGINE=mssql`)
- **Phân quyền đồng bộ 2 chiều:** đổi quyền trên web (Django admin) là SQL Server `[Users].role` đổi theo (signal tự động); đổi `[Users].role` trong SSMS là web đổi theo — chạy `python manage.py install_role_sync` một lần để cài trigger (chi tiết `docs/database-setup.md`)
- **Cách chạy nhanh nhất:** double-click `chay-web.bat` (dùng `run_local.py` tại `https://127.0.0.1:8000/`) hoặc `.\scripts\start.bat` — chạy là tự mở web `https://localhost:8000/`
- **CI:** mỗi commit push lên `main`/`develop` hoặc PR đều chạy 400 tests trên SQL Server 2022 (Docker) — xem trạng thái tại badge **CI** ở đầu README
- Server dev chạy HTTPS bằng cert trong `backend/certs` — đã cài CA tin cậy nên Chrome/Edge hết cảnh báo (xem `docs/https-cert.md`)
- Lỗi `403 CSRF — Origin checking failed` thường do thiếu `CSRF_TRUSTED_ORIGINS` — đã cấu hình sẵn trong `core/settings.py`
- Nếu CSS/JS cũ, hard refresh (Ctrl+F5)
- Tạo thêm tài khoản staff: `python manage.py createsuperuser` → đăng nhập tại `/dang-nhap/`
- **Backup DB:** chạy `.\backup-db.bat` để backup vào `backups/` (giữ 7 ngày). Lần đầu chạy báo lỗi *Access denied* thì chạy `icacls "backups" /grant "NT SERVICE\MSSQLSERVER:(OI)(CI)M"` 1 lần. Đặt trong Windows Task Scheduler để chạy tự động mỗi ngày.

## License

MIT — Bản quyền © 2026 HuuGiau
