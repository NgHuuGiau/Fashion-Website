# Hướng dẫn cài đặt

## Yêu cầu hệ thống

| Yêu cầu | Phiên bản |
|---------|-----------|
| Python | 3.10 trở lên |
| Windows | 11+ (khuyên dùng) / 10 |
| PowerShell | 7+ (hoặc Windows PowerShell 5.1) |

## Cài đặt

```powershell
# 1. Clone repository
git clone <repo-url> Fashion-Website
cd Fashion-Website

# 2. Tạo môi trường ảo
python -m venv .venv

# 3. Kích hoạt
.venv\Scripts\Activate.ps1

# 4. Cài dependencies
pip install -r requirements.txt

# 5. Copy cấu hình
cp .env.example .env
# Mở .env để sửa nếu cần (mặc định chạy local được)

# 6. Kiểm tra hệ thống
cd backend
python manage.py check

# 7. Migrate database
python manage.py migrate

# 8. Seed dữ liệu sản phẩm
python manage.py seed_products --sync
```

## Cấu hình

File `.env` hỗ trợ các biến sau:

| Biến | Mặc định | Mô tả |
|------|---------|-------|
| `SECRET_KEY` | tự sinh | Khóa bí mật Django |
| `DEBUG` | `True` | Chế độ debug (tắt khi production) |
| `ALLOWED_HOSTS` | `127.0.0.1,localhost` | Danh sách host cho phép |
| `DB_PATH` | *(rỗng)* | Đường dẫn database tuỳ chỉnh |
| `SECURE_SSL_REDIRECT` | `False` | Chuyển hướng sang HTTPS |
| `SESSION_COOKIE_SECURE` | `False` | Cookie session an toàn |
| `CSRF_COOKIE_SECURE` | `False` | Cookie CSRF an toàn |
