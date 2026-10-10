import tempfile
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django_otp import DEVICE_ID_SESSION_KEY
from django_otp.plugins.otp_totp.models import TOTPDevice

from .models import Order, ShippingOrder


class ShippingLabelPrivacyTest(TestCase):
    def test_admin_download_requires_permission(self):
        with (
            tempfile.TemporaryDirectory(
                dir=Path(__file__).resolve().parents[2]
            ) as temp_dir,
            override_settings(MEDIA_ROOT=temp_dir),
        ):
            order = Order.objects.create(
                customer_name="Buyer", phone="0900000000", shipping_address="HCM"
            )
            shipping = ShippingOrder.objects.create(
                order=order, carrier="ghn", carrier_order_code="GHN-100"
            )
            shipping.shipping_label_pdf.save("label.pdf", ContentFile(b"%PDF-1.4 test"))
            url = reverse("admin:orders_shippingorder_label", args=[shipping.pk])
            self.assertEqual(self.client.get(url).status_code, 302)

            user = get_user_model().objects.create_superuser(
                username="admin-label",
                email="admin@example.test",
                password="StrongPass123!",
            )
            self.client.force_login(user)
            device = TOTPDevice.objects.create(user=user, name="admin", confirmed=True)
            self.assertEqual(self.client.get(url).status_code, 302)
            session = self.client.session
            session[DEVICE_ID_SESSION_KEY] = device.persistent_id
            session.save()
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(b"".join(response.streaming_content), b"%PDF-1.4 test")
            self.assertIn("attachment", response["Content-Disposition"])
            page = self.client.get(
                reverse("admin:orders_shippingorder_change", args=[shipping.pk])
            )
            self.assertContains(page, "Tải tem PDF")
            self.assertNotIn(shipping.shipping_label_pdf.url, page.content.decode())

    def test_proxies_block_direct_label_urls(self):
        root = Path(__file__).resolve().parents[2]
        self.assertIn(
            "handle /media/shipping_labels/*", (root / "Caddyfile.windows").read_text()
        )
        self.assertIn(
            "location ^~ /media/shipping_labels/", (root / "nginx.conf").read_text()
        )
