# Fashion Website

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-6.0.3-092E20?logo=django&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-Frontend-E34F26?logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-Styles-1572B6?logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-Interaction-F7DF1E?logo=javascript&logoColor=black)
![PowerShell](https://img.shields.io/badge/PowerShell-Scripts-5391FE?logo=powershell&logoColor=white)
![Pillow](https://img.shields.io/badge/Pillow-Image%20Processing-8CAAE6)
![Requests](https://img.shields.io/badge/Requests-HTTP-2D2D2D)
![DRF](https://img.shields.io/badge/DRF-API-A30000)

Website bán hàng cho local brand thời trang, xây dựng bằng Django và Django Templates. Dự án được tổ chức để chạy local nhanh, dễ seed dữ liệu, dễ kiểm tra luồng mua hàng và có sẵn dashboard quản trị cho staff.

---

## Mục lục

1. [Giới thiệu dự án](#1-giới-thiệu-dự-án)
2. [Ngôn ngữ, framework và thư viện](#2-ngôn-ngữ-framework-và-thư-viện)
3. [Cấu trúc dự án đầy đủ](#3-cấu-trúc-dự-án-đầy-đủ)
4. [Vai trò từng thư mục và file chính](#4-vai-trò-từng-thư-mục-và-file-chính)
5. [Yêu cầu môi trường](#5-yêu-cầu-môi-trường)
6. [Cài đặt dự án](#6-cài-đặt-dự-án)
7. [Cấu hình `.env`](#7-cấu-hình-env)
8. [Chạy dự án](#8-chạy-dự-án)
9. [URL quan trọng](#9-url-quan-trọng)
10. [Database, seed và ảnh sản phẩm](#10-database-seed-và-ảnh-sản-phẩm)
11. [Tài khoản mẫu](#11-tài-khoản-mẫu)
12. [Kiểm tra và test](#12-kiểm-tra-và-test)
13. [Lệnh thường dùng](#13-lệnh-thường-dùng)
14. [Ghi chú vận hành](#14-ghi-chú-vận-hành)

---

## 1. Giới thiệu dự án

### Dự án này làm gì

Hệ thống hiện hỗ trợ:

- hiển thị catalog sản phẩm
- lọc theo danh mục, khoảng giá, sắp xếp và tìm kiếm
- xem chi tiết sản phẩm
- chọn màu, size và số lượng
- thêm vào giỏ hàng
- checkout
- theo dõi đơn hàng
- wishlist
- chat hỗ trợ khách hàng
- dashboard quản trị sản phẩm và đơn hàng

### Mục tiêu tổ chức dự án

- dễ chạy local bằng PowerShell
- dễ seed dữ liệu để dựng nhanh môi trường demo
- dễ mở rộng thêm tính năng storefront
- tách rõ backend, frontend, database và script vận hành

### Phù hợp để dùng trong trường hợp nào

- làm demo website local brand
- học cấu trúc Django + templates
- mở rộng tiếp thành hệ thống bán hàng nhỏ
- dùng làm nền để thêm API hoặc frontend riêng sau này

---

## 2. Ngôn ngữ, framework và thư viện

### Ngôn ngữ đang dùng

| Thành phần | Ngôn ngữ |
|---|---|
| Backend | Python |
| Giao diện | HTML |
| Styling | CSS |
| Tương tác frontend | JavaScript |
| Script chạy local | PowerShell |
| Database | SQLite / SQL |

### Framework và nền tảng chính

| Thành phần | Công nghệ |
|---|---|
| Web framework | Django 6.0.3 |
| Database | SQLite |
| Template engine | Django Templates |
| Server local | Django development server |

### Các thư viện quan trọng trong `requirements.txt`

#### Nhóm backend web

- `Django==6.0.3`
- `djangorestframework==3.17.1`
- `django-allauth==65.15.0`
- `django-crispy-forms==2.6`
- `crispy-bootstrap5==2026.3`
- `django-debug-toolbar==6.2.0`
- `whitenoise==6.12.0`

#### Nhóm xử lý ảnh, dữ liệu, nội dung

- `pillow==12.1.1`
- `numpy==2.4.4`
- `pandas==3.0.2`
- `matplotlib==3.10.8`
- `beautifulsoup4==4.14.3`
- `requests==2.33.1`

#### Nhóm test và automation

- `selenium==4.41.0`
- `trio==0.33.0`
- `trio-websocket==0.12.2`
- `websocket-client==1.9.0`

#### Nhóm cấu hình và hỗ trợ

- `python-dotenv==1.2.2`
- `sqlparse==0.5.5`
- `tzdata==2025.3`

### Thư viện đang tham gia trực tiếp nhiều nhất vào code hiện tại

- Django
- SQLite
- Pillow
- requests
- python-dotenv

---

## 3. Cấu trúc dự án đầy đủ

### Cấu trúc tổng thể

```text
Fashion-Website/
├─ .github/
├─ .venv/
├─ backend/
├─ database/
├─ frontend/
├─ scripts/
├─ .gitignore
├─ LICENSE
├─ README.md
└─ requirements.txt
```

### Cấu trúc backend

```text
backend/
├─ manage.py
├─ db.sqlite3.corrupt.20260407.bak
├─ core/
│  ├─ __init__.py
│  ├─ asgi.py
│  ├─ settings.py
│  ├─ text_utils.py
│  ├─ urls.py
│  └─ wsgi.py
├─ orders/
│  ├─ admin.py
│  ├─ admin_product_dashboard.py
│  ├─ apps.py
│  ├─ cart.py
│  ├─ constants.py
│  ├─ context_processors.py
│  ├─ forms.py
│  ├─ models.py
│  ├─ tests.py
│  ├─ test_product_image_limits.py
│  ├─ test_tracking_eta.py
│  ├─ urls.py
│  ├─ views.py
│  ├─ management/
│  └─ migrations/
├─ products/
│  ├─ admin.py
│  ├─ apps.py
│  ├─ constants.py
│  ├─ models.py
│  ├─ tests.py
│  ├─ test_product_gallery.py
│  ├─ test_support_chat_context.py
│  ├─ urls.py
│  ├─ views.py
│  ├─ management/
│  │  └─ commands/
│  │     ├─ generate_product_artwork.py
│  │     └─ seed_products.py
│  ├─ migrations/
│  └─ templatetags/
│     └─ shop_format.py
└─ users/
   ├─ activity.py
   ├─ admin.py
   ├─ apps.py
   ├─ forms.py
   ├─ middleware.py
   ├─ models.py
   ├─ tests.py
   ├─ urls.py
   ├─ views.py
   └─ migrations/
```

### Cấu trúc frontend

```text
frontend/
├─ static/
│  ├─ css/
│  │  └─ site_theme.css
│  ├─ images/
│  │  └─ products/
│  │     ├─ gallery/
│  │     └─ generated/
│  └─ js/
│     └─ site_interactions.js
└─ templates/
   ├─ base.html
   ├─ account/
   │  ├─ my_orders.html
   │  ├─ order_review.html
   │  ├─ profile.html
   │  └─ wishlist.html
   ├─ admin/
   │  └─ admin_dashboard.html
   ├─ auth/
   │  ├─ login.html
   │  └─ register.html
   └─ shop/
      ├─ bank_payment_waiting.html
      ├─ cart.html
      ├─ checkout.html
      ├─ order_failed.html
      ├─ order_success.html
      ├─ product_catalog.html
      └─ product_detail.html
```

### Cấu trúc database và scripts

```text
database/
├─ db.sqlite3
└─ products_to_sync.json

scripts/
├─ local_smoke_test.ps1
└─ run_local.ps1
```

---

## 4. Vai trò từng thư mục và file chính

### `backend/core/`

| File | Vai trò |
|---|---|
| `settings.py` | cấu hình Django, database, static, media, middleware, `.env` |
| `urls.py` | URL root toàn hệ thống |
| `text_utils.py` | utility xử lý text tiếng Việt và chuỗi dùng chung |
| `asgi.py`, `wsgi.py` | entrypoint chạy ASGI/WSGI |

### `backend/products/`

| File | Vai trò |
|---|---|
| `models.py` | category, product, variant, gallery image, wishlist, FAQ |
| `views.py` | catalog, chi tiết sản phẩm, chat hỗ trợ, wishlist |
| `constants.py` | slug danh mục, label loại sản phẩm, giới hạn hiển thị |
| `urls.py` | route của app sản phẩm |
| `seed_products.py` | đồng bộ dữ liệu sản phẩm từ JSON |
| `generate_product_artwork.py` | tạo SVG nội bộ cho sản phẩm |
| `shop_format.py` | template filters như tiền, text, loại sản phẩm |

### `backend/orders/`

| File | Vai trò |
|---|---|
| `cart.py` | thao tác session cart |
| `models.py` | coupon, order, order item |
| `views.py` | checkout, thanh toán ngân hàng, order review, tracking |
| `constants.py` | hằng số ngân hàng, freeship, timeout |
| `forms.py` | form checkout |
| `admin_product_dashboard.py` | dashboard staff quản lý sản phẩm |
| `context_processors.py` | đẩy thông tin giỏ hàng vào template global |

### `backend/users/`

| File | Vai trò |
|---|---|
| `forms.py` | form đăng ký |
| `views.py` | login, register, logout, profile |
| `middleware.py` | visitor tracking |
| `activity.py` | ghi nhận hoạt động người dùng |
| `models.py` | hồ sơ người dùng và session truy cập |

### `frontend/templates/`

| Khu vực | Vai trò |
|---|---|
| `base.html` | layout gốc toàn site |
| `shop/` | giao diện bán hàng |
| `auth/` | trang đăng nhập và đăng ký |
| `account/` | trang tài khoản người dùng |
| `admin/` | dashboard quản trị |

### `frontend/static/`

| File / Thư mục | Vai trò |
|---|---|
| `css/site_theme.css` | CSS giao diện |
| `js/site_interactions.js` | JavaScript tương tác |
| `images/products/` | ảnh sản phẩm và artwork |

---

## 5. Yêu cầu môi trường

Bạn nên dùng:

- Windows PowerShell
- Python 3.11 hoặc 3.12
- `pip`

Kiểm tra Python:

```powershell
python --version
```

---

## 6. Cài đặt dự án

### Bước 1: clone source

```powershell
git clone <repo-url>
cd Fashion-Website
```

### Bước 2: tạo môi trường ảo

```powershell
python -m venv .venv
```

### Bước 3: kích hoạt môi trường ảo

```powershell
.venv\Scripts\Activate.ps1
```

Nếu PowerShell chặn script:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

rồi chạy lại:

```powershell
.venv\Scripts\Activate.ps1
```

### Bước 4: cài dependency

```powershell
pip install -r requirements.txt
```

---

## 7. Cấu hình `.env`

Tạo file `.env` ở root repo nếu cần:

```env
SECRET_KEY=django-insecure-change-this-in-env
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost,testserver
DB_PATH=
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
SECURE_HSTS_SECONDS=0
SECURE_HSTS_INCLUDE_SUBDOMAINS=False
SECURE_HSTS_PRELOAD=False
ENABLE_SQL_LOGGING=False
```

### Ý nghĩa

- `SECRET_KEY`: khóa bí mật Django
- `DEBUG`: bật hoặc tắt debug
- `ALLOWED_HOSTS`: host được phép truy cập
- `DB_PATH`: đổi đường dẫn SQLite nếu cần
- `ENABLE_SQL_LOGGING`: bật log SQL để debug query

---

## 8. Chạy dự án

### Cách nhanh nhất

```powershell
.\scripts\run_local.ps1
```

Script này sẽ:

1. kiểm tra cấu hình Django
2. chạy `migrate`
3. chạy `seed_products --sync`
4. mở trình duyệt tại `http://localhost:8000/`
5. chạy development server

### Tùy chọn script

#### Bỏ qua migrate

```powershell
.\scripts\run_local.ps1 -SkipMigrate
```

#### Bỏ qua seed

```powershell
.\scripts\run_local.ps1 -SkipSeed
```

#### Đổi cổng

```powershell
.\scripts\run_local.ps1 -Port 9000
```

#### Đổi host bind

```powershell
.\scripts\run_local.ps1 -BindHost 127.0.0.1
```

### Chạy thủ công

```powershell
.venv\Scripts\Activate.ps1
cd backend
python manage.py check
python manage.py migrate
python manage.py seed_products --sync
python manage.py runserver
```

---

## 9. URL quan trọng

- Trang chủ: `http://localhost:8000/`
- Đăng nhập: `http://localhost:8000/dang-nhap/`
- Dashboard staff: `http://localhost:8000/admin-dashboard/`
- Django admin: `http://localhost:8000/admin/`

---

## 10. Database, seed và ảnh sản phẩm

### Database

- engine: SQLite
- file mặc định: `database/db.sqlite3`

### Seed dữ liệu sản phẩm

```powershell
cd backend
python manage.py seed_products --sync
```

### Export dữ liệu ra JSON

```powershell
cd backend
python manage.py seed_products --export
```

### Random sản phẩm nổi bật

```powershell
cd backend
python manage.py seed_products --random-hot
python manage.py seed_products --shuffle-hot 12
```

### Ảnh sản phẩm

Ảnh được lưu trong:

- `frontend/static/images/products/gallery/`
- `frontend/static/images/products/generated/`

Hiện tại toàn bộ ảnh sản phẩm thật đã được xóa khỏi dữ liệu và thư mục, nên giao diện sẽ dùng placeholder nếu chưa thêm ảnh mới.

### Tạo lại artwork SVG

```powershell
cd backend
python manage.py generate_product_artwork
```

---

## 11. Tài khoản mẫu

### Admin

- username: `Admin`
- password: `Admin`

### User thường

- username: `User`
- password: `User`

---

## 12. Kiểm tra và test

### Kiểm tra cấu hình

```powershell
cd backend
python manage.py check
```

### Smoke test local

```powershell
.\scripts\local_smoke_test.ps1
```

Script này sẽ:

- kiểm tra Django import được
- chạy `manage.py check`
- chạy `migrate`
- chạy `seed_products --sync`
- bật server tạm ở cổng `8010`
- gọi HTTP tới trang chủ
- xác nhận server trả về `200 OK`

### Chạy test

```powershell
cd backend
python manage.py test
```

---

## 13. Lệnh thường dùng

```powershell
cd backend
python manage.py check
python manage.py migrate
python manage.py test
python manage.py seed_products --sync
python manage.py seed_products --export
python manage.py generate_product_artwork
python manage.py runserver
```

---

## 14. Ghi chú vận hành

- Nếu browser cache CSS hoặc JS cũ, dùng `Ctrl+F5`
- Nếu browser tự ép HTTPS, dùng `http://127.0.0.1:8000/`
- Nếu không muốn seed dữ liệu mỗi lần chạy local, dùng `-SkipSeed`
- `MEDIA_ROOT` hiện đang trỏ vào `frontend/static/images`, nghĩa là media và static image đang nằm chung một vùng thư mục

