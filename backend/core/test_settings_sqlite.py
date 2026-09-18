"""Temporary local-only test settings; do not use for deployment."""

import os

from .settings import *  # noqa: F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.getenv("SQLITE_TEST_DB", ":memory:"),
    }
}

# Browser fixtures send a distinct X-Forwarded-For address per test so the
# production login rate limiter is exercised without sharing one client bucket.
TRUSTED_PROXY = True
