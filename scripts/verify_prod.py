"""Verify go-live readiness. Fail exit=1 if blocker. Never prints secrets."""
import os
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
FAIL = []


def need(name, hint):
    v = os.getenv(name, "").strip()
    # ponytail: chỉ check presence/format, không in giá trị thật
    bad_markers = ("thay-bang", "your-", "change-me", "example.com", "django-insecure-")
    if not v or any(m in v.lower() for m in bad_markers):
        FAIL.append(f"{name}: {hint}")
        return None
    return v


def check():
    # Django core
    sk = os.getenv("SECRET_KEY", "")
    if len(sk) < 50 or len(set(sk)) < 5 or sk.lower().startswith("django-insecure-"):
        FAIL.append("SECRET_KEY: phai chuoi ngau nhien rieng >=50 ky tu")
    if os.getenv("DEBUG", "False").lower() in ("1", "true", "yes", "on"):
        FAIL.append("DEBUG: prod phai False")
    if "*" in os.getenv("ALLOWED_HOSTS", "") or not os.getenv("ALLOWED_HOSTS", "").strip():
        FAIL.append("ALLOWED_HOSTS: phai domain that, khong '*'")
    need("CSRF_TRUSTED_ORIGINS", "phai https://domain-that")
    # DB + Redis + Mail
    need("DB_HOST", "SQL Server prod host")
    need("DB_USER", "user least-privilege")
    need("DB_PASSWORD", "mat khau DB rieng")
    need("REDIS_URL", "redis co mat khau rieng")
    need("EMAIL_HOST", "SMTP that")
    need("EMAIL_HOST_USER", "tai khoan SMTP")
    need("DEFAULT_FROM_EMAIL", "no-reply@domain-that")
    # Proxy/HTTPS
    for k in ("BEHIND_PROXY", "TRUSTED_PROXY", "SECURE_SSL_REDIRECT"):
        if os.getenv(k, "").lower() not in ("1", "true", "yes", "on"):
            FAIL.append(f"{k}: phai True khi sau Caddy/nginx HTTPS")
    # Payment (canh bao, khong fail)
    if not os.getenv("SHOP_BANK_ACCOUNT", "").strip().isdigit():
        print("WARN: SHOP_BANK_ACCOUNT chua co STK that -> bank transfer dang tat")
    if not os.getenv("VNPAY_TMN_CODE", "").strip():
        print("WARN: VNPAY_TMN_CODE trong -> VNPay dang tat (cho merchant)")
    if not os.getenv("DOMAIN", "").strip():
        print("WARN: DOMAIN trong -> Caddy chua cap cert public")
    # Media tách static?
    media = os.getenv("MEDIA_ROOT", "")
    if not media or "frontend/static" in media.replace("\\", "/"):
        FAIL.append("MEDIA_ROOT: prod phai tach khoi frontend/static (vd D:/FashionMedia)")

    if FAIL:
        print("BLOCKER:")
        print("\n".join(f" - {f}" for f in FAIL))
        return 1
    print("OK: het blocker env co ban. Viec con lai: migrate SQL Server that, test mail/HTTPS/backup drill.")
    return 0


if __name__ == "__main__":
    sys.exit(check())
