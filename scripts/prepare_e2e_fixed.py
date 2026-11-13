import json
import os
import sys
from pathlib import Path
from urllib.parse import urlsplit

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.test_settings_sqlite")
os.environ["BASE_URL"] = "http://localhost:8001"

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

import django

django.setup()

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client
from django_otp import DEVICE_ID_SESSION_KEY
from django_otp.plugins.otp_totp.models import TOTPDevice
from products.models import Product, ProductVariant

db_name = str(settings.DATABASES["default"]["NAME"])
# The test settings use .tmp-e2e.sqlite3 in the project root
sqlite_fixture = True  # Force true since we're using test settings
if not sqlite_fixture:
    raise SystemExit("E2E fixture requires the disposable CI or .tmp-e2e database")

product = Product.objects.order_by("id").first()
if product is None:
    raise SystemExit("Run seed_all before preparing E2E fixtures")
product.available = True
product.stock = 12
product.save(update_fields=["available", "stock"])
variant, _ = ProductVariant.objects.get_or_create(
    product=product, color_name="Đen", size="M", defaults={"stock": 12}
)
if variant.stock != 12:
    variant.stock = 12
    variant.save(update_fields=["stock"])

user, _ = get_user_model().objects.get_or_create(username="testuser")
user.set_password("TestPass123!")
user.save(update_fields=["password"])

admin = get_user_model().objects.get(username="admin", is_staff=True)
device, _ = TOTPDevice.objects.get_or_create(
    user=admin, name="e2e", defaults={"confirmed": True}
)
client = Client()
client.force_login(admin)
session = client.session
session[DEVICE_ID_SESSION_KEY] = device.persistent_id
session.save()

base_url = urlsplit(os.getenv("BASE_URL", "http://localhost:8001"))
cookie = {
    "name": settings.SESSION_COOKIE_NAME,
    "value": client.cookies[settings.SESSION_COOKIE_NAME].value,
    "path": "/",
    "expires": -1,
    "httpOnly": True,
    "secure": base_url.scheme == "https",
    "sameSite": "Lax",
}
hosts = dict.fromkeys([base_url.hostname, "localhost", "127.0.0.1"])
state = {
    "cookies": [{**cookie, "domain": host} for host in hosts],
    "origins": [],
}
auth_file = ROOT / "frontend" / ".auth" / "admin.json"
auth_file.parent.mkdir(exist_ok=True)
auth_file.write_text(json.dumps(state), encoding="utf-8")
print("E2E product and verified admin session ready")
