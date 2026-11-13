#!/usr/bin/env python3
"""Validate .env.production before deploy. Never prints secret values."""

import os
import sys

# Chỉ kiểm tra các biến bắt buộc; biến tùy chọn (Sentry, payment, social) để trống được.
REQUIRED = {
    "SECRET_KEY": lambda v: len(v) >= 50 and not v.startswith("django-insecure-"),
    "DEBUG": lambda v: v == "False",
    "ALLOWED_HOSTS": lambda v: bool(v) and "*" not in v,
    "CSRF_TRUSTED_ORIGINS": lambda v: v.startswith("https://"),
    "DB_HOST": lambda v: bool(v),
    "DB_NAME": lambda v: bool(v),
    "DB_USER": lambda v: bool(v),
    "DB_PASSWORD": lambda v: len(v) >= 16,
    "REDIS_URL": lambda v: v.startswith("redis://"),
    "EMAIL_HOST": lambda v: bool(v),
    "EMAIL_HOST_USER": lambda v: "@" in v,
    "EMAIL_HOST_PASSWORD": lambda v: len(v) >= 16,
    "DEFAULT_FROM_EMAIL": lambda v: "@" in v,
    "MEDIA_ROOT": lambda v: bool(v) and "frontend" not in v.replace("\\", "/"),
}

# Chuỗi còn sót từ file mẫu.
PLACEHOLDERS = (
    "THAY_BANG",
    "MAT_KHAU",
    "APP_PASSWORD",
    "_THAT",
    "YOUR_",
    "example.com",
)


def load_env(path):
    env = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def main():
    path = ".env.production"
    if not os.path.exists(path):
        print(f"[ERROR] {path} not found")
        return 1

    env = load_env(path)
    errors = [
        f"  [ERROR] {key}: missing or invalid"
        for key, check in REQUIRED.items()
        if not check(env.get(key, ""))
    ]
    for key, value in env.items():
        if any(p in value for p in PLACEHOLDERS):
            errors.append(f"  [ERROR] {key}: still a template placeholder")

    if errors:
        print("[ERROR] BLOCKERS - Must fix before deploy:")
        print("\n".join(errors))
        return 1

    print("[SUCCESS] .env.production PASSED - Ready for deploy")
    return 0


if __name__ == "__main__":
    sys.exit(main())
