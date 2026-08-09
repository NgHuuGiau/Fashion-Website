import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def load_env_file(env_path):
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ[key.strip()] = value.strip().strip('"').strip("'")



def env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}



def env_list(name, default=None):
    value = os.getenv(name)
    if not value:
        return default or []
    return [item.strip() for item in value.split(",") if item.strip()]


load_env_file(BASE_DIR / ".env")


_secret_key = os.getenv("SECRET_KEY")
if not _secret_key:
    raise RuntimeError(
        "SECRET_KEY chưa được thiết lập. "
        "Thêm SECRET_KEY=your-secret-key vào file .env ở thư mục gốc."
    )
SECRET_KEY = _secret_key
DEBUG = env_bool("DEBUG", False)
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", ["127.0.0.1", "localhost", "testserver"])
CSRF_TRUSTED_ORIGINS = [
    "https://localhost:8000",
    "https://127.0.0.1:8000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "core",
    "django.contrib.staticfiles",
    "compressor",
    "django_extensions",
    "products",
    "users",
    "orders",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "core.middleware.CSPMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "users.middleware.VisitorTrackingMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "frontend/templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "builtins": [
                "products.templatetags.shop_format",
            ],
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "orders.context_processors.cart_info",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

DB_ENGINE = os.getenv("DB_ENGINE", "mssql").lower()

# SQL Server is the only supported database. Do not silently fall back.
if DB_ENGINE not in {"mssql", "sqlserver"}:
    from django.core.exceptions import ImproperlyConfigured

    raise ImproperlyConfigured(
        "Only SQL Server is supported (set DB_ENGINE=mssql)."
    )

_db_options = {
    "driver": os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server"),
    "trusted_connection": env_bool("DB_TRUSTED_CONNECTION", True),
    "extra_params": os.getenv(
        "DB_EXTRA_PARAMS", "TrustServerCertificate=yes;Encrypt=yes"
    ),
}

DATABASES = {
    "default": {
        "ENGINE": "mssql",
        "NAME": os.getenv("DB_NAME", "HUUGIAU_Fashion"),
        "HOST": os.getenv("DB_HOST", "."),
        "PORT": os.getenv("DB_PORT", ""),
        "OPTIONS": _db_options,
    }
}

if os.getenv("DB_USER"):
    # SQL auth (e.g. CI). Leave unset for Windows/trusted auth locally.
    DATABASES["default"]["USER"] = os.getenv("DB_USER")
    DATABASES["default"]["PASSWORD"] = os.getenv("DB_PASSWORD", "")

LANGUAGE_CODE = "vi"
TIME_ZONE = "Asia/Ho_Chi_Minh"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "frontend/static"]

COMPRESS_ENABLED = env_bool("COMPRESS_ENABLED", not DEBUG)
COMPRESS_URL = STATIC_URL
COMPRESS_ROOT = BASE_DIR / "frontend/static"
COMPRESS_CSS_FILTERS = ["compressor.filters.cssmin.rCSSMinFilter"]
COMPRESS_JS_FILTERS = ["compressor.filters.jsmin.rJSMinFilter"]
COMPRESS_OUTPUT_DIR = "CACHE"
COMPRESS_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
if not DEBUG:
    COMPRESS_OFFLINE = True
    COMPRESS_OFFLINE_CONTEXT = {}
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "frontend/static/images"

TRUSTED_PROXY = env_bool("TRUSTED_PROXY", False)
LOGIN_URL = "users:login"
LOGIN_REDIRECT_URL = "products:product_list"
LOGOUT_REDIRECT_URL = "products:product_list"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

_redis_url = os.getenv("REDIS_URL", "")
if _redis_url:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": _redis_url,
            "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        }
    }
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
else:
    # WARNING: LocMemCache is per-process and NOT suitable for production with multiple workers.
    # Set REDIS_URL in .env for production to enable cross-worker rate limiting and caching.
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "huugiau-cache",
        }
    }

SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", False)
SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", False)
CSRF_COOKIE_SECURE = env_bool("CSRF_COOKIE_SECURE", False)
SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", False)
SECURE_HSTS_PRELOAD = env_bool("SECURE_HSTS_PRELOAD", False)


if not DEBUG:
    if os.getenv("ALLOWED_HOSTS", "").strip() in ("", "*"):
        import warnings
        warnings.warn("ALLOWED_HOSTS không được để trống hoặc '*' khi DEBUG=False. Đặt giá trị cụ thể trong .env")

    SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", True)
    SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", True)
    CSRF_COOKIE_SECURE = env_bool("CSRF_COOKIE_SECURE", True)
    SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "31536000"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", True)
    SECURE_HSTS_PRELOAD = env_bool("SECURE_HSTS_PRELOAD", True)
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG' if (DEBUG and env_bool("ENABLE_SQL_LOGGING", False)) else 'WARNING',
        },
    },
}
