# 🛍️ Fashion Store - Local Brand E-Commerce Platform

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Django](https://img.shields.io/badge/Django-5.x-darkgreen.svg)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

Một nền tảng web thương mại điện tử chuyên biệt dành cho các local brand thời trang. Dự án cung cấp đầy đủ các tính năng từ mua sắm đến quản trị hệ thống, được xây dựng trên framework **Django** mạnh mẽ giúp đảm bảo hiệu năng và cấu trúc chuẩn mực.

---

## ✨ Tính Năng Nổi Bật (Features)

- 🛒 **Mua sắm linh hoạt:** Trưng bày sản phẩm trực quan, tính năng giỏ hàng (Cart) và quy trình thanh toán (Checkout) mượt mà.
- 🔐 **Quản lý tài khoản:** Đăng nhập, đăng ký, bảo vệ mật khẩu, và lưu trữ lịch sử đơn hàng của người dùng.
- 📊 **Dashboard Quản trị (Admin):** Giao diện thiết kế riêng (Custom Dashboard) dành cho nhân viên/quản lý để theo dõi doanh thu, xử lý sản phẩm và trạng thái đơn hàng.
- 📱 **Giao diện Responsive:** Giao diện tối ưu hiển thị tốt trên mọi thiết bị: PC, Tablet và Mobile.
- 🛡️ **Bảo mật:** Tích hợp kiểm thử bảo mật nâng cao và áp dụng các chuẩn an toàn gốc rễ của Django framework.

---

## 💻 Tech Stack (Công nghệ sử dụng)

- **Backend:** Python, Django
- **Frontend:** HTML5, CSS3, Vanilla JavaScript, Django Templates
- **Database:** SQLite (chuyên dụng cho môi trường Development)

---

## 🚀 Hướng Dẫn Cài Đặt (Local Development)

### 1. Yêu cầu hệ thống
- Python 3.x
- Git

### 2. Thiết lập dự án

**Bước 1: Clone mã nguồn và kích hoạt môi trường ảo**
```powershell
cd "D:\File Code\Fashion Website"
.\.venv\Scripts\activate
```

**Bước 2: Thiết lập tham số môi trường (`.env`)**
Bạn cần thiết lập các thông số bảo mật và môi trường để khởi chạy.
```powershell
Copy-Item .env.example .env
```
Truy cập file `.env` vừa tạo và chỉnh sửa một số biến:
- `SECRET_KEY`: Khóa bảo mật cốt lõi của Django.
- `DEBUG`: Đặt bằng `True` nếu đang lập trình local, `False` nếu đã đưa lên Production.
- `ALLOWED_HOSTS`: Các tên miền/IP được cho phép (vd: `127.0.0.1,localhost`).

**Bước 3: Khởi tạo dữ liệu và chạy Server**
```powershell
cd backend
python manage.py migrate                      # Khởi tạo bảng dữ liệu Database
python manage.py seed_products --sync         # Đồng bộ dữ liệu từ JSON
python manage.py seed_products --random-hot    # Ngẫu nhiên 12 sản phẩm HOT
python manage.py runserver                    # Khởi động Web Server
```

> 🌐 **Local URL:** Web được chạy tĩnh tại `http://127.0.0.1:8000/`

---

Trong thư mục `backend/`, mình đã cung cấp lệnh tích hợp để bạn quản trị Database nhanh chóng mà không cần file lẻ:

- **`--sync`**: Đồng bộ sản phẩm từ file JSON vào website.
- **`--export`**: Xuất toàn bộ sản phẩm hiện có ra file JSON.
- **`--random-hot`**: Tự động chọn ngẫu nhiên 12 sản phẩm HOT.
- **`--inspect`**: Hiển thị bảng biểu dữ liệu trực quan ngay trên Terminal.
- **`--shell`**: Môi trường nhập lệnh SQL tương tác.
- **`--run-sql`**: Chạy nhanh file SQL bất kỳ.

**Cách dùng chung:**
```powershell
python manage.py seed_products [tham số]
```

---

## 🛣️ Các Đường Dẫn Hệ Thống Quan Trọng (Routing)

- **Trang chủ:** `/`
- **Đăng nhập:** `/dang-nhap/`
- **Đăng ký:** `/dang-ky/`
- **Dashboard định chuẩn (Nhân viên):** `/admin-dashboard/`
- **Trang quản trị (Django Admin):** `/admin/`

---

## 🧪 Kiểm Thử & Gỡ Lỗi (Testing & Checks)

Để đảm bảo hệ thống vận hành đúng luồng và không có rủi ro tiềm ẩn, hãy chạy các lệnh sau:

```powershell
cd backend
# Kiểm tra lỗi cấu trúc tổng hợp của nền tảng
python manage.py check

# Kiểm tra các cảnh báo quan trọng nếu dùng ở trạng thái Deploy
python manage.py check --deploy

# Chạy Unit Tests để test từng phần
python manage.py test -v 2
```

---

## 🔒 Hướng Dẫn Push GitHub & Bảo Mật

Việc vô tình đưa những file không thuộc về Repository lên mạng tiềm ẩn nguy cơ bảo mật. Tuyệt đối **KHÔNG** push các file sau:
- Thư mục ảo (`.venv/`)
- Mật khẩu & Cấu hình cục bộ (`.env`)
- Các cơ sở dữ liệu (`*.sqlite3`, `*.db`)
*(Chủ dự án chỉ cần push file `.env.example` chứa các Key chưa gán Value để setup dễ hiểu).*

**Chuỗi lệnh Push dự án mẫu chuẩn:**
```powershell
git add .
git commit -m "<loại>: <tiêu đề ngắn gọn>"
git pull --rebase origin main
git push origin main
```

### 🔒 Các loại Commit (Commit Types)
Để quản lý mã nguồn chuyên nghiệp, vui lòng tuân thủ các tiền tố sau trong tiêu đề commit:
- `feat`: Tính năng mới.
- `fix`: Sửa lỗi.
- `docs`: Tài liệu.
- `style`: Định dạng code (không đổi logic).
- `refactor`: Tái cấu trúc code.
- `chore`: Thay đổi linh tinh (quản lý package, chuẩn bị...).
