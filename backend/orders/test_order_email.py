from django.core import mail
from django.test import TestCase, override_settings

from .models import Order
from .services.order_email import send_order_email


def make_order():
    return Order.objects.create(
        customer_name="Khach",
        customer_email="khach@example.test",
        phone="0900000000",
        shipping_address="HCM",
        payment_method="cod",
        total_amount=100000,
    )


class OrderEmailTest(TestCase):
    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        EMAIL_HOST="",
    )
    def test_sends_with_console_backend_without_smtp_host(self):
        self.assertTrue(send_order_email(make_order(), event="created"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["khach@example.test"])

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend",
        EMAIL_HOST="",
    )
    def test_skips_smtp_backend_without_host(self):
        self.assertFalse(send_order_email(make_order(), event="created"))
        self.assertEqual(len(mail.outbox), 0)
