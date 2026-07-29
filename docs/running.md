# Hướng dẫn chạy

## Chạy nhanh

```powershell
.\scripts\run_local.ps1
```

Script sẽ:
1. Chạy `python manage.py check`
2. Chạy `python manage.py migrate`
3. Chạy `python manage.py seed_products --sync`
4. Mở server tại `http://localhost:8000/`

## Chạy thủ công từng bước

```powershell
cd backend
python manage.py check          # Kiểm tra hệ thống
python manage.py migrate        # Đồng bộ database
python manage.py seed_products --sync  # Seed sản phẩm
python manage.py runserver localhost:8000  # Chạy server
```

## Các URL chính

| URL | Mô tả |
|-----|-------|
| `http://localhost:8000/` | Trang chủ / danh mục sản phẩm |
| `http://localhost:8000/admin-dashboard/` | Quản trị (chỉ staff) |
| `http://localhost:8000/dang-nhap/` | Đăng nhập |
| `http://localhost:8000/dang-ky/` | Đăng ký |
| `http://localhost:8000/gio-hang/` | Giỏ hàng |
| `http://localhost:8000/tra-cuu-don/` | Tra cứu đơn hàng |

## Tài khoản admin

Tạo tài khoản staff:

```powershell
cd backend
python manage.py createsuperuser
```

Sau đó đăng nhập tại `/dang-nhap/` và vào `/admin-dashboard/`.

## Chạy test

```powershell
cd backend
python manage.py test
```

## Kiểm tra nhanh

```powershell
.\scripts\local_smoke_test.ps1
```

Script kiểm tra server trả về kết quả trên các endpoint chính.
