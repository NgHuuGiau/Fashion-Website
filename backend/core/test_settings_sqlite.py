"""Temporary local-only test settings; do not use for deployment."""

import os

# Set defaults BEFORE importing settings so the test runner / dev server can
# be started without manually exporting env vars.
os.environ.setdefault(
    "SECRET_KEY", "test-only-secret-key-not-for-production-a1B2c3D4e5F6g7H8i9J0"
)
os.environ.setdefault("DEBUG", "True")
os.environ.setdefault(
    "SQLITE_TEST_DB",
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".tmp-e2e.sqlite3"
    ),
)
os.environ.setdefault("SHOP_BANK_ACCOUNT", "")
os.environ.setdefault("VNPAY_TMN_CODE", "")
# Use file-based email backend for E2E tests (writes to files for cross-process access)
os.environ.setdefault(
    "EMAIL_BACKEND", "django.core.mail.backends.filebased.EmailBackend"
)
os.environ.setdefault(
    "EMAIL_FILE_PATH",
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".tmp-e2e-emails"
    ),
)

from .settings import *  # noqa: E402,F403

# Override EMAIL_FILE_PATH in settings (not read from env by default)
EMAIL_FILE_PATH = os.environ["EMAIL_FILE_PATH"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.environ["SQLITE_TEST_DB"],
    }
}

# Browser fixtures send a distinct X-Forwarded-For address per test so the
# production login rate limiter is exercised without sharing one client bucket.
TRUSTED_PROXY = True
