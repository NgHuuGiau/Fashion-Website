# Xử lý sự cố thường gặp

Các lỗi đã gặp thật trên máy dev và cách xử lý.

## Web không khởi động / cổng bị chiếm

```powershell
netstat -ano | Select-String '8001'
Stop-Process -Id <PID> -Force
```

`runserver --noreload` chạy detached hay tự chết — dùng waitress theo `scripts/start-windows-web.ps1`.

## Trang 500 ở chế độ production local

Nguyên nhân từng gặp: thẻ `<script nonce>` nằm trong `{% compress %}` offline (nonce đổi mỗi request, manifest lệch key).
Đã sửa: script có nonce để ngoài block compress. Sau khi sửa template, restart waitress
(process cũ cache template) rồi chạy lại `python manage.py compress --force`.

## Static 404 dưới waitress

Waitress không serve `/static/` — kiến trúc prod trông chờ reverse proxy.
Chạy Caddy (`C:\caddy\caddy.exe run --config C:\caddy\Caddyfile.local`)
hoặc kiểm tra `staticfiles/` đã có sau `collectstatic` chưa.

## Lỗi 403 CSRF

Thiếu `CSRF_TRUSTED_ORIGINS` cho host/port đang dùng. Local đã cấu hình sẵn
`localhost:8000`/`127.0.0.1:8000` (HTTP+HTTPS); đổi port thì bổ sung tương ứng.

## Không kết nối SQL Server

- Kiểm tra ODBC Driver 17: `sqlcmd -?`
- Local dùng Windows Authentication (`DB_TRUSTED_CONNECTION=True`, user/pass để trống).
- Máy chủ dùng user riêng + `Encrypt=yes`.

## Test treo ở "Creating test database"

Lần chạy trước chết để lại DB rác `test_HUUGIAU_Fashion`. Xóa tay:

```powershell
sqlcmd -S localhost -E -C -Q "ALTER DATABASE [test_HUUGIAU_Fashion] SET SINGLE_USER WITH ROLLBACK IMMEDIATE; DROP DATABASE [test_HUUGIAU_Fashion];"
```

## Test `test_faq_payment_reply` fail sau khi bật bank ở `.env`

Test này từng phụ thuộc `.env` máy local. Đã bịt bằng `@override_settings`
trong `backend/products/tests.py` — bật/tắt bank local không còn ảnh hưởng suite.
Quy tắc: test nào đọc setting theo môi trường thì phải override tường minh.

## Checkout chờ lâu / map không hiện

- Leaflet tải lazy khi cuộn tới + timeout 10s; CDN `cdnjs` phải lọt CSP prod.
- API geocode timeout 8s; chưa có `GEOAPIFY_API_KEY` thì trả 503 nhanh — không treo.
