"""Kiểm thử các guard fail-fast của settings khi chạy production (DEBUG=False).

Mỗi ca chạy trong tiến trình con với biến môi trường riêng để cô lập. Ghi chú:
`core.settings` nạp `.env` với `override=False`, nên biến môi trường đã đặt sẵn
luôn thắng file `.env` — đủ để mô phỏng thiếu/sai cấu hình.
"""

import os
import subprocess
import sys
from pathlib import Path

from django.test import SimpleTestCase

BACKEND_DIR = Path(__file__).resolve().parent.parent

BASE_ENV = {
    "DEBUG": "False",
    "DB_ENGINE": "postgres",
    "REDIS_URL": "redis://localhost:6379/0",
    "ALLOWED_HOSTS": "shop.example.com",
    "CSRF_TRUSTED_ORIGINS": "https://shop.example.com",
    "SECRET_KEY": "zR2nQ9wX4kL8mT3bY6cH1jF5sD0gA2eU7iO4nB9xW3qZ8vC6rP1tM5hK0l",
}

_KEYS_TO_RESET = (
    "DEBUG",
    "SECRET_KEY",
    "ALLOWED_HOSTS",
    "CSRF_TRUSTED_ORIGINS",
    "REDIS_URL",
    "DB_ENGINE",
    "DJANGO_SETTINGS_MODULE",
)


def _import_settings(env_overrides):
    env = dict(os.environ)
    for key in _KEYS_TO_RESET:
        env.pop(key, None)
    env["DJANGO_SETTINGS_MODULE"] = "core.settings"
    env["PYTHONUTF8"] = "1"
    env.update(BASE_ENV)
    env.update(env_overrides)
    return subprocess.run(
        [sys.executable, "-c", "import core.settings; print('OK')"],
        cwd=BACKEND_DIR,
        env=env,
        capture_output=True,
        text=True,
    )


class ProductionGuardTest(SimpleTestCase):
    def test_valid_production_env_imports_ok(self):
        result = _import_settings({})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("OK", result.stdout)

    def test_weak_secret_key_blocked(self):
        result = _import_settings({"SECRET_KEY": "shortkey"})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("SECRET_KEY production", result.stderr)

    def test_missing_csrf_trusted_origins_blocked(self):
        result = _import_settings({"CSRF_TRUSTED_ORIGINS": ""})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("CSRF_TRUSTED_ORIGINS", result.stderr)

    def test_missing_redis_url_blocked(self):
        result = _import_settings({"REDIS_URL": ""})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("REDIS_URL", result.stderr)

    def test_unsupported_db_engine_blocked(self):
        result = _import_settings({"DB_ENGINE": "sqlite"})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DB_ENGINE", result.stderr)
