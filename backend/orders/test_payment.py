import hashlib
import json
from datetime import timedelta
from unittest import mock
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from products.models import Category, Product, ProductVariant
from users.test_client import VerifiedStaffClient
from .models import Order, OrderItem, RefundRecord
from .vnpay import _secure_hash


def _payment_token(order_id):
    raw = f"bank:{order_id}:qr:{settings.SECRET_KEY}"
    return hashlib.sha256(raw.encode()).hexdigest()


VNPAY_CONFIG = {
    "DEBUG": True,
    "VNPAY_URL": "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html",
    "VNPAY_TMN_CODE": "TESTTMN",
    "VNPAY_HASH_SECRET": "tests3cret",
}


@override_settings(
    BANK_TRANSFER_ENABLED=True,
    SHOP_BANK_CODE="VCB",
    SHOP_BANK_ACCOUNT="12345678",
    SHOP_ACCOUNT_NAME="HUUGIAU TEST",
)
class BankPaymentMobileTest(TestCase):
    def setUp(self):
        from django.core.cache import cache

        cache.clear()
        self.user = User.objects.create_user(
            username="buyer", password="StrongPass123!"
        )
        self.category_pk = Category.objects.create(name="Phu kien", slug="phu-kien")
        self.product = Product.objects.create(
            category=self.category_pk,
            name="Tui test",
            slug="tui-test",
            price=300000,
            stock=10,
            available=True,
        )
        self.client.login(username="buyer", password="StrongPass123!")
        self.client.post(
            reverse("orders:cart_add", kwargs={"product_id": self.product.id}),
            {"quantity": 1},
        )
        self.client.post(
            reverse("orders:checkout"),
            {
                "customer_name": "Test",
                "phone": "0909000000",
                "shipping_address": "HCM",
                "payment_method": "bank",
                "bank_code": "VCB",
            },
        )
        self.order = Order.objects.first()
        self.token = _payment_token(self.order.id)
        self.mobile_url = reverse(
            "orders:bank_payment_mobile",
            kwargs={"token": self.token, "order_id": self.order.id},
        )

    def test_mobile_token_mismatch_404(self):
        url = reverse(
            "orders:bank_payment_mobile",
            kwargs={"token": "invalid", "order_id": self.order.id},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_mobile_get_active(self):
        response = self.client.get(self.mobile_url)
        self.assertEqual(response.status_code, 200)

    def test_mobile_get_expired_after_timeout(self):
        Order.objects.filter(id=self.order.id).update(
            created_at=timezone.now() - timedelta(minutes=16)
        )
        response = self.client.get(self.mobile_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("expired", response.context)

    def test_mobile_post_confirm_success(self):
        response = self.client.post(self.mobile_url, {"action": "confirm"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["verification_pending"])
        self.order.refresh_from_db()
        self.assertFalse(self.order.is_paid)

    def test_mobile_post_cancel_success(self):
        response = self.client.post(self.mobile_url, {"action": "cancel"})
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "cancelled")


class BankTransferConfigurationTest(TestCase):
    @override_settings(
        BANK_TRANSFER_ENABLED=False,
        SHOP_BANK_ACCOUNT="",
        SHOP_ACCOUNT_NAME="",
    )
    def test_checkout_hides_bank_transfer_when_not_configured(self):
        from .forms import CheckoutForm
        from .views.cart import build_vietqr_url

        choices = dict(CheckoutForm().fields["payment_method"].choices)
        self.assertNotIn("bank", choices)
        self.assertNotIn("vnpay", choices)
        self.assertNotIn("bank_code", CheckoutForm().fields)
        self.assertEqual(build_vietqr_url(10000, "DH1"), "")

    @override_settings(
        DEBUG=True,
        VNPAY_TMN_CODE="TESTTMN",
        VNPAY_HASH_SECRET="test-secret",
        VNPAY_URL="https://sandbox.vnpayment.vn/paymentv2/vpcpay.html",
    )
    def test_checkout_shows_vnpay_only_when_gateway_is_configured(self):
        from .forms import CheckoutForm

        self.assertIn("vnpay", dict(CheckoutForm().fields["payment_method"].choices))

    @override_settings(
        DEBUG=False,
        VNPAY_TMN_CODE="TESTTMN",
        VNPAY_HASH_SECRET="test-secret",
        VNPAY_URL="https://sandbox.vnpayment.vn/paymentv2/vpcpay.html",
    )
    def test_production_rejects_vnpay_sandbox(self):
        from .vnpay import is_configured

        self.assertFalse(is_configured())

    @override_settings(
        DEBUG=False,
        VNPAY_TMN_CODE="TESTTMN",
        VNPAY_HASH_SECRET="test-secret",
        VNPAY_URL="https://pay.vnpayment.vn/paymentv2/vpcpay.html",
    )
    def test_production_accepts_https_vnpay_gateway(self):
        from .vnpay import is_configured

        self.assertTrue(is_configured())

    @override_settings(
        BANK_TRANSFER_ENABLED=True,
        SHOP_BANK_CODE="ICB",
        SHOP_BANK_ACCOUNT="",
        SHOP_ACCOUNT_NAME="",
    )
    def test_bank_transfer_requires_account_details_even_if_enabled(self):
        from .constants import bank_transfer_is_enabled
        from .forms import CheckoutForm

        self.assertFalse(bank_transfer_is_enabled())
        self.assertNotIn("bank", dict(CheckoutForm().fields["payment_method"].choices))

    @override_settings(
        BANK_TRANSFER_ENABLED=True,
        SHOP_BANK_CODE="UNKNOWN",
        SHOP_BANK_ACCOUNT="12345678",
        SHOP_ACCOUNT_NAME="HUUGIAU TEST",
    )
    def test_bank_transfer_rejects_unknown_shop_bank_code(self):
        from .constants import bank_transfer_is_enabled
        from .forms import CheckoutForm

        self.assertFalse(bank_transfer_is_enabled())
        self.assertNotIn("bank", dict(CheckoutForm().fields["payment_method"].choices))

    @override_settings(
        BANK_TRANSFER_ENABLED=False,
        SHOP_BANK_ACCOUNT="",
        SHOP_ACCOUNT_NAME="",
    )
    def test_existing_bank_order_shows_disabled_notice_without_payment_details(self):
        user = User.objects.create_user(
            username="bank-disabled", password="StrongPass123!"
        )
        self.client.login(username="bank-disabled", password="StrongPass123!")
        order = Order.objects.create(
            user=user,
            customer_name="Buyer",
            phone="0909000000",
            shipping_address="HCM",
            payment_method="bank",
            total_amount=100000,
            status="processing",
            is_paid=False,
        )

        response = self.client.get(
            reverse("orders:bank_payment_waiting", kwargs={"order_id": order.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Chuyển khoản chưa khả dụng")
        self.assertNotContains(response, "1234567890")

    @override_settings(
        BANK_TRANSFER_ENABLED=True,
        SHOP_BANK_CODE="ICB",
        SHOP_BANK_ACCOUNT="12345678",
        SHOP_ACCOUNT_NAME="HUUGIAU TEST",
    )
    def test_configured_bank_transfer_builds_qr_with_configured_account(self):
        from .views.cart import build_vietqr_url

        self.assertIn(
            "970415-12345678-compact2.png",
            build_vietqr_url(10000, "DH1"),
        )


class BankPaymentStatusTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="buyer", password="StrongPass123!"
        )
        self.client.login(username="buyer", password="StrongPass123!")

    def test_status_waiting(self):
        order = Order.objects.create(
            user=self.user,
            customer_name="T",
            phone="0909",
            shipping_address="HCM",
            payment_method="bank",
            total_amount=100000,
            status="processing",
            is_paid=False,
        )
        response = self.client.get(
            reverse("orders:bank_payment_status", kwargs={"order_id": order.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["state"], "waiting")

    def test_status_success(self):
        order = Order.objects.create(
            user=self.user,
            customer_name="T",
            phone="0909",
            shipping_address="HCM",
            payment_method="bank",
            total_amount=100000,
            status="processing",
            is_paid=True,
        )
        response = self.client.get(
            reverse("orders:bank_payment_status", kwargs={"order_id": order.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["state"], "success")

    def test_status_failed_when_cancelled(self):
        order = Order.objects.create(
            user=self.user,
            customer_name="T",
            phone="0909",
            shipping_address="HCM",
            payment_method="bank",
            total_amount=100000,
            status="cancelled",
            is_paid=False,
        )
        response = self.client.get(
            reverse("orders:bank_payment_status", kwargs={"order_id": order.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["state"], "failed")


class PaymentEdgeBranchesTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="payer", password="StrongPass123!"
        )
        self.category_pk = Category.objects.create(name="Phu kien", slug="phu-kien")
        self.product = Product.objects.create(
            category=self.category_pk,
            name="Vi test",
            slug="vi-test",
            price=150000,
            stock=10,
            available=True,
        )
        self.client.login(username="payer", password="StrongPass123!")

    def _cod_order(self, **kw):
        defaults = dict(
            user=self.user,
            customer_name="T",
            phone="0909",
            shipping_address="HCM",
            payment_method="cod",
            total_amount=150000,
            subtotal_amount=150000,
            shipping_fee=30000,
            discount_amount=0,
            status="pending",
            is_paid=False,
        )
        defaults.update(kw)
        return Order.objects.create(**defaults)

    def test_order_success_expired_bank_redirects_failed(self):
        order = Order.objects.create(
            user=self.user,
            customer_name="T",
            phone="0909",
            shipping_address="HCM",
            payment_method="bank",
            bank_code="VCB",
            status="processing",
            is_paid=False,
            total_amount=150000,
        )
        Order.objects.filter(id=order.id).update(
            created_at=timezone.now() - timedelta(minutes=16)
        )
        response = self.client.get(
            reverse("orders:order_success", kwargs={"order_id": order.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, reverse("orders:order_failed", kwargs={"order_id": order.id})
        )

    def test_order_success_paid_cod_renders(self):
        order = self._cod_order(is_paid=True)
        response = self.client.get(
            reverse("orders:order_success", kwargs={"order_id": order.id})
        )
        self.assertEqual(response.status_code, 200)

    def test_bank_payment_confirm_non_bank_order(self):
        order = self._cod_order()
        response = self.client.post(
            reverse("orders:bank_payment_confirm", kwargs={"order_id": order.id}),
            {"token": _payment_token(order.id)},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, reverse("orders:order_success", kwargs={"order_id": order.id})
        )
        order.refresh_from_db()
        self.assertFalse(order.is_paid)

    def test_bank_payment_confirm_expired_order(self):
        order = Order.objects.create(
            user=self.user,
            customer_name="T",
            phone="0909",
            shipping_address="HCM",
            payment_method="bank",
            bank_code="VCB",
            status="processing",
            is_paid=False,
            total_amount=150000,
        )
        Order.objects.filter(id=order.id).update(
            created_at=timezone.now() - timedelta(minutes=16)
        )
        response = self.client.post(
            reverse("orders:bank_payment_confirm", kwargs={"order_id": order.id}),
            {"token": _payment_token(order.id)},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, reverse("orders:order_failed", kwargs={"order_id": order.id})
        )

    def test_bank_payment_confirm_token_mismatch(self):
        order = Order.objects.create(
            user=self.user,
            customer_name="T",
            phone="0909",
            shipping_address="HCM",
            payment_method="bank",
            bank_code="VCB",
            status="processing",
            is_paid=False,
            total_amount=150000,
        )
        response = self.client.post(
            reverse("orders:bank_payment_confirm", kwargs={"order_id": order.id}),
            {"token": "wrong-token"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("orders:bank_payment_waiting", kwargs={"order_id": order.id}),
        )
        order.refresh_from_db()
        self.assertFalse(order.is_paid)

    def test_bank_payment_cancel_already_cancelled(self):
        order = Order.objects.create(
            user=self.user,
            customer_name="T",
            phone="0909",
            shipping_address="HCM",
            payment_method="bank",
            bank_code="VCB",
            status="cancelled",
            is_paid=False,
            total_amount=150000,
        )
        response = self.client.post(
            reverse("orders:bank_payment_cancel", kwargs={"order_id": order.id})
        )
        self.assertEqual(response.status_code, 302)

    def test_bank_payment_cancel_non_bank(self):
        order = self._cod_order()
        response = self.client.post(
            reverse("orders:bank_payment_cancel", kwargs={"order_id": order.id})
        )
        self.assertEqual(response.status_code, 302)

    def test_order_failed_with_reason_param(self):
        order = self._cod_order()
        response = self.client.get(
            reverse("orders:order_failed", kwargs={"order_id": order.id}),
            {"reason": "custom"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["failed_reason"], "Đã hủy thanh toán")

    def test_order_failed_with_expired_note(self):
        order = self._cod_order(note="[AUTO_TIMEOUT_15_MIN]")
        response = self.client.get(
            reverse("orders:order_failed", kwargs={"order_id": order.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["failed_reason"], "Quá 15 phút chưa thanh toán"
        )

    def test_bank_payment_waiting_non_bank_redirects(self):
        order = self._cod_order()
        response = self.client.get(
            reverse("orders:bank_payment_waiting", kwargs={"order_id": order.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, reverse("orders:order_success", kwargs={"order_id": order.id})
        )

    def test_bank_payment_waiting_paid_redirects_success(self):
        order = Order.objects.create(
            user=self.user,
            customer_name="T",
            phone="0909",
            shipping_address="HCM",
            payment_method="bank",
            bank_code="VCB",
            status="processing",
            is_paid=True,
            total_amount=150000,
        )
        response = self.client.get(
            reverse("orders:bank_payment_waiting", kwargs={"order_id": order.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, reverse("orders:order_success", kwargs={"order_id": order.id})
        )


@override_settings(
    BANK_TRANSFER_ENABLED=True,
    SHOP_BANK_CODE="VCB",
    SHOP_BANK_ACCOUNT="12345678",
    SHOP_ACCOUNT_NAME="HUUGIAU TEST",
)
class PaymentExtraBranchesTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="payextra", password="StrongPass123!"
        )
        self.client.login(username="payextra", password="StrongPass123!")

    def _bank_order(self, **kw):
        defaults = dict(
            user=self.user,
            customer_name="T",
            phone="0909",
            shipping_address="HCM",
            payment_method="bank",
            bank_code="VCB",
            total_amount=100000,
            status="processing",
            is_paid=False,
        )
        defaults.update(kw)
        return Order.objects.create(**defaults)

    def _cod_order(self, **kw):
        defaults = dict(
            user=self.user,
            customer_name="T",
            phone="0909",
            shipping_address="HCM",
            payment_method="cod",
            total_amount=100000,
            status="pending",
            is_paid=False,
        )
        defaults.update(kw)
        return Order.objects.create(**defaults)

    def test_order_success_unpaid_bank_redirects_waiting(self):
        order = self._bank_order()
        response = self.client.get(
            reverse("orders:order_success", kwargs={"order_id": order.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("orders:bank_payment_waiting", kwargs={"order_id": order.id}),
        )

    def test_order_success_paid_bank_renders_with_qr(self):
        order = self._bank_order(is_paid=True)
        response = self.client.get(
            reverse("orders:order_success", kwargs={"order_id": order.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["qr_url"])

    def test_bank_waiting_cancelled_redirects_failed(self):
        order = self._bank_order(status="cancelled")
        response = self.client.get(
            reverse("orders:bank_payment_waiting", kwargs={"order_id": order.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, reverse("orders:order_failed", kwargs={"order_id": order.id})
        )

    def test_bank_confirm_cancelled_redirects_success(self):
        order = self._bank_order(status="cancelled")
        response = self.client.post(
            reverse("orders:bank_payment_confirm", kwargs={"order_id": order.id}),
            {"token": _payment_token(order.id)},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, reverse("orders:order_success", kwargs={"order_id": order.id})
        )

    def test_bank_confirm_already_paid(self):
        order = self._bank_order(is_paid=True)
        response = self.client.post(
            reverse("orders:bank_payment_confirm", kwargs={"order_id": order.id}),
            {"token": _payment_token(order.id)},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, reverse("orders:order_success", kwargs={"order_id": order.id})
        )

    def test_bank_cancel_already_paid(self):
        order = self._bank_order(is_paid=True)
        response = self.client.post(
            reverse("orders:bank_payment_cancel", kwargs={"order_id": order.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, reverse("orders:order_success", kwargs={"order_id": order.id})
        )

    def _mobile_url(self, order):
        return reverse(
            "orders:bank_payment_mobile",
            kwargs={"token": _payment_token(order.id), "order_id": order.id},
        )

    def test_mobile_confirm_expired(self):
        order = self._bank_order()
        Order.objects.filter(id=order.id).update(
            created_at=timezone.now() - timedelta(minutes=16)
        )
        response = self.client.post(self._mobile_url(order), {"action": "confirm"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["expired"])

    def test_mobile_confirm_cancelled(self):
        order = self._bank_order(status="cancelled")
        response = self.client.post(self._mobile_url(order), {"action": "confirm"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["cancelled"])

    def test_mobile_confirm_already_paid(self):
        order = self._bank_order(is_paid=True)
        response = self.client.post(self._mobile_url(order), {"action": "confirm"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["just_paid"])

    def test_mobile_cancel_already_paid(self):
        order = self._bank_order(is_paid=True)
        response = self.client.post(self._mobile_url(order), {"action": "cancel"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["paid"])

    def test_mobile_cancel_expired(self):
        order = self._bank_order()
        Order.objects.filter(id=order.id).update(
            created_at=timezone.now() - timedelta(minutes=16)
        )
        response = self.client.post(self._mobile_url(order), {"action": "cancel"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["expired"])

    def test_mobile_get_already_paid(self):
        order = self._bank_order(is_paid=True)
        response = self.client.get(self._mobile_url(order))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["paid"])

    def test_mobile_get_cancelled(self):
        order = self._bank_order(status="cancelled")
        response = self.client.get(self._mobile_url(order))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["cancelled"])

    def test_guest_can_view_own_recent_order(self):
        self.client.logout()
        order = self._cod_order(user=None, status="pending", is_paid=False)
        session = self.client.session
        session["guest_orders"] = [order.id]
        session.save()
        response = self.client.get(
            reverse("orders:order_success", kwargs={"order_id": order.id})
        )
        self.assertEqual(response.status_code, 200)

    def test_guest_cannot_view_unknown_order(self):
        self.client.logout()
        order = self._cod_order(user=None, status="pending", is_paid=False)
        response = self.client.get(
            reverse("orders:order_success", kwargs={"order_id": order.id})
        )
        self.assertEqual(response.status_code, 404)

    def test_guest_order_success_blocks_other_users_orders(self):
        self.client.logout()
        order = self._cod_order(status="pending", is_paid=False)
        session = self.client.session
        session["guest_orders"] = [order.id]
        session.save()
        response = self.client.get(
            reverse("orders:order_success", kwargs={"order_id": order.id})
        )
        self.assertEqual(response.status_code, 404)


@override_settings(**VNPAY_CONFIG)
class VNPayTest(TestCase):
    client_class = VerifiedStaffClient

    def setUp(self):
        self.user = User.objects.create_user(
            username="buyer", password="StrongPass123!"
        )
        self.category = Category.objects.create(name="Ao", slug="ao")
        self.product = Product.objects.create(
            category=self.category,
            name="Ao vnpay",
            slug="ao-vnpay",
            price=300000,
            stock=5,
            available=True,
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            color_name="Den",
            color_code="#111111",
            size="L",
            stock=3,
            is_active=True,
        )
        self.order = Order.objects.create(
            user=self.user,
            customer_name="T",
            phone="0909",
            shipping_address="HCM",
            payment_method="vnpay",
            total_amount=300000,
            status="processing",
            is_paid=False,
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            variant=self.variant,
            quantity=2,
            price=300000,
        )

    def _signed(self, **extra):
        params = {
            "vnp_Version": "2.1.0",
            "vnp_Command": "pay",
            "vnp_TmnCode": "TESTTMN",
            "vnp_Amount": "30000000",
            "vnp_TxnRef": str(self.order.id),
            "vnp_ResponseCode": "00",
            "vnp_TransactionStatus": "00",
            "vnp_TransactionNo": "987654321",
            "vnp_OrderInfo": "Thanh toan don hang test",
        }
        params.update(extra)
        signed = params.copy()
        signed["vnp_SecureHash"] = _secure_hash(params)
        return signed

    def test_payment_redirects_to_gateway_when_configured(self):
        self.client.login(username="buyer", password="StrongPass123!")
        response = self.client.get(
            reverse("orders:vnpay_payment", kwargs={"order_id": self.order.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("sandbox.vnpayment.vn", response.url)

    def test_payment_unconfigured_redirects_success(self):
        with override_settings(VNPAY_TMN_CODE="", VNPAY_HASH_SECRET=""):
            self.client.login(username="buyer", password="StrongPass123!")
            response = self.client.get(
                reverse("orders:vnpay_payment", kwargs={"order_id": self.order.id})
            )
            self.assertRedirects(
                response,
                reverse("orders:order_success", kwargs={"order_id": self.order.id}),
            )

    def test_payment_rejects_non_vnpay_order(self):
        self.order.payment_method = "cod"
        self.order.save(update_fields=["payment_method"])
        self.client.login(username="buyer", password="StrongPass123!")
        response = self.client.get(
            reverse("orders:vnpay_payment", kwargs={"order_id": self.order.id})
        )
        self.assertRedirects(
            response,
            reverse("orders:order_success", kwargs={"order_id": self.order.id}),
        )

    def test_payment_rejects_foreign_order(self):
        other = User.objects.create_user(
            username="otheruser", password="StrongPass123!"
        )
        order = Order.objects.create(
            user=other,
            customer_name="T",
            phone="0909",
            shipping_address="HCM",
            payment_method="vnpay",
            total_amount=100000,
            status="processing",
            is_paid=False,
        )
        self.client.login(username="buyer", password="StrongPass123!")
        response = self.client.get(
            reverse("orders:vnpay_payment", kwargs={"order_id": order.id})
        )
        self.assertEqual(response.status_code, 404)

    def test_return_success_marks_paid(self):
        params = self._signed()
        response = self.client.get(reverse("orders:vnpay_return"), params)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("orders:order_success", kwargs={"order_id": self.order.id}),
        )
        self.order.refresh_from_db()
        self.assertTrue(self.order.is_paid)
        self.assertEqual(self.order.status, "processing")
        self.assertEqual(self.order.vnpay_transaction_id, "987654321")

    def test_late_success_callback_does_not_reopen_cancelled_order_or_reserve_stock(
        self,
    ):
        self.order.status = "cancelled"
        self.order.save(update_fields=["status"])
        self.variant.stock = 5
        self.variant.save(update_fields=["stock"])
        response = self.client.get(reverse("orders:vnpay_return"), self._signed())
        self.assertEqual(response.status_code, 302)
        self.order.refresh_from_db()
        self.assertTrue(self.order.is_paid)
        self.assertEqual(self.order.status, "cancelled")
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock, 5)

    def test_return_success_idempotent_when_already_paid(self):
        self.order.is_paid = True
        self.order.save(update_fields=["is_paid"])
        params = self._signed(vnp_ResponseCode="99")
        response = self.client.get(reverse("orders:vnpay_return"), params)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("orders:order_success", kwargs={"order_id": self.order.id}),
        )

    def test_return_failure_cancels_and_restores_stock(self):
        params = self._signed(vnp_ResponseCode="24", vnp_TransactionStatus="24")
        response = self.client.get(reverse("orders:vnpay_return"), params)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("orders:order_failed", kwargs={"order_id": self.order.id}),
        )
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "cancelled")
        self.variant.refresh_from_db()
        self.product.refresh_from_db()
        self.assertEqual(self.variant.stock, 5)
        self.assertEqual(self.product.stock, 5)

    def test_return_bad_signature_rejected(self):
        params = self._signed(vnp_ResponseCode="00")
        params["vnp_SecureHash"] = "deadbeef"
        response = self.client.get(reverse("orders:vnpay_return"), params)
        self.assertEqual(response.status_code, 302)
        self.order.refresh_from_db()
        self.assertFalse(self.order.is_paid)
        self.assertEqual(self.order.status, "processing")

    def test_return_unknown_order_redirects_my_orders(self):
        params = self._signed(vnp_TxnRef="99999")
        response = self.client.get(reverse("orders:vnpay_return"), params)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:my_orders"))

    def test_ipn_success_confirms(self):
        params = self._signed()
        response = self.client.get(reverse("orders:vnpay_ipn"), params)
        self.assertEqual(response.json()["RspCode"], "00")
        self.order.refresh_from_db()
        self.assertTrue(self.order.is_paid)
        self.assertEqual(self.order.vnpay_transaction_id, "987654321")

    @override_settings(VNPAY_REFUND_URL="https://merchant.test/refund")
    @mock.patch(
        "orders.vnpay.refund_transaction",
        return_value={
            "success": True,
            "response_code": "00",
            "data": {"vnp_ResponseCode": "00"},
        },
    )
    def test_refund_is_idempotent_and_tracks_amount(self, refund_mock):
        User.objects.create_user(
            username="refund_staff", password="StrongPass123!", is_staff=True
        )
        self.client.login(username="refund_staff", password="StrongPass123!")
        self.order.is_paid = True
        self.order.vnpay_transaction_id = "987654321"
        self.order.save(update_fields=["is_paid", "vnpay_transaction_id"])
        url = reverse("orders:vnpay_refund")
        body = json.dumps(
            {
                "order_id": self.order.id,
                "amount": 100000,
                "trans_id": "987654321",
                "reason": "Khách trả hàng",
            }
        )
        response = self.client.post(
            url,
            body,
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="refund-0001",
        )
        self.assertEqual(response.status_code, 200)
        replay = self.client.post(
            url,
            body,
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="refund-0001",
        )
        self.assertEqual(replay.status_code, 200)
        changed_transaction = json.dumps(
            {
                "order_id": self.order.id,
                "amount": 100000,
                "trans_id": "different-transaction",
            }
        )
        conflict = self.client.post(
            url,
            changed_transaction,
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="refund-0001",
        )
        self.assertEqual(conflict.status_code, 409)
        refund_mock.assert_called_once()
        self.order.refresh_from_db()
        self.assertEqual(self.order.refunded_amount, 100000)
        self.assertEqual(RefundRecord.objects.get().status, "succeeded")

    def test_refund_rejects_fractional_amount(self):
        User.objects.create_user(
            username="refund_staff", password="StrongPass123!", is_staff=True
        )
        self.client.login(username="refund_staff", password="StrongPass123!")
        response = self.client.post(
            reverse("orders:vnpay_refund"),
            json.dumps(
                {
                    "order_id": self.order.id,
                    "amount": 100000.5,
                    "trans_id": "987654321",
                }
            ),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="refund-0003",
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(RefundRecord.objects.exists())

    @override_settings(VNPAY_REFUND_URL="https://merchant.test/refund")
    @mock.patch(
        "orders.vnpay.refund_transaction",
        return_value={"success": False, "ambiguous": True, "message": "timeout"},
    )
    def test_ambiguous_refund_stays_pending_and_is_not_retried(self, refund_mock):
        User.objects.create_user(
            username="refund_staff", password="StrongPass123!", is_staff=True
        )
        self.client.login(username="refund_staff", password="StrongPass123!")
        self.order.is_paid = True
        self.order.vnpay_transaction_id = "987654321"
        self.order.save(update_fields=["is_paid", "vnpay_transaction_id"])
        url = reverse("orders:vnpay_refund")
        body = json.dumps(
            {"order_id": self.order.id, "amount": 100000, "trans_id": "987654321"}
        )
        response = self.client.post(
            url,
            body,
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="refund-0002",
        )
        self.assertEqual(response.status_code, 202)
        replay = self.client.post(
            url,
            body,
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="refund-0002",
        )
        self.assertEqual(replay.status_code, 202)
        refund_mock.assert_called_once()
        self.assertEqual(RefundRecord.objects.get().status, "pending")

    def test_ipn_bad_signature_returns_97(self):
        params = self._signed()
        params["vnp_SecureHash"] = "deadbeef"
        response = self.client.get(reverse("orders:vnpay_ipn"), params)
        self.assertEqual(response.json()["RspCode"], "97")
        self.order.refresh_from_db()
        self.assertFalse(self.order.is_paid)

    def test_ipn_unknown_order_returns_01(self):
        params = self._signed(vnp_TxnRef="99999")
        response = self.client.get(reverse("orders:vnpay_ipn"), params)
        self.assertEqual(response.json()["RspCode"], "01")

    def test_ipn_already_paid_returns_02(self):
        self.order.is_paid = True
        self.order.save(update_fields=["is_paid"])
        params = self._signed()
        response = self.client.get(reverse("orders:vnpay_ipn"), params)
        self.assertEqual(response.json()["RspCode"], "02")

    def test_checkout_vnpay_creates_processing_unpaid_and_redirects(self):
        self.client.login(username="buyer", password="StrongPass123!")
        self.client.post(
            reverse("orders:cart_add", kwargs={"product_id": self.product.id}),
            {"quantity": 1, "variant_id": self.variant.id},
        )
        response = self.client.post(
            reverse("orders:checkout"),
            {
                "customer_name": "Buyer Test",
                "customer_email": "buyer@test.com",
                "phone": "0909000000",
                "shipping_address": "1 Test Street",
                "payment_method": "vnpay",
                "coupon_code": "",
                "note": "",
            },
        )
        order = Order.objects.filter(payment_method="vnpay").order_by("-id").first()
        self.assertIsNotNone(order)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, reverse("orders:vnpay_payment", kwargs={"order_id": order.id})
        )
        order.refresh_from_db()
        self.assertFalse(order.is_paid)
        self.assertEqual(order.status, "processing")

    def test_vnpay_order_auto_expires_after_15_minutes(self):
        Order.objects.filter(id=self.order.id).update(
            created_at=timezone.now() - timedelta(minutes=16)
        )
        self.order.refresh_from_db()
        self.client.login(username="buyer", password="StrongPass123!")
        response = self.client.get(
            reverse("orders:order_success", kwargs={"order_id": self.order.id})
        )
        self.assertRedirects(
            response, reverse("orders:order_failed", kwargs={"order_id": self.order.id})
        )
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "cancelled")
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock, 5)


class FooterPaymentDisclosureTest(TestCase):
    @override_settings(
        BANK_TRANSFER_ENABLED=False,
        SHOP_BANK_ACCOUNT="",
        SHOP_ACCOUNT_NAME="",
        VNPAY_TMN_CODE="",
        VNPAY_HASH_SECRET="",
    )
    def test_footer_only_advertises_cash_on_delivery_when_other_methods_disabled(self):
        response = self.client.get("/lien-he/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "COD")
        self.assertNotContains(response, "Visa")
        self.assertNotContains(response, "Mastercard")
        self.assertNotContains(response, "PayPal")
        self.assertNotContains(response, "Chuyển khoản ngân hàng")
        self.assertNotContains(response, "VNPay")

    @override_settings(
        DEBUG=True,
        BANK_TRANSFER_ENABLED=True,
        SHOP_BANK_CODE="ICB",
        SHOP_BANK_ACCOUNT="12345678",
        SHOP_ACCOUNT_NAME="HUUGIAU TEST",
        VNPAY_TMN_CODE="TESTTMN",
        VNPAY_HASH_SECRET="test-secret",
        VNPAY_URL="https://sandbox.vnpayment.vn/paymentv2/vpcpay.html",
    )
    def test_footer_shows_only_configured_payment_methods(self):
        response = self.client.get("/lien-he/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "COD")
        self.assertContains(response, "Chuyển khoản")
        self.assertContains(response, "VNPay")
