from datetime import timedelta
from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from products.models import Category, Product
from .admin_forms import (
    OrderEditForm,
    OrderLookupForm,
)
from .models import Order, OrderItem, ReturnRequest


class OrderLookupTest(TestCase):
    def setUp(self):
        from django.core.cache import cache

        cache.clear()
        self.user = User.objects.create_user(
            username="buyer", password="StrongPass123!"
        )
        self.order = Order.objects.create(
            user=self.user,
            customer_name="Lookup Test",
            phone="0912345678",
            shipping_address="HCM",
            payment_method="cod",
            total_amount=200000,
        )

    def test_order_lookup_get_renders(self):
        response = self.client.get(reverse("orders:order_lookup"))
        self.assertEqual(response.status_code, 200)

    def test_order_lookup_post_found(self):
        response = self.client.post(
            reverse("orders:order_lookup"),
            {"order_id": self.order.id, "phone": "0912345678"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["looked_up_order"].id, self.order.id)

    def test_order_lookup_post_not_found(self):
        response = self.client.post(
            reverse("orders:order_lookup"),
            {"order_id": 99999, "phone": "0000000000"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("lookup_error", response.context)

    def test_order_lookup_post_invalid_phone(self):
        response = self.client.post(
            reverse("orders:order_lookup"),
            {"order_id": self.order.id, "phone": "abc"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("lookup_error", response.context)


class OrderEditFormTest(TestCase):
    def test_order_edit_form_valid(self):
        form = OrderEditForm(
            data={
                "customer_name": "Test",
                "customer_email": "t@t.com",
                "phone": "0912345678",
                "shipping_address": "HCM",
                "note": "",
                "bank_code": "VCB",
            },
        )
        self.assertTrue(form.is_valid())

    def test_order_edit_form_invalid_phone(self):
        form = OrderEditForm(
            data={"customer_name": "Test", "phone": "abc", "shipping_address": "HCM"},
        )
        self.assertFalse(form.is_valid())
        self.assertIn("Số điện thoại không hợp lệ", str(form.errors.get("phone", "")))


class OrderLookupFormTest(TestCase):
    def test_order_lookup_form_valid(self):
        form = OrderLookupForm(data={"order_id": 1, "phone": "0912345678"})
        self.assertTrue(form.is_valid())

    def test_order_lookup_form_invalid_phone(self):
        form = OrderLookupForm(data={"order_id": 1, "phone": "abc"})
        self.assertFalse(form.is_valid())


class OrderViewEdgeBranchesTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="orderview", password="StrongPass123!"
        )
        self.client.login(username="orderview", password="StrongPass123!")

    def test_estimate_delivery_days_hcm(self):
        from .views.order import estimate_delivery_days

        self.assertEqual(estimate_delivery_days("123 Quan 1, Ho Chi Minh"), 2)

    def test_estimate_delivery_days_near_hcm(self):
        from .views.order import estimate_delivery_days

        self.assertEqual(estimate_delivery_days("Binh Duong"), 3)

    def test_estimate_delivery_days_northern(self):
        from .views.order import estimate_delivery_days

        self.assertEqual(estimate_delivery_days("Ha Noi"), 7)

    def test_estimate_delivery_days_default(self):
        from .views.order import estimate_delivery_days

        self.assertEqual(estimate_delivery_days("Da Lat"), 5)

    def test_order_review_not_editable_when_paid(self):
        order = Order.objects.create(
            user=self.user,
            customer_name="T",
            phone="0909",
            shipping_address="HCM",
            payment_method="cod",
            total_amount=100000,
            status="processing",
            is_paid=True,
        )
        response = self.client.post(
            reverse("orders:order_review", kwargs={"order_id": order.id}),
            {"customer_name": "Hacked", "phone": "0909", "shipping_address": "HCM"},
        )
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.customer_name, "T")

    def test_my_orders_lists_shipping_order(self):
        order = Order.objects.create(
            user=self.user,
            customer_name="S",
            phone="0909",
            shipping_address="HCM",
            payment_method="cod",
            total_amount=100000,
            status="shipping",
            is_paid=True,
        )
        response = self.client.get(reverse("orders:my_orders"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"#{order.id}")
        self.assertNotContains(response, "Cần theo dõi ngay")

    def test_user_cancel_order_not_cancellable_state(self):
        order = Order.objects.create(
            user=self.user,
            customer_name="T",
            phone="0909",
            shipping_address="HCM",
            payment_method="cod",
            total_amount=100000,
            status="delivered",
            is_paid=True,
        )
        response = self.client.post(
            reverse("orders:user_cancel_order", kwargs={"order_id": order.id})
        )
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.status, "delivered")


@override_settings(
    BANK_TRANSFER_ENABLED=True,
    SHOP_BANK_CODE="VCB",
    SHOP_BANK_ACCOUNT="12345678",
    SHOP_ACCOUNT_NAME="HUUGIAU TEST",
)
class OrderViewExtraBranchesTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="orderextra", password="StrongPass123!"
        )
        self.client.login(username="orderextra", password="StrongPass123!")

    def test_order_review_expired_bank_redirects_failed(self):
        order = Order.objects.create(
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
        Order.objects.filter(id=order.id).update(
            created_at=timezone.now() - timedelta(minutes=16)
        )
        response = self.client.get(
            reverse("orders:order_review", kwargs={"order_id": order.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, reverse("orders:order_failed", kwargs={"order_id": order.id})
        )

    def test_order_review_post_invalid_form_redirects(self):
        order = Order.objects.create(
            user=self.user,
            customer_name="T",
            phone="0909",
            shipping_address="HCM",
            payment_method="cod",
            total_amount=100000,
            status="pending",
            is_paid=False,
        )
        response = self.client.post(
            reverse("orders:order_review", kwargs={"order_id": order.id}),
            {"customer_name": "T", "phone": "abc", "shipping_address": "HCM"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, reverse("orders:order_review", kwargs={"order_id": order.id})
        )

    def test_order_review_get_bank_builds_qr_and_defaults_bank(self):
        order = Order.objects.create(
            user=self.user,
            customer_name="T",
            phone="0909",
            shipping_address="HCM",
            payment_method="bank",
            bank_code="",
            total_amount=100000,
            status="processing",
            is_paid=False,
        )
        response = self.client.get(
            reverse("orders:order_review", kwargs={"order_id": order.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["qr_url"])
        self.assertTrue(response.context["selected_bank_name"])

    def test_my_orders_shows_empty_state_without_tracking_card(self):
        Order.objects.create(
            user=self.user,
            customer_name="T",
            phone="0909",
            shipping_address="HCM",
            payment_method="cod",
            total_amount=100000,
            status="pending",
            is_paid=False,
        )
        response = self.client.get(reverse("orders:my_orders"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Cần theo dõi ngay")


class TimelineInLookupTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="tl_user", password="StrongPass123!"
        )
        self.order = Order.objects.create(
            user=self.user,
            customer_name="TL Test",
            phone="0911122233",
            shipping_address="HCM",
            payment_method="cod",
            total_amount=150000,
        )

    def test_timeline_renders_in_lookup_result(self):
        resp = self.client.post(
            reverse("orders:order_lookup"),
            {"order_id": self.order.id, "phone": "0911122233"},
        )
        self.assertContains(resp, "order-timeline")


class ReturnRequestTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="returner", password="StrongPass123!"
        )
        self.client.login(username="returner", password="StrongPass123!")
        self.category = Category.objects.create(name="Ao", slug="ao")
        self.product = Product.objects.create(
            category=self.category,
            name="Ao tra hang",
            slug="ao-tra-hang",
            price=300000,
            stock=5,
            available=True,
        )
        self.order = Order.objects.create(
            user=self.user,
            customer_name="T",
            phone="0909",
            shipping_address="HCM",
            payment_method="cod",
            total_amount=600000,
            status="delivered",
            is_paid=True,
        )
        self.order_item = OrderItem.objects.create(
            order=self.order, product=self.product, quantity=2, price=300000
        )

    def test_can_request_return_only_when_delivered_and_once(self):
        self.assertTrue(self.order.can_request_return)
        ReturnRequest.objects.create(
            order=self.order, return_type="refund", reason="wrong_size"
        )
        self.order.refresh_from_db()
        self.assertFalse(self.order.can_request_return)

    def test_return_page_shows_delivery_date_not_order_date(self):
        delivered_at = timezone.now() - timedelta(days=2)
        self.order.delivered_at = delivered_at
        self.order.save(update_fields=["delivered_at"])
        response = self.client.get(
            reverse("orders:create_return", kwargs={"order_id": self.order.id})
        )
        self.assertContains(
            response, timezone.localtime(delivered_at).strftime("%d/%m/%Y")
        )

    def test_return_page_does_not_invent_missing_delivery_date(self):
        response = self.client.get(
            reverse("orders:create_return", kwargs={"order_id": self.order.id})
        )
        self.assertContains(response, "chưa lưu ngày giao thực tế")

    def test_create_return_request_sums_selected_items(self):
        url = reverse("orders:create_return", kwargs={"order_id": self.order.id})
        response = self.client.post(
            url, {"return_type": "refund", "reason": "wrong_size", "note": "Ao bi rong"}
        )
        self.assertRedirects(
            response, reverse("orders:order_review", kwargs={"order_id": self.order.id})
        )
        rr = ReturnRequest.objects.get(order=self.order)
        self.assertEqual(rr.refund_amount, Decimal("600000"))
        self.assertEqual(rr.status, "pending")
        self.assertEqual(len(rr.items), 1)
        self.assertEqual(rr.items[0]["order_item_id"], self.order_item.id)

    def test_stock_is_only_restored_after_received_and_inspected(self):
        self.product.stock = 3
        self.product.save(update_fields=["stock"])
        response = self.client.post(
            reverse("orders:create_return", kwargs={"order_id": self.order.id}),
            {"return_type": "refund", "reason": "defective"},
        )
        self.assertEqual(response.status_code, 302)
        rr = ReturnRequest.objects.get(order=self.order)
        rr.status = "approved"
        rr.save(update_fields=["status"])
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)
        rr.receive_and_restock()
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 5)
        self.assertEqual(rr.status, "received")
        self.assertIsNotNone(rr.stock_restored_at)
        rr.receive_and_restock()
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 5)

    def test_return_window_expires_seven_days_after_delivery(self):
        self.order.delivered_at = timezone.now() - timedelta(days=8)
        self.order.save(update_fields=["delivered_at"])
        self.assertFalse(self.order.can_request_return)

    def test_create_return_rejected_for_non_delivered(self):
        self.order.status = "shipping"
        self.order.save(update_fields=["status"])
        response = self.client.post(
            reverse("orders:create_return", kwargs={"order_id": self.order.id}),
            {"return_type": "refund", "reason": "wrong_size"},
        )
        self.assertRedirects(
            response, reverse("orders:order_review", kwargs={"order_id": self.order.id})
        )
        self.assertEqual(ReturnRequest.objects.count(), 0)

    def test_return_requires_receipt_before_refund_status(self):
        url = reverse("orders:create_return", kwargs={"order_id": self.order.id})
        self.client.post(url, {"return_type": "refund", "reason": "defective"})
        rr = ReturnRequest.objects.get(order=self.order)
        rr.status = "approved"
        rr.save(update_fields=["status"])
        rr.receive_and_restock()
        rr.refresh_from_db()
        self.assertEqual(rr.status, "received")
        rr.status = "refunded"
        rr.refund_reference = "MANUAL-REF-001"
        rr.save(update_fields=["status"])
        rr.refresh_from_db()
        self.assertEqual(rr.status, "refunded")


class SocialLoginTest(TestCase):
    def test_social_login_invalid_provider(self):
        response = self.client.get(
            reverse("users:social_login", kwargs={"provider": "invalid"})
        )
        self.assertEqual(response.status_code, 302)

    def test_social_login_not_configured(self):
        response = self.client.get(
            reverse("users:social_login", kwargs={"provider": "google"})
        )
        self.assertEqual(response.status_code, 302)
