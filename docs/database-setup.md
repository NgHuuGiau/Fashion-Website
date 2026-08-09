# Database Setup

## 1. Requirements

- SQL Server local instance (MSSQLSERVER)
- ODBC Driver 18 for SQL Server ([tải về](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server))
- Windows Authentication (mặc định)

## 2. Kiểm tra kết nối ODBC

```powershell
python -c "
import pyodbc
cn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER=.;Trusted_Connection=yes;TrustServerCertificate=yes;Encrypt=yes')
print('OK')
"
```

## 3. Tạo database và tables

Mở **SSMS**, chạy lần lượt:

```sql
-- database/sql/01_CREATE_TABLES.sql
-- database/sql/02_INSERT_DATA.sql
```

Hoặc chạy bằng script Python:

```powershell
cd backend
python -c "
from django.db import connection
with connection.cursor() as cur:
    sql = open('../database/sql/01_CREATE_TABLES.sql', encoding='utf-8').read()
    for batch in sql.split('GO'):
        if batch.strip(): cur.execute(batch)
"
```

## 4. Migrate Django tables

```powershell
cd backend
python manage.py migrate
```

Tạo các Django system tables: `auth_user`, `django_session`, `products_product`, `orders_order`, ...

## 5. Import dữ liệu từ legacy tables

```powershell
python manage.py import_legacy
```

Đọc từ legacy tables (`[Users]`, `[Products]`, `[Orders]`, ...) và insert vào Django ORM tables với mapping:

| Legacy table | Django table | Ghi chú |
|-------------|--------------|---------|
| `[Users]` | `auth_user` + `users_userprofile` | role → is_staff/is_superuser, phone → profile |
| `[Categories]` | `products_category` | Direct mapping |
| `[Products]` | `products_product` | Thiếu description, image, updated (auto) |
| `[Variants]` | `products_productvariant` | Direct mapping |
| `[Coupons]` | `orders_coupon` | type→discount_type, min_amount→min_order_amount, ... |
| `[Orders]` | `orders_order` | coupon→coupon_code (string), coupon→coupon_id (FK, nullable) |
| `[OrderItems]` | `orders_orderitem` | color→selected_color, size→selected_size |
| `[Wishlist]` | `products_wishlistitem` | Direct mapping |
| `[FAQs]` | `products_supportfaq` | Thiếu keywords, created, updated (auto) |
| `[Activities]` | `users_useractivity` | event→event_type |

## 6. Database engine

Hệ thống chỉ hỗ trợ **SQL Server** (`DB_ENGINE=mssql`). Không còn hỗ trợ SQLite.

```
DB_ENGINE=mssql
```

Sau khi đổi cấu hình, cần chạy lại `migrate` và `import_legacy`.

## 7. Đồng bộ phân quyền (role 0/1/2) giữa SQL Server và web

Quyền của user nằm ở bảng `auth_user` (`is_staff`/`is_superuser`) trong khi bảng legacy `[Users]` lưu cột `role` (0 = admin, 1 = nhân viên, 2 = khách hàng). Hai chiều đồng bộ:

**1) Web → SQL Server:** tự động. Mỗi lần lưu user (Django admin, `createsuperuser`, ...), Django ghi `role` tương ứng vào bảng `[Users]` (signal `users.signals`).

**2) SQL Server → Web:** cài trigger trên bảng `[Users]` để sửa `role` trực tiếp trong SSMS là `auth_user` đổi theo ngay. Chạy một lần:

```
python manage.py install_role_sync
```

Nếu không muốn dùng trigger, chạy thủ công khi cần:

```
python manage.py sync_roles
```

> Lưu ý: signal chỉ cập nhật user **đã có dòng trong bảng `[Users]`** (thường là user đã import). User đăng ký mới hoàn toàn trên web sẽ không tự thêm vào `[Users]`.

## 8. Tài khoản mặc định

Database có sẵn 18 tài khoản (hash pbkdf2 — không đọc được từ SQL, dùng đúng password bên dưới):

| Vai trò | Username | Password |
|---------|----------|----------|
| Quản trị | `admin` | `admin123` |
| Nhân viên | `codexstaff` | `staff123` |
| Nhân viên | `readmestaff` | `readme123` |
| Khách hàng (15) | `nguyenvanA`, `tranthib`, `lethic`, `phamvand`, `hoangthie`, `nguyenvanE`, `phamthif`, `hoangthig`, `dothih`, `buithii`, `dangthank`, `ngothil`, `lyvanm`, `tranvann`, `vuongo` | `user123` |

> Login chấp nhận username, email hoặc SĐT (lấy từ `users_userprofile`). Chặn sau 10 lần sai/5 phút; restart server để reset.

## 9. Lưu ý

- SQL Server dùng Windows Authentication (Trusted_Connection=yes)
- Host `.` (dot) = shared memory/named pipes, không cần bật TCP/IP
- Password trong `[Users]` đã là hash Django pbkdf2 hợp lệ
- Các legacy tables có thể xoá sau khi import thành công (trừ khi muốn giữ đồng bộ role)
