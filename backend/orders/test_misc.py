from decimal import Decimal
from unittest import mock
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from products.models import Category, Product, ProductVariant
from users.test_client import VerifiedStaffClient
from .models import Coupon, Order, OrderItem, ReturnRequest


class DemoSeedGuardTest(TestCase):
    @override_settings(DEBUG=False)
    def test_demo_seed_is_refused_in_production_mode(self):
        from django.core.management import call_command
        from django.core.management.base import CommandError

        with self.assertRaisesMessage(CommandError, "không được ghi vào production"):
            call_command("seed_all", no_input=True)


class ContextProcessorTest(TestCase):
    def test_wishlist_count_cached(self):
        from types import SimpleNamespace

        user = User.objects.create_user(username="cpuser", password="StrongPass123!")
        from .context_processors import wishlist_count

        class FakeSession(dict):
            def set_expiry(self, value):
                raise AssertionError("Wishlist cache must not expire the login session")

        request = SimpleNamespace(user=user, session=FakeSession())
        first = wishlist_count(request)
        second = wishlist_count(request)
        self.assertEqual(first, second)
        self.assertIn(f"_wishlist_count_{user.id}", request.session)

    def test_wishlist_count_refreshes_after_five_minutes(self):
        from types import SimpleNamespace
        from .context_processors import wishlist_count

        user = User.objects.create_user(username="cp-expiry", password="StrongPass123!")
        request = SimpleNamespace(user=user, session={})
        with mock.patch("products.models.WishlistItem.objects.filter") as query:
            query.return_value.count.side_effect = [1, 2]
            self.assertEqual(wishlist_count(request), 1)
            self.assertEqual(wishlist_count(request), 1)
            request.session[f"_wishlist_count_{user.id}"]["expires"] = 0
            self.assertEqual(wishlist_count(request), 2)
            self.assertEqual(query.return_value.count.call_count, 2)

    def test_cart_count_cached_returns_cached(self):
        from types import SimpleNamespace
        from .context_processors import cart_count_cached

        request = SimpleNamespace(
            session={"cart": {"_cart_item_count": 9, "1:0": {"quantity": 1}}}
        )
        self.assertEqual(cart_count_cached(request), 9)

    def test_cart_count_cached_empty_cart(self):
        from types import SimpleNamespace
        from .context_processors import cart_count_cached

        request = SimpleNamespace(session={})
        self.assertEqual(cart_count_cached(request), 0)


class RealismBatchBTests(TestCase):
    def setUp(self):
        from users.models import UserProfile

        self.user = User.objects.create_user(
            username="vip_buyer", password="StrongPass123!"
        )
        self.profile = UserProfile.objects.create(user=self.user, points=2000)
        self.cat = Category.objects.create(name="Ao", slug="ao")
        self.product = Product.objects.create(
            category=self.cat,
            name="Ao test",
            slug="ao-test",
            price=400000,
            stock=10,
            available=True,
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            color_name="Den",
            color_code="#111",
            size="M",
            stock=5,
            is_active=True,
        )
        self.client.login(username="vip_buyer", password="StrongPass123!")

    def _checkout(self, **overrides):
        payload = {
            "customer_name": "VIP Buyer",
            "customer_email": "vip@test.com",
            "phone": "0909000000",
            "shipping_address": "12 Nguyen Huu Tho, Quan 7, TP HCM",
            "payment_method": "cod",
            "coupon_code": "",
            "note": "",
            "delivery_time_slot": "evening",
            "gift_wrap": "on",
            "gift_note": "Chuc mung sinh nhat",
        }
        payload.update(overrides)
        self.client.post(
            reverse("orders:cart_add", kwargs={"product_id": self.product.id}),
            {"quantity": 1, "variant_id": self.variant.id},
        )
        return self.client.post(reverse("orders:checkout"), payload)

    def test_region_shipping_fee_near_hcm(self):
        response = self._checkout(shipping_address="12 Nguyen Huu Tho, Quan 7, TP HCM")
        self.assertEqual(response.status_code, 302)
        order = Order.objects.first()
        self.assertEqual(order.shipping_fee, Decimal("25000"))

    def test_region_shipping_fee_standard(self):
        self._checkout(shipping_address="Ninh Kieu, Can Tho")
        self.assertEqual(Order.objects.first().shipping_fee, Decimal("30000"))

    def test_region_shipping_fee_north(self):
        self._checkout(shipping_address="Hoan Kiem, Ha Noi")
        self.assertEqual(Order.objects.first().shipping_fee, Decimal("35000"))

    def test_vip_tier_discount_applied(self):
        self._checkout()
        order = Order.objects.first()
        self.assertEqual(order.discount_amount, Decimal("20000"))
        self.assertEqual(
            order.total_amount, Decimal("25000") + Decimal("400000") - Decimal("20000")
        )

    def test_delivery_slot_and_gift_saved(self):
        self._checkout()
        order = Order.objects.first()
        self.assertEqual(order.delivery_time_slot, "evening")
        self.assertEqual(order.get_delivery_slot_display(), "18:00 – 21:00")
        self.assertTrue(order.gift_wrap)
        self.assertEqual(order.gift_note, "Chuc mung sinh nhat")

    def test_customer_reply_after_shop_reply(self):
        from products.models import Review

        review = Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            comment="Dep",
            shop_reply="Cam on ban",
        )
        url = reverse(
            "products:review_customer_reply", kwargs={"product_id": self.product.id}
        )
        response = self.client.post(url, {"customer_reply": "Rat hai long"})
        self.assertEqual(response.status_code, 302)
        review.refresh_from_db()
        self.assertEqual(review.customer_reply, "Rat hai long")

    def test_customer_reply_requires_shop_reply(self):
        from products.models import Review

        review = Review.objects.create(
            product=self.product, user=self.user, rating=5, comment="Dep"
        )
        url = reverse(
            "products:review_customer_reply", kwargs={"product_id": self.product.id}
        )
        self.client.post(url, {"customer_reply": "Noi dung"})
        review.refresh_from_db()
        self.assertEqual(review.customer_reply, "")


@override_settings(
    BANK_TRANSFER_ENABLED=True,
    SHOP_BANK_CODE="VCB",
    SHOP_BANK_ACCOUNT="12345678",
    SHOP_ACCOUNT_NAME="HUUGIAU TEST",
)
class P1FeaturesTest(TestCase):
    client_class = VerifiedStaffClient

    """Bao phu P1: idempotency checkout + import ton kho CSV."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="buyer", password="StrongPass123!"
        )
        self.staff = User.objects.create_user(
            username="staff", password="StrongPass123!", is_staff=True
        )
        self.category = Category.objects.create(name="Ao", slug="ao")
        self.product = Product.objects.create(
            category=self.category,
            name="Ao test",
            slug="ao-test",
            price=500000,
            stock=10,
            available=True,
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            color_name="Den",
            color_code="#111111",
            size="L",
            stock=5,
            is_active=True,
        )

    def _checkout_payload(self, key="k1"):
        return {
            "customer_name": "Buyer",
            "customer_email": "buyer@test.com",
            "phone": "0909000000",
            "shipping_address": "1 Test Street",
            "payment_method": "cod",
            "coupon_code": "",
            "idempotency_key": key,
        }

    def test_double_submit_same_key_creates_one_order(self):
        self.client.login(username="buyer", password="StrongPass123!")
        self.client.post(
            reverse("orders:cart_add", kwargs={"product_id": self.product.id}),
            {"quantity": 1, "variant_id": self.variant.id},
        )
        url = reverse("orders:checkout")
        r1 = self.client.post(url, self._checkout_payload("dup-key"))
        self.assertEqual(r1.status_code, 302)
        self.assertEqual(Order.objects.count(), 1)
        # cart da xoa sau don 1; nap lai roi submit trung key
        self.client.post(
            reverse("orders:cart_add", kwargs={"product_id": self.product.id}),
            {"quantity": 1, "variant_id": self.variant.id},
        )
        r2 = self.client.post(url, self._checkout_payload("dup-key"))
        self.assertEqual(r2.status_code, 302)
        self.assertEqual(Order.objects.count(), 1)

    def test_import_stock_csv_updates_variant(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        self.client.login(username="staff", password="StrongPass123!")
        csv_body = "product_id,color_name,size,stock\n%s,Den,L,42\n" % self.product.id
        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {
                "action": "import_stock",
                "stock_file": SimpleUploadedFile(
                    "stock.csv", csv_body.encode(), content_type="text/csv"
                ),
            },
        )
        self.assertEqual(response.status_code, 302)
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock, 42)

    def test_import_stock_csv_requires_inventory_perm(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        self.client.login(username="buyer", password="StrongPass123!")
        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {
                "action": "import_stock",
                "stock_file": SimpleUploadedFile(
                    "stock.csv", b"product_id,stock\n1,5\n", content_type="text/csv"
                ),
            },
        )
        self.assertEqual(response.status_code, 302)
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock, 5)

    def test_inventory_list_is_paginated(self):
        self.client.login(username="staff", password="StrongPass123!")
        response = self.client.get(reverse("orders:admin_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("inventory_page_obj", response.context)
        self.assertIn("inventory_stats", response.context)

    @override_settings(EMAIL_HOST="", SUPPORT_EMAIL="")
    def test_notify_low_stock_skipped_without_mail(self):
        from orders.tasks import notify_low_stock

        result = notify_low_stock.run()
        self.assertEqual(result["status"], "skipped_no_mail_config")


class AuditFixBatchTest(TestCase):
    """Bao phu fix audit: hoan tien ty le, diem idempotent, tien te vi, ma giam gia."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="audit_buyer", password="StrongPass123!"
        )
        self.client.login(username="audit_buyer", password="StrongPass123!")
        self.category = Category.objects.create(name="Ao audit", slug="ao-audit")
        self.product = Product.objects.create(
            category=self.category,
            name="Ao audit",
            slug="ao-audit-item",
            price=300000,
            stock=10,
            available=True,
        )
        self.order = Order.objects.create(
            user=self.user,
            customer_name="Audit",
            phone="0909000001",
            shipping_address="HCM",
            payment_method="cod",
            subtotal_amount=Decimal("600000"),
            shipping_fee=Decimal("30000"),
            discount_amount=Decimal("100000"),
            total_amount=Decimal("530000"),
            status="delivered",
            is_paid=True,
        )
        self.item = OrderItem.objects.create(
            order=self.order, product=self.product, quantity=2, price=300000
        )

    def test_return_refund_is_prorated_after_discounts(self):
        self.client.post(
            reverse("orders:create_return", kwargs={"order_id": self.order.id}),
            {"return_type": "refund", "reason": "wrong_size"},
        )
        rr = ReturnRequest.objects.get(order=self.order)
        # hang 600000 da duoc giam con 500000 (khong tinh phi ship) -> hoan 500000
        self.assertEqual(rr.refund_amount, Decimal("500000"))

    def test_double_return_post_creates_single_request(self):
        url = reverse("orders:create_return", kwargs={"order_id": self.order.id})
        self.client.post(url, {"return_type": "refund", "reason": "wrong_size"})
        second = self.client.post(
            url, {"return_type": "refund", "reason": "wrong_size"}
        )
        self.assertRedirects(
            second, reverse("orders:order_review", kwargs={"order_id": self.order.id})
        )
        self.assertEqual(ReturnRequest.objects.count(), 1)

    def test_gateway_amount_checks_reject_foreign_currency(self):
        from .momo import amount_matches as momo_match
        from .shopeepay import amount_matches as sp_match
        from .vnpay import amount_matches as vnp_match
        from .zalopay import amount_matches as zalo_match

        vnd = {"amount": 530000, "currency": "VND"}
        for match in (momo_match, sp_match, zalo_match):
            with self.subTest(gateway=match.__module__):
                self.assertTrue(match(self.order, vnd))
                self.assertFalse(
                    match(self.order, {"amount": 530000, "currency": "USD"})
                )
        vnp = {"vnp_Amount": 53000000, "vnp_CurrCode": "VND"}
        self.assertTrue(vnp_match(self.order, vnp))
        self.assertFalse(vnp_match(self.order, {**vnp, "vnp_CurrCode": "JPY"}))

    def test_grant_order_points_only_once(self):
        from users.models import UserProfile

        from .views.order import _grant_order_points

        _grant_order_points(self.order)
        _grant_order_points(self.order)
        expected = int(self.order.total_amount // 10)
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.points, expected)
        self.order.refresh_from_db()
        self.assertEqual(self.order.points_earned, expected)

    def test_percent_coupon_discount_rounds_to_integer(self):
        from .views.cart import calculate_coupon_discount

        coupon = Coupon.objects.create(
            code="P33",
            discount_type=Coupon.TYPE_PERCENT,
            value=Decimal("33"),
            is_active=True,
        )
        result = calculate_coupon_discount(coupon, Decimal("100001"), Decimal("30000"))
        self.assertEqual(result, Decimal("33000"))

    def test_gift_card_code_format_and_unique(self):
        from .models import GiftCard

        codes = [GiftCard.generate_unique_code() for _ in range(3)]
        for code in codes:
            self.assertRegex(code, r"\AGC[A-Z0-9]{10}\Z")
        self.assertEqual(len(set(codes)), 3, "ma gift card phai ngau nhien")
