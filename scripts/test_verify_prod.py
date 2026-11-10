import contextlib
import io
import os
import unittest
from unittest.mock import patch

from scripts import verify_prod


class VerifyProdTest(unittest.TestCase):
    def setUp(self):
        verify_prod.FAIL.clear()
        self.env = {
            "SECRET_KEY": "aB3$x" * 12,
            "DEBUG": "False",
            "ALLOWED_HOSTS": "shop.test",
            "CSRF_TRUSTED_ORIGINS": "https://shop.test",
            "DB_HOST": "db.test",
            "DB_USER": "app",
            "DB_PASSWORD": "secret",
            "REDIS_URL": "redis://redis.test:6379/0",
            "EMAIL_HOST": "smtp.test",
            "EMAIL_HOST_USER": "mailer",
            "DEFAULT_FROM_EMAIL": "no-reply@shop.test",
            "PUBLIC_CONTACTS_VERIFIED": "True",
            "BEHIND_PROXY": "True",
            "TRUSTED_PROXY": "True",
            "SECURE_SSL_REDIRECT": "True",
            "MEDIA_ROOT": "D:/FashionMedia",
        }

    def test_requires_verified_support_channel(self):
        with (
            patch.dict(os.environ, self.env, clear=True),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            self.assertEqual(verify_prod.check(), 1)
        self.assertTrue(
            any("SUPPORT_EMAIL/HOTLINE" in item for item in verify_prod.FAIL)
        )

    def test_accepts_configured_support_email(self):
        self.env["SUPPORT_EMAIL"] = "support@shop.test"
        with (
            patch.dict(os.environ, self.env, clear=True),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            self.assertEqual(verify_prod.check(), 0)

    def test_accepts_hotline_without_email(self):
        self.env["HOTLINE"] = "0912345678"
        with (
            patch.dict(os.environ, self.env, clear=True),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            self.assertEqual(verify_prod.check(), 0)

    def test_rejects_placeholder_support_email(self):
        self.env["SUPPORT_EMAIL"] = "support@shop.example.com"
        with (
            patch.dict(os.environ, self.env, clear=True),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            self.assertEqual(verify_prod.check(), 1)

    def test_requires_explicit_public_contact_confirmation(self):
        self.env["SUPPORT_EMAIL"] = "support@shop.test"
        self.env["PUBLIC_CONTACTS_VERIFIED"] = "False"
        with (
            patch.dict(os.environ, self.env, clear=True),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            self.assertEqual(verify_prod.check(), 1)


if __name__ == "__main__":
    unittest.main()
