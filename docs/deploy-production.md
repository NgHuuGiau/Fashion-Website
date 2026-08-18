# Deploy production

Hướng dẫn đưa website thời trang lên môi trường thật (quốc tế). Stack hiện tại: Django 6 trên **Windows** với **SQL Server**. Có 2 đường triển khai khả thi.

## Lựa chọn 1 — VPS Windows (giữ nguyên stack, dễ nhất)

Vì code dùng `mssql-django` + `pyodbc`, giữ nguyên Windows/SQL Server là ít đổi nhất. Dùng VPS Windows Server 2019/2022 (VD: Azure VM B2s, Vultr Windows).

1. Cài Python 3.12 (64-bit), ODBC Driver 18 for SQL Server, SQL Server Express (hoặc SQL Server chuẩn nếu dùng external DB).
2. Copy repo, tạo venv, `pip install -r requirements.txt`.
3. Chạy script DB (`database/sql/`), `manage.py migrate`, `manage.py import_legacy`, `manage.py seed_products --sync`.
4. **WSGI server production:** thay `run_local.py` bằng waitress nhiều worker:

```powershell
pip install waitress
cd backend
waitress-serve --listen=0.0.0.0:8000 --threads=8 core.wsgi:application
```

5. Reverse proxy/https: dùng **nginx (Windows)** hoặc Caddy làm proxy để có HTTPS Let's Encrypt. Đơn giản nhất là Caddy (tự cấp + gia hạn chứng chỉ):

```caddyfile
huugiau.com {
    reverse_proxy 127.0.0.1:8000
}
```

```powershell
caddy start
```

6. Cấu hình `.env` production (xem mục Cấu hình production bên dưới).

## Lựa chọn 2 — VPS Linux + PostgreSQL (đổi DB)

Đổi `DB_ENGINE` sang Postgres thì mới chạy Linux trơn (pyodbc + SQL Server trên Linux gắn thêm thư viện). Cần chỉnh `settings.py` mở rộng cho `postgres` + `requirements.txt` thêm `psycopg[binary]`. Nhiều công hơn về data migration, chỉ làm nếu thật sự muốn chi phí rẻ hơn.

## Cấu hình production (`.env`)

```env
SECRET_KEY=<một chuỗi ngẫu nhiên dài 50+ ký tự — GIỮ KÍN>
DEBUG=False
ALLOWED_HOSTS=huugiau.com,www.huugiau.com
CSRF_TRUSTED_ORIGINS=https://huugiau.com,https://www.huugiau.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000

# Redis thật cho cache + session đa worker (bắt buộc nếu có >1 worker)
REDIS_URL=redis://127.0.0.1:6379/0

# Email thật
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=<App Password 16 ký tự>
DEFAULT_FROM_EMAIL=HUUGIAU Studio <no-reply@yourdomain.com>

# VNPay PRODUCTION (không dùng sandbox)
VNPAY_URL=https://pay.vnpayment.vn/paymentv2/vpcpay.html
VNPAY_TMN_CODE=<mã merchant thật>
VNPAY_HASH_SECRET=<khóa thật>

# Tùy chọn: GA4 + Zalo
GA4_MEASUREMENT_ID=G-XXXXXXXXXX
ZALO_OA_ID=<zalo oa id>
```

> `VNPAY_URL` cho production phải là `https://pay.vnpayment.vn/paymentv2/vpcpay.html` (cổng thanh toán VNPay thật, xác nhận lại khi đăng ký merchant). Sandbox dùng `https://sandbox.vnpayment.vn/paymentv2/vpcpay.html`.

## Steps sau khi deploy

1. `python manage.py collectstatic --noinput` + `python manage.py compress --force` (vì `COMPRESS_OFFLINE=True` khi `DEBUG=False`).
2. Tạo superuser: `python manage.py createsuperuser`.
3. Cài role sync trigger: `python manage.py install_role_sync`.
4. Backup tự động: đặt `backup-db.bat` vào Windows Task Scheduler chạy hằng ngày.
5. Tối ưu ảnh: `python manage.py optimize_images` (một lần) — chuyển ảnh sản phẩm sang WebP.

## Checklist an toàn

- [ ] `DEBUG=False` và `ALLOWED_HOSTS` có giá trị cụ thể (không `*`).
- [ ] `SECRET_KEY` ngẫu nhiên + không commit.
- [ ] Redis chạy và `REDIS_URL` đúng (nếu nhiều worker, LocMemCache KHÔNG hợp lệ).
- [ ] HTTPS từ Let's Encrypt, không có cảnh báo "Not secure".
- [ ] VNPay dùng merchant thật, test 1 đơn chuyển khoản + 1 đơn VNPay từ đầu tới cuối.
- [ ] Email gửi thật (đặt đơn → nhận mail).
- [ ] Backup DB chạy tự động mỗi ngày.