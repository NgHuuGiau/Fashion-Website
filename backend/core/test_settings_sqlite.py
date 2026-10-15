"""Temporary local-only test settings; do not use for deployment."""

import os

# Cho phép chạy test trên clone sạch, không cần file .env (CI cũng cấp biến qua env).
os.environ.setdefault(
    "SECRET_KEY", "test-only-secret-key-not-for-production-a1B2c3D4e5F6g7H8i9J0"
)
os.environ.setdefault("DEBUG", "True")

from .settings import *  # noqa: E402,F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.getenv("SQLITE_TEST_DB", ":memory:"),
    }
}

# Browser fixtures send a distinct X-Forwarded-For address per test so the
# production login rate limiter is exercised without sharing one client bucket.
TRUSTED_PROXY = True
