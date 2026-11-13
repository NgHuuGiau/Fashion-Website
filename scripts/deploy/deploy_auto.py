#!/usr/bin/env python3
"""
Auto-deployment script for HUUGIAU Fashion Website
Handles: SECRET_KEY generation, .env.production validation, migrations, collectstatic
Only prompts for values that CANNOT be auto-generated (DB, Redis, SMTP, Payment, Domain, Sentry)
"""

import os
import secrets
import subprocess
import sys


class DeployAutomation:
    def __init__(self):
        self.env_path = ".env.production"
        self.env_values = {}
        self.required_interactive = [
            ("DB_HOST", "SQL Server host/IP (e.g., 10.0.0.50)"),
            ("DB_USER", "Database username (least privilege)"),
            ("DB_PASSWORD", "Database password (16+ chars)"),
            ("DB_NAME", "Database name", "HUUGIAU_Fashion"),
            ("DB_DRIVER", "ODBC Driver version", "ODBC Driver 18 for SQL Server"),
            ("DB_PORT", "SQL Server port", "1433"),
            ("REDIS_URL", "Redis URL with password (redis://:pass@host:6379/0)"),
            ("EMAIL_HOST", "SMTP host (e.g., smtp.gmail.com)"),
            ("EMAIL_PORT", "SMTP port", "587"),
            ("EMAIL_HOST_USER", "SMTP username (email)", "no-reply@yourdomain.com"),
            ("EMAIL_HOST_PASSWORD", "SMTP app password (16+ chars)"),
            ("DEFAULT_FROM_EMAIL", "From email address", "no-reply@yourdomain.com"),
            (
                "ALLOWED_HOSTS",
                "Comma-separated domains (e.g., yourdomain.com,www.yourdomain.com)",
            ),
            (
                "CSRF_TRUSTED_ORIGINS",
                "HTTPS origins (e.g., https://yourdomain.com,https://www.yourdomain.com)",
            ),
            ("SENTRY_DSN", "Sentry DSN (optional, press Enter to skip)", ""),
            ("DOMAIN", "Your production domain (e.g., shop.yourdomain.com)"),
        ]

    def generate_secret_key(self):
        """Generate secure Django SECRET_KEY"""
        return secrets.token_urlsafe(50)

    def load_env(self):
        """Load existing .env.production"""
        if os.path.exists(self.env_path):
            with open(self.env_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        self.env_values[k.strip()] = v.strip().strip('"').strip("'")

    def save_env(self):
        """Save .env.production with all values"""
        # Read original to preserve comments and order
        lines = []
        if os.path.exists(self.env_path):
            with open(self.env_path, encoding="utf-8") as f:
                lines = f.readlines()

        # Update values in place, preserving comments
        updated_keys = set()
        new_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and "=" in line:
                key = line.split("=")[0].strip()
                if key in self.env_values:
                    new_lines.append(f"{key}={self.env_values[key]}\n")
                    updated_keys.add(key)
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)

        # Add missing keys at the end
        for key, value in self.env_values.items():
            if key not in updated_keys:
                new_lines.append(f"{key}={value}\n")

        with open(self.env_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print(f"[OK] Saved {self.env_path}")

    def generate_secret_key_if_needed(self):
        """Generate SECRET_KEY if placeholder"""
        current = self.env_values.get("SECRET_KEY", "")
        if not current or "THAY_BANG" in current or "django-insecure-" in current:
            new_key = self.generate_secret_key()
            self.env_values["SECRET_KEY"] = new_key
            print("[OK] Generated new SECRET_KEY")
        else:
            print("[OK] SECRET_KEY already set")

    def prompt_interactive(self):
        """Prompt for values that cannot be auto-generated"""
        print("\n" + "=" * 60)
        print("INTERACTIVE CONFIGURATION REQUIRED")
        print("=" * 60)
        print("Enter values for production (press Enter to keep current/default):\n")

        for key, prompt, *default in self.required_interactive:
            current = self.env_values.get(key, "")
            default_val = default[0] if default else ""
            display_current = current[:50] + "..." if len(current) > 50 else current
            if current and not any(
                p in current
                for p in [
                    "THAY_BANG",
                    "MAT_KHAU",
                    "APP_PASSWORD",
                    "THAT",
                    "shop.huugiau.vn",
                    "huugiau_app",
                    "huugiau",
                ]
            ):
                display_current = current
            else:
                display_current = ""

            prompt_text = f"{prompt}"
            if default_val:
                prompt_text += f" [{default_val}]"
            if display_current:
                prompt_text += f" (current: {display_current})"
            prompt_text += ": "

            while True:
                try:
                    user_input = input(prompt_text).strip()
                except (EOFError, KeyboardInterrupt):
                    print("\n[ERROR] Deployment cancelled")
                    sys.exit(1)

                if user_input:
                    self.env_values[key] = user_input
                    break
                elif default_val:
                    self.env_values[key] = default_val
                    break
                elif current and not any(
                    p in current
                    for p in [
                        "THAY_BANG",
                        "MAT_KHAU",
                        "APP_PASSWORD",
                        "THAT",
                        "shop.huugiau.vn",
                        "huugiau_app",
                        "huugiau",
                    ]
                ):
                    print(f"  [Keeping current: {current[:50]}...]")
                    break
                else:
                    print("  [ERROR] This field is required for production!")

    def auto_fill_known(self):
        """Auto-fill values we can determine"""
        self.env_values.setdefault("DEBUG", "False")
        self.env_values.setdefault("DB_ENGINE", "mssql")
        self.env_values.setdefault("DB_PORT", "1433")
        self.env_values.setdefault("DB_DRIVER", "ODBC Driver 18 for SQL Server")
        self.env_values.setdefault("DB_TRUSTED_CONNECTION", "False")
        self.env_values.setdefault(
            "DB_EXTRA_PARAMS", "TrustServerCertificate=yes;Encrypt=yes"
        )
        self.env_values.setdefault(
            "CELERY_BROKER_URL",
            self.env_values.get("REDIS_URL", "").replace("/0", "/1"),
        )
        self.env_values.setdefault(
            "CELERY_RESULT_BACKEND",
            self.env_values.get("REDIS_URL", "").replace("/0", "/2"),
        )
        self.env_values.setdefault("EMAIL_PORT", "587")
        self.env_values.setdefault("EMAIL_USE_TLS", "True")
        self.env_values.setdefault("BEHIND_PROXY", "True")
        self.env_values.setdefault("TRUSTED_PROXY", "True")
        self.env_values.setdefault("TRUSTED_PROXY_HOPS", "2")
        self.env_values.setdefault("SECURE_HSTS_SECONDS", "31536000")
        self.env_values.setdefault("CONN_MAX_AGE", "60")
        self.env_values.setdefault("COMPRESS_ENABLED", "True")
        self.env_values.setdefault("MEDIA_ROOT", "D:/FashionMedia")

    def validate_all(self):
        """Run validation script"""
        print("\n[INFO] Running validation...")
        result = subprocess.run(
            [sys.executable, "scripts/validate_env.py"],
            capture_output=True,
            text=True,
            check=False,
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return result.returncode == 0

    def run_verify_prod(self):
        """Run verify_prod script"""
        print("\n[INFO] Running verify_prod...")
        result = subprocess.run(
            [sys.executable, "scripts/verify_prod.py", "--fail-on-blocker"],
            capture_output=True,
            text=True,
            check=False,
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return result.returncode == 0

    def run_migrations(self):
        print("\n[INFO] Running migrations...")
        result = subprocess.run(
            [sys.executable, "manage.py", "migrate", "--noinput"],
            cwd="backend",
            env={**os.environ, "APP_ENV_FILE": self.env_path},
            capture_output=True,
            text=True,
            check=False,
        )
        print(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
        if result.stderr:
            print(result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr)
        return result.returncode == 0

    def run_collectstatic(self):
        print("\n[INFO] Collecting static files...")
        result = subprocess.run(
            [sys.executable, "manage.py", "collectstatic", "--noinput"],
            cwd="backend",
            env={**os.environ, "APP_ENV_FILE": self.env_path},
            capture_output=True,
            text=True,
            check=False,
        )
        print(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
        if result.stderr:
            print(result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr)
        return result.returncode == 0

    def run_deploy(self):
        print("=" * 60)
        print("HUUGIAU FASHION - PRODUCTION DEPLOYMENT AUTOMATION")
        print("=" * 60)

        # Step 1: Load existing env
        print("\n[1/7] Loading .env.production...")
        self.load_env()

        # Step 2: Generate SECRET_KEY
        print("\n[2/7] Generating SECRET_KEY...")
        self.generate_secret_key_if_needed()

        # Step 3: Auto-fill known values
        print("\n[3/7] Auto-filling known config...")
        self.auto_fill_known()

        # Step 4: Interactive prompts for required values
        print("\n[4/7] Interactive configuration...")
        self.prompt_interactive()

        # Step 5: Save + validate TRƯỚC khi động vào DB
        print("\n[5/7] Saving and validating .env.production...")
        self.save_env()
        if not self.validate_all():
            print("[ERROR] Validation failed!")
            return False
        if not self.run_verify_prod():
            print("[ERROR] verify_prod failed!")
            return False

        # Step 6: Run migrations
        print("\n[6/7] Running migrations...")
        if not self.run_migrations():
            print("[ERROR] Migrations failed!")
            return False

        # Step 7: Collect static
        print("\n[7/7] Collecting static files...")
        if not self.run_collectstatic():
            print("[ERROR] Collectstatic failed!")
            return False

        print("\n" + "=" * 60)
        print("✅ DEPLOYMENT PREPARATION COMPLETE!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Review .env.production one final time")
        print(
            "2. Deploy with: Caddy + Gunicorn/Uvicorn + Celery worker + Celery beat + Redis + SQL Server"
        )
        print("3. Monitor: /health/, /metrics/, Sentry, logs")
        return True


if __name__ == "__main__":
    deployer = DeployAutomation()
    try:
        success = deployer.run_deploy()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n[INFO] Deployment cancelled by user")
        sys.exit(1)
    except Exception as e:  # noqa: BLE001 - top-level guard for a CLI script
        print(f"[ERROR] {e}")
        sys.exit(1)
