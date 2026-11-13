# DEPLOYMENT CHECKLIST — HUUGIAU FASHION

Copy `.env.production.example` → `.env.production` rồi điền giá trị thật.
Không commit `.env.production`, không dùng lại mật khẩu mẫu.

## Bắt buộc (production)
- [ ] `SECRET_KEY` — `python -c "import secrets; print(secrets.token_urlsafe(50))"`
- [ ] `DEBUG=False`
- [ ] `DOMAIN`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` = domain thật (https)
- [ ] `BEHIND_PROXY=True`, `TRUSTED_PROXY=True`, `TRUSTED_PROXY_HOPS=2`
- [ ] `MEDIA_ROOT` tách khỏi code (vd `D:/FashionMedia`)

## Database (SQL Server)
- [ ] `DB_HOST`, `DB_PORT=1433`, `DB_DRIVER=ODBC Driver 18 for SQL Server`
- [ ] `DB_NAME=HUUGIAU_Fashion`, `DB_USER` (least privilege), `DB_PASSWORD` (16+ ký tự)
- [ ] `DB_TRUSTED_CONNECTION=False`, `DB_EXTRA_PARAMS=TrustServerCertificate=yes;Encrypt=yes`

## Redis / Celery
- [ ] `REDIS_URL` (có mật khẩu) `/0`
- [ ] `CELERY_BROKER_URL` `/1`, `CELERY_RESULT_BACKEND` `/2`

## Email (SMTP)
- [ ] `EMAIL_HOST`, `EMAIL_PORT=587`, `EMAIL_USE_TLS=True`
- [ ] `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` (app password 16 ký tự)
- [ ] `DEFAULT_FROM_EMAIL`, `SERVER_EMAIL`, `ADMIN_ALERT_EMAILS`

## Thông tin công khai (không được bịa)
- [ ] `HOTLINE`, `SUPPORT_EMAIL`, `STORE_ADDRESS` = giá trị thật
- [ ] Chỉ đặt `PUBLIC_CONTACTS_VERIFIED=True` sau khi đã kiểm tra hiển thị đúng
- [ ] `SHOP_TAX_ID`, `SHOP_BANK_ACCOUNT`, `SHOP_ACCOUNT_NAME` nếu bật chuyển khoản
- [ ] `BANK_TRANSFER_ENABLED=True` chỉ khi tài khoản + tên chủ tài khoản đã đúng

## Thanh toán / vận chuyển (chỉ bật khi có merchant thật)
- [ ] VNPay: `VNPAY_TMN_CODE`, `VNPAY_HASH_SECRET`, `VNPAY_ALLOWED_IPS`
- [ ] MoMo: `MOMO_PARTNER_CODE`, `MOMO_ACCESS_KEY`, `MOMO_SECRET_KEY`, `MOMO_ENDPOINT` (production, không sandbox)
- [ ] ZaloPay: `ZALOPAY_APP_ID`, `ZALOPAY_KEY1`, `ZALOPAY_KEY2`, `ZALOPAY_ENDPOINT`
- [ ] ShopeePay: `SHOPEEPAY_PARTNER_ID`, `SHOPEEPAY_KEY`, `SHOPEEPAY_SECRET`, `SHOPEEPAY_ENDPOINT`
- [ ] GHN: `GHN_TOKEN`, `GHN_SHOP_ID`, `GHN_WEBHOOK_TOKEN` (32+ ký tự)

## Tùy chọn
- [ ] `SENTRY_DSN` (để trống = tắt), `APP_ENV=production`
- [ ] `GA4_MEASUREMENT_ID`, `GEOAPIFY_API_KEY`, `ZALO_OA_ID`, `SOCIAL_*`, `BCT_BADGE_*`

## Kiểm tra trước khi go-live
```powershell
cd D:\Project\Fashion-Website
python scripts/validate_env.py                  # phải [SUCCESS]
python scripts/verify_prod.py --fail-on-blocker # phải OK
cd backend
python manage.py migrate --noinput
python manage.py compress --force
python manage.py collectstatic --noinput
python manage.py check --deploy --fail-level=ERROR
python -m pytest -q --ds=core.test_settings_sqlite
```

## Hạ tầng
- [ ] Caddy + Gunicorn/Uvicorn, Celery worker, Celery beat, Redis, SQL Server
- [ ] HTTPS cert OK; `/health/` trả 200, `/metrics/` chỉ mở nội bộ
- [ ] Sentry nhận được lỗi thử (nếu bật)
- [ ] Backup SQL Server đã lên lịch (`scripts/backup_db.ps1`) + đã thử restore
- [ ] Redis persistence bật
- [ ] Rollback: giữ bản release trước + backup DB trước khi migrate
