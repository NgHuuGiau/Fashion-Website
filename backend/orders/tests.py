import hashlib
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Sum
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from products.models import Category, Product, ProductVariant
from .admin_forms import CouponForm, OrderEditForm, OrderLookupForm, OrderSearchForm, OrderStatusForm, ProductForm
from .models import Coupon, Order, OrderItem
from .vnpay import _secure_hash


def _payment_token(order_id):
    raw = f"bank:{order_id}:qr:{settings.SECRET_KEY}"
    return hashlib.sha256(raw.encode()).hexdigest()



class CartCheckoutAndAdminTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="buyer", password="StrongPass123!")
        self.staff = User.objects.create_user(username="staff", password="StrongPass123!", is_staff=True)

        self.category_ao = Category.objects.create(name="Ao", slug="ao")
        self.category_pk = Category.objects.create(name="Phu kien", slug="phu-kien")

        self.product_ao = Product.objects.create(
            category=self.category_ao,
            name="Ao hoodie test",
            slug="ao-hoodie-test",
            price=500000,
            stock=10,
            available=True,
        )
        self.variant_black_l = ProductVariant.objects.create(
            product=self.product_ao,
            color_name="Den",
            color_code="#111111",
            size="L",
            stock=5,
            is_active=True,
        )
        self.variant_red_m = ProductVariant.objects.create(
            product=self.product_ao,
            color_name="Do",
            color_code="#c1121f",
            size="M",
            stock=3,
            is_active=True,
        )

        self.product_accessory = Product.objects.create(
            category=self.category_pk,
            name="Non test",
            slug="non-test",
            price=200000,
            stock=8,
            available=True,
        )

        self.coupon_percent = Coupon.objects.create(
            code="GIAM10",
            discount_type=Coupon.TYPE_PERCENT,
            value=Decimal("10"),
            min_order_amount=Decimal("300000"),
            is_active=True,
        )
        self.coupon_freeship = Coupon.objects.create(
            code="FREESHIP",
            discount_type=Coupon.TYPE_FREESHIP,
            value=Decimal("0"),
            min_order_amount=Decimal("100000"),
            is_active=True,
        )


    def test_cart_add_requires_variant_for_apparel(self):
        add_url = reverse("orders:cart_add", kwargs={"product_id": self.product_ao.id})
        response = self.client.post(add_url, {"quantity": 1})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session.get("cart", {}), {})


    def test_cart_add_non_apparel_without_variant_works(self):
        add_url = reverse("orders:cart_add", kwargs={"product_id": self.product_accessory.id})
        response = self.client.post(add_url, {"quantity": 2})
        self.assertEqual(response.status_code, 302)
        self.assertIn(f"{self.product_accessory.id}:0", self.client.session.get("cart", {}))


    def test_cart_add_invalid_variant_is_rejected(self):
        add_url = reverse("orders:cart_add", kwargs={"product_id": self.product_ao.id})
        response = self.client.post(add_url, {"quantity": 1, "variant_id": 999999})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session.get("cart", {}), {})


    def test_cart_add_quantity_clamped_to_variant_stock(self):
        add_url = reverse("orders:cart_add", kwargs={"product_id": self.product_ao.id})
        self.client.post(add_url, {"quantity": 99, "variant_id": self.variant_black_l.id})
        cart = self.client.session.get("cart", {})
        self.assertEqual(cart[f"{self.product_ao.id}:{self.variant_black_l.id}"]["quantity"], 5)


    def test_cart_update_with_invalid_item_key_does_not_crash(self):
        update_url = reverse("orders:cart_update")
        response = self.client.post(update_url, {"item_key": "wrong-format", "quantity": 2})
        self.assertEqual(response.status_code, 302)


    def test_cart_update_non_numeric_quantity_fallback(self):
        add_url = reverse("orders:cart_add", kwargs={"product_id": self.product_ao.id})
        self.client.post(add_url, {"quantity": 1, "variant_id": self.variant_black_l.id})
        key = f"{self.product_ao.id}:{self.variant_black_l.id}"

        update_url = reverse("orders:cart_update")
        self.client.post(update_url, {"item_key": key, "quantity": "abc"})
        cart = self.client.session.get("cart", {})
        self.assertEqual(cart[key]["quantity"], 1)


    def test_cart_clear_all_empties_session_cart(self):
        self.client.post(reverse("orders:cart_add", kwargs={"product_id": self.product_accessory.id}), {"quantity": 2})
        self.assertTrue(self.client.session.get("cart"))

        response = self.client.post(reverse("orders:cart_clear_all"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session.get("cart", {}), {})


    def test_cart_detail_calculates_shipping_fee(self):
        self.client.post(reverse("orders:cart_add", kwargs={"product_id": self.product_accessory.id}), {"quantity": 1})
        response = self.client.get(reverse("orders:cart_detail"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["subtotal"], Decimal("200000"))
        self.assertEqual(response.context["shipping_fee"], Decimal("30000"))
        self.assertEqual(response.context["total"], Decimal("230000"))


    def test_checkout_requires_login(self):
        response = self.client.get(reverse("orders:checkout"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("users:login"), response.url)


    def test_checkout_empty_cart_redirects(self):
        self.client.login(username="buyer", password="StrongPass123!")
        response = self.client.get(reverse("orders:checkout"))
        self.assertEqual(response.status_code, 302)


    def test_checkout_creates_order_and_updates_stock(self):
        self.client.login(username="buyer", password="StrongPass123!")
        self.client.post(
            reverse("orders:cart_add", kwargs={"product_id": self.product_ao.id}),
            {"quantity": 2, "variant_id": self.variant_black_l.id},
        )

        response = self.client.post(
            reverse("orders:checkout"),
            {
                "customer_name": "Buyer Test",
                "customer_email": "buyer@test.com",
                "phone": "0909000000",
                "shipping_address": "1 Test Street",
                "payment_method": "cod",
                "coupon_code": "",
                "note": "office hours",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)

        order = Order.objects.first()
        self.assertEqual(order.subtotal_amount, Decimal("1000000"))
        self.assertEqual(order.shipping_fee, Decimal("0"))
        self.assertEqual(order.discount_amount, Decimal("0"))
        self.assertEqual(order.total_amount, Decimal("1000000"))
        self.assertEqual(order.status, "pending")
        self.assertFalse(order.is_paid)

        self.variant_black_l.refresh_from_db()
        self.product_ao.refresh_from_db()
        self.assertEqual(self.variant_black_l.stock, 3)
        self.assertEqual(self.product_ao.stock, 6)


    def test_checkout_with_percent_coupon_applies_discount(self):
        self.client.login(username="buyer", password="StrongPass123!")
        self.client.post(
            reverse("orders:cart_add", kwargs={"product_id": self.product_ao.id}),
            {"quantity": 1, "variant_id": self.variant_black_l.id},
        )

        response = self.client.post(
            reverse("orders:checkout"),
            {
                "customer_name": "Buyer Test",
                "customer_email": "buyer@test.com",
                "phone": "0909000000",
                "shipping_address": "1 Test Street",
                "payment_method": "cod",
                "coupon_code": "GIAM10",
                "note": "apply coupon",
            },
        )
        self.assertEqual(response.status_code, 302)

        order = Order.objects.first()
        self.assertEqual(order.coupon_code, "GIAM10")
        self.assertEqual(order.subtotal_amount, Decimal("500000"))
        self.assertEqual(order.discount_amount, Decimal("50000"))
        self.assertEqual(order.total_amount, Decimal("450000"))

        self.coupon_percent.refresh_from_db()
        self.assertEqual(self.coupon_percent.used_count, 1)


    def test_checkout_with_freeship_coupon(self):
        self.client.login(username="buyer", password="StrongPass123!")
        self.client.post(reverse("orders:cart_add", kwargs={"product_id": self.product_accessory.id}), {"quantity": 1})

        response = self.client.post(
            reverse("orders:checkout"),
            {
                "customer_name": "Buyer Test",
                "customer_email": "buyer@test.com",
                "phone": "0909000000",
                "shipping_address": "1 Test Street",
                "payment_method": "cod",
                "coupon_code": "FREESHIP",
                "note": "freeship",
            },
        )
        self.assertEqual(response.status_code, 302)
        order = Order.objects.first()
        self.assertEqual(order.subtotal_amount, Decimal("200000"))
        self.assertEqual(order.shipping_fee, Decimal("30000"))
        self.assertEqual(order.discount_amount, Decimal("30000"))
        self.assertEqual(order.total_amount, Decimal("200000"))


    def test_checkout_invalid_coupon_returns_form_error(self):
        self.client.login(username="buyer", password="StrongPass123!")
        self.client.post(reverse("orders:cart_add", kwargs={"product_id": self.product_accessory.id}), {"quantity": 1})

        response = self.client.post(
            reverse("orders:checkout"),
            {
                "customer_name": "Buyer Test",
                "customer_email": "buyer@test.com",
                "phone": "0909000000",
                "shipping_address": "1 Test Street",
                "payment_method": "cod",
                "coupon_code": "INVALID",
                "note": "invalid coupon",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mã giảm giá không tồn tại")


    def test_checkout_bank_sets_unpaid_and_processing_with_bank_code(self):
        self.client.login(username="buyer", password="StrongPass123!")
        self.client.post(
            reverse("orders:cart_add", kwargs={"product_id": self.product_ao.id}),
            {"quantity": 1, "variant_id": self.variant_red_m.id},
        )

        response = self.client.post(
            reverse("orders:checkout"),
            {
                "customer_name": "Buyer Test",
                "customer_email": "buyer@test.com",
                "phone": "0909000000",
                "shipping_address": "1 Test Street",
                "payment_method": "bank",
                "bank_code": "VCB",
                "coupon_code": "",
                "note": "bank payment",
            },
        )
        self.assertEqual(response.status_code, 302)
        order = Order.objects.first()
        self.assertEqual(response.url, reverse("orders:bank_payment_waiting", kwargs={"order_id": order.id}))
        self.assertEqual(order.status, "processing")
        self.assertFalse(order.is_paid)
        self.assertEqual(order.bank_code, "VCB")


    def test_bank_waiting_page_renders_for_unpaid_bank_order(self):
        self.client.login(username="buyer", password="StrongPass123!")
        order = Order.objects.create(
            user=self.user,
            customer_name="Buyer",
            customer_email="buyer@test.com",
            phone="0909",
            shipping_address="test",
            payment_method="bank",
            bank_code="VCB",
            total_amount=100000,
            status="processing",
            is_paid=False,
        )
        response = self.client.get(reverse("orders:bank_payment_waiting", kwargs={"order_id": order.id}))
        self.assertEqual(response.status_code, 200)


    def test_checkout_bank_requires_bank_code(self):
        self.client.login(username="buyer", password="StrongPass123!")
        self.client.post(
            reverse("orders:cart_add", kwargs={"product_id": self.product_ao.id}),
            {"quantity": 1, "variant_id": self.variant_red_m.id},
        )

        response = self.client.post(
            reverse("orders:checkout"),
            {
                "customer_name": "Buyer Test",
                "customer_email": "buyer@test.com",
                "phone": "0909000000",
                "shipping_address": "1 Test Street",
                "payment_method": "bank",
                "bank_code": "",
                "coupon_code": "",
                "note": "bank payment",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Vui l\u00f2ng ch\u1ecdn ng\u00e2n h\u00e0ng")


    def test_bank_payment_confirm_marks_order_paid(self):
        self.client.login(username="buyer", password="StrongPass123!")
        self.client.post(
            reverse("orders:cart_add", kwargs={"product_id": self.product_ao.id}),
            {"quantity": 1, "variant_id": self.variant_red_m.id},
        )
        self.client.post(
            reverse("orders:checkout"),
            {
                "customer_name": "Buyer Test",
                "customer_email": "buyer@test.com",
                "phone": "0909000000",
                "shipping_address": "1 Test Street",
                "payment_method": "bank",
                "bank_code": "VCB",
                "coupon_code": "",
                "note": "",
            },
        )
        order = Order.objects.first()

        token = _payment_token(order.id)
        response = self.client.post(
            reverse("orders:bank_payment_confirm", kwargs={"order_id": order.id}),
            {"token": token},
        )
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertTrue(order.is_paid)
        self.assertEqual(order.status, "processing")


    def test_bank_payment_cancel_sets_cancelled_and_restores_stock(self):
        self.client.login(username="buyer", password="StrongPass123!")
        self.client.post(
            reverse("orders:cart_add", kwargs={"product_id": self.product_ao.id}),
            {"quantity": 2, "variant_id": self.variant_black_l.id},
        )
        self.client.post(
            reverse("orders:checkout"),
            {
                "customer_name": "Buyer Test",
                "customer_email": "buyer@test.com",
                "phone": "0909000000",
                "shipping_address": "1 Test Street",
                "payment_method": "bank",
                "bank_code": "VCB",
                "coupon_code": "",
                "note": "",
            },
        )
        order = Order.objects.first()
        self.variant_black_l.refresh_from_db()
        self.assertEqual(self.variant_black_l.stock, 3)

        response = self.client.post(reverse("orders:bank_payment_cancel", kwargs={"order_id": order.id}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:order_failed", kwargs={"order_id": order.id}))
        order.refresh_from_db()
        self.assertEqual(order.status, "cancelled")
        self.assertFalse(order.is_paid)

        self.variant_black_l.refresh_from_db()
        self.product_ao.refresh_from_db()
        self.assertEqual(self.variant_black_l.stock, 5)
        self.assertEqual(self.product_ao.stock, 8)


    def test_order_success_redirects_to_order_failed_when_cancelled(self):
        self.client.login(username="buyer", password="StrongPass123!")
        order = Order.objects.create(
            user=self.user,
            customer_name="Buyer",
            customer_email="buyer@test.com",
            phone="0909",
            shipping_address="test",
            payment_method="bank",
            bank_code="VCB",
            total_amount=100000,
            status="cancelled",
            is_paid=False,
        )
        response = self.client.get(reverse("orders:order_success", kwargs={"order_id": order.id}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:order_failed", kwargs={"order_id": order.id}))


    def test_bank_order_auto_expires_after_15_minutes(self):
        self.client.login(username="buyer", password="StrongPass123!")
        self.client.post(
            reverse("orders:cart_add", kwargs={"product_id": self.product_ao.id}),
            {"quantity": 2, "variant_id": self.variant_black_l.id},
        )
        self.client.post(
            reverse("orders:checkout"),
            {
                "customer_name": "Buyer Test",
                "customer_email": "buyer@test.com",
                "phone": "0909000000",
                "shipping_address": "1 Test Street",
                "payment_method": "bank",
                "bank_code": "VCB",
                "coupon_code": "",
                "note": "",
            },
        )
        order = Order.objects.first()
        Order.objects.filter(id=order.id).update(created_at=timezone.now() - timedelta(minutes=16))

        response = self.client.get(reverse("orders:bank_payment_waiting", kwargs={"order_id": order.id}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:order_failed", kwargs={"order_id": order.id}))

        order.refresh_from_db()
        self.assertEqual(order.status, "cancelled")
        self.assertFalse(order.is_paid)
        self.assertIn("AUTO_TIMEOUT_15_MIN", order.note)

        self.variant_black_l.refresh_from_db()
        self.product_ao.refresh_from_db()
        self.assertEqual(self.variant_black_l.stock, 5)
        self.assertEqual(self.product_ao.stock, 8)


    def test_order_review_requires_login(self):
        order = Order.objects.create(
            user=self.user,
            customer_name="Buyer",
            customer_email="buyer@test.com",
            phone="0909",
            shipping_address="test",
            payment_method="bank",
            bank_code="VCB",
            total_amount=100000,
            status="processing",
            is_paid=False,
        )
        response = self.client.get(reverse("orders:order_review", kwargs={"order_id": order.id}))
        self.assertEqual(response.status_code, 302)


    def test_order_review_updates_info_and_redirects_waiting(self):
        self.client.login(username="buyer", password="StrongPass123!")
        order = Order.objects.create(
            user=self.user,
            customer_name="Buyer",
            customer_email="buyer@test.com",
            phone="0909",
            shipping_address="old address",
            payment_method="bank",
            bank_code="VCB",
            total_amount=100000,
            status="processing",
            is_paid=False,
        )
        response = self.client.post(
            reverse("orders:order_review", kwargs={"order_id": order.id}),
            {
                "customer_name": "Buyer New",
                "customer_email": "new@test.com",
                "phone": "0911111111",
                "shipping_address": "new address",
                "note": "update",
                "bank_code": "MB",
                "action": "pay_now",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:bank_payment_waiting", kwargs={"order_id": order.id}))
        order.refresh_from_db()
        self.assertEqual(order.customer_name, "Buyer New")
        self.assertEqual(order.bank_code, "MB")


    def test_my_orders_requires_login(self):
        response = self.client.get(reverse("orders:my_orders"))
        self.assertEqual(response.status_code, 302)


    def test_admin_dashboard_order_list_has_data(self):
        self.client.login(username="staff", password="StrongPass123!")
        self.client.post(
            reverse("orders:cart_add", kwargs={"product_id": self.product_ao.id}),
            {"quantity": 1, "variant_id": self.variant_black_l.id},
        )
        self.client.post(
            reverse("orders:checkout"),
            {"customer_name": "Test", "phone": "0900000000", "shipping_address": "HCM", "payment_method": "cod"},
        )
        response = self.client.get(reverse("orders:admin_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.context["recent_orders"]), 0)


    def test_admin_dashboard_update_order_status(self):
        self.client.login(username="staff", password="StrongPass123!")
        self.client.post(
            reverse("orders:cart_add", kwargs={"product_id": self.product_ao.id}),
            {"quantity": 1, "variant_id": self.variant_black_l.id},
        )
        self.client.post(
            reverse("orders:checkout"),
            {"customer_name": "Test", "phone": "0900000000", "shipping_address": "HCM", "payment_method": "cod"},
        )
        order = Order.objects.first()
        self.assertIsNotNone(order)
        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {"action": "update_order_status", "order_id": order.id, "new_status": "shipping"},
        )
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.status, "shipping")


    def test_admin_mark_shipping_assigns_carrier_and_tracking(self):
        self.client.login(username="staff", password="StrongPass123!")
        self.client.post(
            reverse("orders:cart_add", kwargs={"product_id": self.product_ao.id}),
            {"quantity": 1, "variant_id": self.variant_black_l.id},
        )
        self.client.post(
            reverse("orders:checkout"),
            {"customer_name": "Test", "phone": "0900000000", "shipping_address": "HCM", "payment_method": "cod"},
        )
        order = Order.objects.first()
        self.client.post(
            reverse("orders:admin_dashboard"),
            {"action": "update_order_status", "order_id": order.id, "new_status": "shipping"},
        )
        order.refresh_from_db()
        self.assertEqual(order.carrier, "ghn")
        self.assertTrue(order.tracking_code.startswith("GHD"))
        self.assertIn("donhang.ghn.vn", order.tracking_url)


    def test_admin_mark_delivered_grants_points(self):
        self.client.login(username="staff", password="StrongPass123!")
        self.client.post(
            reverse("orders:cart_add", kwargs={"product_id": self.product_ao.id}),
            {"quantity": 1, "variant_id": self.variant_black_l.id},
        )
        self.client.post(
            reverse("orders:checkout"),
            {"customer_name": "Test", "phone": "0900000000", "shipping_address": "HCM", "payment_method": "cod"},
        )
        order = Order.objects.first()
        self.client.post(
            reverse("orders:admin_dashboard"),
            {"action": "update_order_status", "order_id": order.id, "new_status": "delivered", "is_paid": "on"},
        )
        order.refresh_from_db()
        self.assertEqual(order.status, "delivered")
        self.assertGreater(order.points_earned, 0)
        profile = order.user.profile
        self.assertGreaterEqual(profile.points, order.points_earned)


    def test_user_cancel_order_requires_post(self):
        self.client.login(username="staff", password="StrongPass123!")
        self.client.post(
            reverse("orders:cart_add", kwargs={"product_id": self.product_ao.id}),
            {"quantity": 1, "variant_id": self.variant_black_l.id},
        )
        self.client.post(
            reverse("orders:checkout"),
            {"customer_name": "Test", "phone": "0900000000", "shipping_address": "HCM", "payment_method": "cod"},
        )
        order = Order.objects.first()
        self.assertIsNotNone(order)
        response = self.client.get(reverse("orders:user_cancel_order", kwargs={"order_id": order.id}))
        self.assertEqual(response.status_code, 405)


    def test_user_cancel_order_via_post(self):
        self.client.login(username="staff", password="StrongPass123!")
        self.client.post(
            reverse("orders:cart_add", kwargs={"product_id": self.product_ao.id}),
            {"quantity": 1, "variant_id": self.variant_black_l.id},
        )
        self.client.post(
            reverse("orders:checkout"),
            {"customer_name": "Test", "phone": "0900000000", "shipping_address": "HCM", "payment_method": "cod"},
        )
        order = Order.objects.first()
        self.assertIsNotNone(order)
        self.assertEqual(order.status, "pending")
        response = self.client.post(
            reverse("orders:user_cancel_order", kwargs={"order_id": order.id})
        )
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.status, "cancelled")


    def test_admin_dashboard_requires_staff(self):
        self.client.login(username="buyer", password="StrongPass123!")
        response = self.client.get(reverse("orders:admin_dashboard"))
        self.assertEqual(response.status_code, 302)


    def test_admin_dashboard_staff_access(self):
        self.client.login(username="staff", password="StrongPass123!")
        response = self.client.get(reverse("orders:admin_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("total_orders", response.context)
        self.assertIn("recent_orders", response.context)
        self.assertIn("low_stock_products", response.context)
        self.assertIn("daily_revenue", response.context)
        self.assertIn("active_coupons", response.context)


    def test_admin_dashboard_staff_can_create_product(self):
        self.client.login(username="staff", password="StrongPass123!")
        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {
                "category_id": str(self.category_ao.id),
                "name": "Ao bomber moi",
                "price": "650000",
                "stock": "0",
                "description": "Form boxy local brand",
                "image_url": "https://example.com/bomber.jpg",
                "available": "on",
                "featured": "on",
                "variant_row_key[]": ["row-1", "row-2"],
                "variant_color_name[]": ["Den", "Den"],
                "variant_color_code[]": ["#111111", "#111111"],
                "variant_size[]": ["M", "L"],
                "variant_stock[]": ["4", "6"],
                "variant_is_active[]": ["row-1", "row-2"],
            },
        )

        self.assertEqual(response.status_code, 302)
        product = Product.objects.get(name="Ao bomber moi")
        self.assertEqual(product.category, self.category_ao)
        self.assertEqual(product.stock, 10)
        self.assertEqual(product.price, Decimal("650000"))
        self.assertEqual(product.variants.count(), 2)

    def test_admin_dashboard_create_product_with_matrix_variants(self):
        self.client.login(username="staff", password="StrongPass123!")
        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {
                "category_id": str(self.category_ao.id),
                "name": "Ao polo matrix",
                "price": "350000",
                "stock": "0",
                "available": "on",
                "matrix_sizes": ["S", "M", "L"],
                "matrix_color_name[]": ["Den", "Trang"],
                "matrix_color_code[]": ["#111111", "#ffffff"],
                "matrix_color_active[]": ["0", "1"],
                "matrix_stock_0_S": "2",
                "matrix_stock_0_M": "3",
                "matrix_stock_0_L": "5",
                "matrix_stock_1_S": "1",
                "matrix_stock_1_M": "0",
                "matrix_stock_1_L": "4",
            },
        )

        self.assertEqual(response.status_code, 302)
        product = Product.objects.get(name="Ao polo matrix")
        self.assertEqual(product.variants.count(), 6)
        self.assertEqual(product.stock, 15)
        den_s = product.variants.get(color_name="Den", size="S")
        self.assertTrue(den_s.is_active)
        self.assertEqual(den_s.stock, 2)

    def test_admin_dashboard_matrix_inactive_color_excluded_from_stock(self):
        self.client.login(username="staff", password="StrongPass123!")
        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {
                "category_id": str(self.category_ao.id),
                "name": "Ao den tinh",
                "price": "400000",
                "stock": "0",
                "available": "on",
                "matrix_sizes": ["S", "M"],
                "matrix_color_name[]": ["Den", "Do"],
                "matrix_color_code[]": ["#111111", "#c1121f"],
                "matrix_color_active[]": ["0"],
                "matrix_stock_0_S": "3",
                "matrix_stock_0_M": "4",
                "matrix_stock_1_S": "9",
                "matrix_stock_1_M": "9",
            },
        )

        self.assertEqual(response.status_code, 302)
        product = Product.objects.get(name="Ao den tinh")
        self.assertEqual(product.stock, 7)
        self.assertTrue(product.variants.get(color_name="Den", size="S").is_active)
        self.assertFalse(product.variants.get(color_name="Do", size="S").is_active)

    def test_admin_dashboard_matrix_default_sizes_render(self):
        self.client.login(username="staff", password="StrongPass123!")
        response = self.client.get(reverse("orders:admin_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="matrix_sizes"')
        self.assertContains(response, 'name="matrix_stock_0_S"')
        self.assertContains(response, 'name="matrix_stock_0_XL"')


    def test_admin_dashboard_apparel_requires_variants(self):
        self.client.login(username="staff", password="StrongPass123!")
        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {
                "category_id": str(self.category_ao.id),
                "name": "Ao thieu bien the",
                "price": "550000",
                "stock": "5",
                "description": "Khong co size mau",
                "available": "on",
                "variant_row_key[]": ["row-1"],
                "variant_color_name[]": [""],
                "variant_color_code[]": ["#111111"],
                "variant_size[]": [""],
                "variant_stock[]": [""],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Danh mục áo/quần cần ít nhất một biến thể màu và size.")
        self.assertFalse(Product.objects.filter(name="Ao thieu bien the").exists())


    def test_admin_dashboard_can_mark_out_of_stock(self):
        self.client.login(username="staff", password="StrongPass123!")
        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {
                "action": "mark_out_of_stock",
                "product_id": str(self.product_ao.id),
            },
        )

        self.assertEqual(response.status_code, 302)
        self.product_ao.refresh_from_db()
        self.variant_black_l.refresh_from_db()
        self.assertFalse(self.product_ao.available)
        self.assertEqual(self.product_ao.stock, 0)
        self.assertEqual(self.variant_black_l.stock, 0)


    def test_admin_dashboard_can_update_product(self):
        self.client.login(username="staff", password="StrongPass123!")
        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {
                "action": "save_product",
                "product_id": str(self.product_ao.id),
                "category_id": str(self.category_ao.id),
                "name": "Ao hoodie da sua",
                "price": "700000",
                "stock": "0",
                "description": "Cap nhat mo ta",
                "image_url": "https://example.com/updated.jpg",
                "available": "on",
                "featured": "on",
                "variant_row_key[]": ["row-1"],
                "variant_color_name[]": ["Đen"],
                "variant_color_code[]": ["#111111"],
                "variant_size[]": ["XL"],
                "variant_stock[]": ["9"],
                "variant_is_active[]": ["row-1"],
            },
        )

        self.assertEqual(response.status_code, 302)
        self.product_ao.refresh_from_db()
        self.assertEqual(self.product_ao.name, "Ao hoodie da sua")
        self.assertEqual(self.product_ao.stock, 9)
        self.assertEqual(self.product_ao.variants.count(), 1)
        variant = self.product_ao.variants.first()
        self.assertEqual(variant.size, "XL")

    def test_admin_dashboard_cancel_order_restores_stock(self):
        self.client.login(username="staff", password="StrongPass123!")
        self.client.post(
            reverse("orders:cart_add", kwargs={"product_id": self.product_ao.id}),
            {"quantity": 2, "variant_id": self.variant_black_l.id},
        )
        self.client.post(
            reverse("orders:checkout"),
            {"customer_name": "Test", "phone": "0900000000", "shipping_address": "HCM", "payment_method": "cod"},
        )
        order = Order.objects.first()
        self.variant_black_l.refresh_from_db()
        self.assertEqual(self.variant_black_l.stock, 3)

        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {"action": "update_order_status", "order_id": order.id, "new_status": "cancelled"},
        )
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.status, "cancelled")
        self.variant_black_l.refresh_from_db()
        self.product_ao.refresh_from_db()
        self.assertEqual(self.variant_black_l.stock, 5)
        self.assertEqual(self.product_ao.stock, 8)

    def test_admin_dashboard_reopen_cancelled_order_reserves_stock(self):
        self.client.login(username="staff", password="StrongPass123!")
        self.client.post(
            reverse("orders:cart_add", kwargs={"product_id": self.product_ao.id}),
            {"quantity": 2, "variant_id": self.variant_black_l.id},
        )
        self.client.post(
            reverse("orders:checkout"),
            {"customer_name": "Test", "phone": "0900000000", "shipping_address": "HCM", "payment_method": "cod"},
        )
        order = Order.objects.first()
        self.client.post(
            reverse("orders:admin_dashboard"),
            {"action": "update_order_status", "order_id": order.id, "new_status": "cancelled"},
        )
        order.refresh_from_db()
        self.assertEqual(order.status, "cancelled")

        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {"action": "update_order_status", "order_id": order.id, "new_status": "pending"},
        )
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.status, "pending")
        self.variant_black_l.refresh_from_db()
        self.product_ao.refresh_from_db()
        self.assertEqual(self.variant_black_l.stock, 3)
        self.assertEqual(self.product_ao.stock, 6)

    def test_admin_dashboard_staff_cannot_delete_product(self):
        self.client.login(username="staff", password="StrongPass123!")
        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {"action": "delete_product", "product_id": self.product_accessory.id},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Product.objects.filter(id=self.product_accessory.id).exists())

    def test_admin_dashboard_admin_can_delete_product(self):
        User.objects.create_superuser(username="admin", password="StrongPass123!")
        self.client.login(username="admin", password="StrongPass123!")
        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {"action": "delete_product", "product_id": self.product_accessory.id},
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Product.objects.filter(id=self.product_accessory.id).exists())

    def test_admin_dashboard_admin_set_user_role(self):
        User.objects.create_superuser(username="admin", password="StrongPass123!")
        self.client.login(username="admin", password="StrongPass123!")
        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {"action": "set_user_role", "user_id": self.user.id, "role": "staff"},
        )
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)

        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {"action": "set_user_role", "user_id": self.user.id, "role": "user"},
        )
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)

        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {"action": "set_user_role", "user_id": self.user.id, "role": "admin"},
        )
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_staff)
        self.assertTrue(self.user.is_superuser)

    def test_admin_dashboard_staff_cannot_set_user_role(self):
        self.client.login(username="staff", password="StrongPass123!")
        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {"action": "set_user_role", "user_id": self.user.id, "role": "staff"},
        )
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_staff)

    def test_admin_dashboard_admin_cannot_demote_last_superuser(self):
        admin = User.objects.create_superuser(username="admin", password="StrongPass123!")
        self.client.login(username="admin", password="StrongPass123!")
        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {"action": "set_user_role", "user_id": admin.id, "role": "user"},
        )
        self.assertEqual(response.status_code, 302)
        admin.refresh_from_db()
        self.assertTrue(admin.is_superuser)

    def test_admin_dashboard_admin_can_change_own_role_if_another_admin(self):
        admin = User.objects.create_superuser(username="admin", password="StrongPass123!")
        User.objects.create_superuser(username="admin2", password="StrongPass123!")
        self.client.login(username="admin", password="StrongPass123!")
        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {"action": "set_user_role", "user_id": admin.id, "role": "staff"},
        )
        self.assertEqual(response.status_code, 302)
        admin.refresh_from_db()
        self.assertTrue(admin.is_staff)
        self.assertFalse(admin.is_superuser)

    def test_admin_dashboard_inventory_context(self):
        self.client.login(username="staff", password="StrongPass123!")
        response = self.client.get(reverse("orders:admin_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("inventory_stats", response.context)
        self.assertIn("inventory_products", response.context)
        self.assertIn("permissions", response.context)
        self.assertIn("manage_users", response.context)
        self.assertEqual(response.context["inventory_stats"]["total_products"], Product.objects.count())
        self.assertEqual(response.context["inventory_stats"]["total_units"], Product.objects.aggregate(total=Sum("stock"))["total"])

    def test_admin_dashboard_inventory_out_filter(self):
        self.client.login(username="staff", password="StrongPass123!")
        response = self.client.get(reverse("orders:admin_dashboard"), {"inventory_status": "out"})
        self.assertEqual(response.status_code, 200)
        for product in response.context["inventory_products"]:
            self.assertEqual(product.stock, 0)

    def test_admin_dashboard_staff_permission_flags(self):
        self.client.login(username="staff", password="StrongPass123!")
        response = self.client.get(reverse("orders:admin_dashboard"))
        perms = response.context["permissions"]
        self.assertFalse(perms["is_admin"])
        self.assertTrue(perms["is_staff_member"])
        self.assertTrue(perms["can_manage_orders"])
        self.assertTrue(perms["can_manage_inventory"])
        self.assertTrue(perms["can_manage_products"])
        self.assertFalse(perms["can_delete_product"])
        self.assertFalse(perms["can_manage_coupons"])
        self.assertFalse(perms["can_manage_users"])

    def test_admin_dashboard_admin_create_user_staff(self):
        User.objects.create_superuser(username="admin", password="StrongPass123!")
        self.client.login(username="admin", password="StrongPass123!")
        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {"action": "create_user", "username": "nhanvien01", "password": "matkhau123", "email": "nv@shop.vn", "role": "staff"},
        )
        self.assertEqual(response.status_code, 302)
        new_user = User.objects.get(username="nhanvien01")
        self.assertTrue(new_user.is_staff)
        self.assertFalse(new_user.is_superuser)
        self.assertTrue(new_user.check_password("matkhau123"))
        self.assertEqual(new_user.email, "nv@shop.vn")

    def test_admin_dashboard_admin_create_user_admin(self):
        User.objects.create_superuser(username="admin", password="StrongPass123!")
        self.client.login(username="admin", password="StrongPass123!")
        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {"action": "create_user", "username": "boss", "password": "matkhau123", "role": "admin"},
        )
        self.assertEqual(response.status_code, 302)
        new_user = User.objects.get(username="boss")
        self.assertTrue(new_user.is_superuser)
        self.assertTrue(new_user.is_staff)

    def test_admin_dashboard_create_user_rejects_duplicate(self):
        User.objects.create_superuser(username="admin", password="StrongPass123!")
        self.client.login(username="admin", password="StrongPass123!")
        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {"action": "create_user", "username": "buyer", "password": "matkhau123", "role": "staff"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.filter(username="buyer").count(), 1)

    def test_admin_dashboard_create_user_rejects_short_password(self):
        User.objects.create_superuser(username="admin", password="StrongPass123!")
        self.client.login(username="admin", password="StrongPass123!")
        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {"action": "create_user", "username": "shortpwd", "password": "123", "role": "staff"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.filter(username="shortpwd").exists())

    def test_admin_dashboard_staff_cannot_create_user(self):
        self.client.login(username="staff", password="StrongPass123!")
        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {"action": "create_user", "username": "hacker", "password": "matkhau123", "role": "staff"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.filter(username="hacker").exists())

    def test_admin_dashboard_admin_delete_user(self):
        User.objects.create_superuser(username="admin", password="StrongPass123!")
        victim = User.objects.create_user(username="victim", password="StrongPass123!")
        self.client.login(username="admin", password="StrongPass123!")
        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {"action": "delete_user", "user_id": victim.id},
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.filter(username="victim").exists())

    def test_admin_dashboard_admin_cannot_delete_self(self):
        admin = User.objects.create_superuser(username="admin", password="StrongPass123!")
        User.objects.create_superuser(username="admin2", password="StrongPass123!")
        self.client.login(username="admin", password="StrongPass123!")
        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {"action": "delete_user", "user_id": admin.id},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(id=admin.id).exists())

    def test_admin_dashboard_admin_cannot_delete_last_superuser(self):
        admin = User.objects.create_superuser(username="admin", password="StrongPass123!")
        self.client.login(username="admin", password="StrongPass123!")
        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {"action": "delete_user", "user_id": admin.id},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(id=admin.id).exists())
        self.assertTrue(admin.is_superuser)

    def test_admin_dashboard_inventory_out_includes_hidden_products(self):
        hidden_empty = Product.objects.create(
            category=self.category_pk, name="An het hang", slug="an-het-hang",
            price=100000, stock=0, available=False,
        )
        self.client.login(username="staff", password="StrongPass123!")
        response = self.client.get(reverse("orders:admin_dashboard"), {"inventory_status": "out"})
        self.assertEqual(response.status_code, 200)
        ids = [p.id for p in response.context["inventory_products"]]
        self.assertIn(hidden_empty.id, ids)
        for product in response.context["inventory_products"]:
            self.assertEqual(product.stock, 0)

    def test_admin_dashboard_monthly_revenue_context(self):
        Order.objects.create(
            user=self.user, customer_name="Buyer", phone="0909000000", shipping_address="HCM",
            payment_method="cod", status="delivered", is_paid=True,
            subtotal_amount=200000, total_amount=220000,
        )
        self.client.login(username="staff", password="StrongPass123!")
        response = self.client.get(reverse("orders:admin_dashboard"))
        self.assertIn("monthly_revenue", response.context)
        self.assertEqual(len(response.context["monthly_revenue"]), 12)
        latest = response.context["monthly_revenue"][-1]
        self.assertEqual(latest["revenue"], 220000)
        self.assertEqual(latest["orders_count"], 1)

    def test_admin_export_revenue_requires_staff(self):
        response = self.client.get(reverse("orders:admin_export_revenue"))
        self.assertEqual(response.status_code, 302)

    def test_admin_export_revenue_csv(self):
        Order.objects.create(
            user=self.user, customer_name="Buyer", phone="0909000000", shipping_address="HCM",
            payment_method="cod", status="delivered", is_paid=True,
            subtotal_amount=200000, total_amount=220000,
        )
        self.client.login(username="staff", password="StrongPass123!")
        response = self.client.get(reverse("orders:admin_export_revenue"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/csv", response["Content-Type"])
        body = response.content.decode("utf-8-sig")
        self.assertIn("Tháng", body)
        self.assertIn("220000", body)

    def test_admin_dashboard_chart_context(self):
        self.client.login(username="staff", password="StrongPass123!")
        response = self.client.get(reverse("orders:admin_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("orders_chart", response.context)
        self.assertIn("top_products", response.context)
        self.assertIn("category_revenue", response.context)
        self.assertIn("status_chart", response.context)
        self.assertEqual(len(response.context["orders_chart"]), 7)
        self.assertIsInstance(response.context["top_products"], list)
        self.assertIsInstance(response.context["category_revenue"], list)
        self.assertEqual(len(response.context["status_chart"]), 5)
        for item in response.context["status_chart"]:
            self.assertIn("height", item)
            self.assertIn("label", item)
            self.assertIn("pct", item)
            self.assertIn("offset", item)
            self.assertIn("color", item)
            self.assertGreaterEqual(item["pct"], 0)
            self.assertLessEqual(item["pct"], 100)


class CartRemoveClearTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(name="Phu kien", slug="phu-kien")
        self.product = Product.objects.create(
            category=self.category,
            name="Item to remove",
            slug="item-to-remove",
            price=100000,
            stock=5,
            available=True,
        )

    def test_cart_remove_existing_item(self):
        add_url = reverse("orders:cart_add", kwargs={"product_id": self.product.id})
        self.client.post(add_url, {"quantity": 1})
        key = f"{self.product.id}:0"
        self.assertIn(key, self.client.session.get("cart", {}))

        response = self.client.post(reverse("orders:cart_remove"), {"item_key": key})
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(key, self.client.session.get("cart", {}))

    def test_cart_remove_non_existent_item_does_not_crash(self):
        response = self.client.post(reverse("orders:cart_remove"), {"item_key": "99999:0"})
        self.assertEqual(response.status_code, 302)


class CartFailureTest(TestCase):

    def setUp(self):
        self.category_ao = Category.objects.create(name="Ao", slug="ao")
        self.category_pk = Category.objects.create(name="Phu kien", slug="phu-kien")

        self.unavailable_product = Product.objects.create(
            category=self.category_pk,
            name="Unavailable item",
            slug="unavailable-item",
            price=100000,
            stock=0,
            available=False,
        )
        self.available_product = Product.objects.create(
            category=self.category_ao,
            name="Available item",
            slug="available-item",
            price=200000,
            stock=5,
            available=True,
        )
        self.variant = ProductVariant.objects.create(
            product=self.available_product,
            color_name="Den",
            color_code="#111111",
            size="L",
            stock=5,
            is_active=True,
        )

    def test_cart_add_unavailable_product_fails(self):
        response = self.client.post(
            reverse("orders:cart_add", kwargs={"product_id": self.unavailable_product.id}),
            {"quantity": 1},
        )
        self.assertEqual(response.status_code, 404)

    def test_cart_add_invalid_variant_id_fails(self):
        add_url = reverse("orders:cart_add", kwargs={"product_id": self.available_product.id})
        response = self.client.post(add_url, {"quantity": 1, "variant_id": 999999})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session.get("cart", {}), {})

    def test_cart_update_non_existent_key(self):
        update_url = reverse("orders:cart_update")
        response = self.client.post(update_url, {"item_key": "99999:0", "quantity": 2})
        self.assertEqual(response.status_code, 302)

    def test_cart_update_invalid_item_key_format(self):
        update_url = reverse("orders:cart_update")
        response = self.client.post(update_url, {"item_key": "abc:def:ghi", "quantity": 1})
        self.assertEqual(response.status_code, 302)


class AdminFormsTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(name="Ao", slug="ao")

    def test_product_form_valid(self):
        form = ProductForm(
            data={
                "name": "Ao test",
                "category": self.category.id,
                "slug": "ao-test",
                "price": 500000,
                "available": True,
            }
        )
        self.assertTrue(form.is_valid())

    def test_product_form_invalid_price(self):
        form = ProductForm(
            data={
                "name": "Ao invalid",
                "category": self.category.id,
                "slug": "ao-invalid",
                "price": 0,
                "available": True,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("Giá sản phẩm phải lớn hơn 0.", form.errors["price"])

    def test_coupon_form_valid(self):
        form = CouponForm(
            data={
                "code": "TEST10",
                "discount_type": "percent",
                "value": 10,
                "min_order_amount": 100000,
                "is_active": True,
                "used_count": 0,
            }
        )
        self.assertTrue(form.is_valid())

    def test_coupon_form_invalid_dates(self):
        form = CouponForm(
            data={
                "code": "DATES",
                "discount_type": "percent",
                "value": 10,
                "min_order_amount": 0,
                "is_active": True,
                "used_count": 0,
                "starts_at": "2025-01-01",
                "ends_at": "2024-01-01",
            }
        )
        self.assertFalse(form.is_valid())

    def test_order_status_form_valid(self):
        form = OrderStatusForm(data={"status": "shipping", "is_paid": False})
        self.assertTrue(form.is_valid())

    def test_order_status_form_delivered_requires_paid(self):
        form = OrderStatusForm(data={"status": "delivered", "is_paid": False})
        self.assertFalse(form.is_valid())

    def test_order_search_form_valid(self):
        form = OrderSearchForm(data={"q": "test", "status": "pending"})
        self.assertTrue(form.is_valid())


class CsvExportTest(TestCase):

    def setUp(self):
        from django.contrib.auth.models import User
        self.staff = User.objects.create_user(username="admin", password="admin123!", is_staff=True)
        self.user = User.objects.create_user(username="customer", password="pass123!")
        from .models import Order
        Order.objects.create(
            user=self.user, customer_name="Test", customer_email="t@t.com",
            phone="0909", shipping_address="HCM",
            payment_method="cod", total_amount=200000,
            subtotal_amount=200000, shipping_fee=30000,
            discount_amount=0, status="pending", is_paid=False,
        )

    def test_export_requires_staff(self):
        self.client.login(username="customer", password="pass123!")
        response = self.client.get(reverse("orders:admin_export_orders"))
        self.assertEqual(response.status_code, 404)

    def test_export_returns_csv(self):
        self.client.login(username="admin", password="admin123!")
        response = self.client.get(reverse("orders:admin_export_orders"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8-sig")
        self.assertIn("Mã ĐH", response.content.decode("utf-8-sig"))
        self.assertIn("Test", response.content.decode("utf-8-sig"))

    def test_export_filters_by_status(self):
        self.client.login(username="admin", password="admin123!")
        from .models import Order
        Order.objects.create(
            user=self.user, customer_name="Shipped", customer_email="s@t.com",
            phone="0909", shipping_address="HCM",
            payment_method="cod", total_amount=100000,
            status="shipping", is_paid=False,
        )
        response = self.client.get(reverse("orders:admin_export_orders"), {"status": "shipping"})
        self.assertIn("Shipped", response.content.decode("utf-8-sig"))


class BankPaymentMobileTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="buyer", password="StrongPass123!")
        self.category_pk = Category.objects.create(name="Phu kien", slug="phu-kien")
        self.product = Product.objects.create(
            category=self.category_pk, name="Tui test", slug="tui-test",
            price=300000, stock=10, available=True,
        )
        self.client.login(username="buyer", password="StrongPass123!")
        self.client.post(
            reverse("orders:cart_add", kwargs={"product_id": self.product.id}),
            {"quantity": 1},
        )
        self.client.post(
            reverse("orders:checkout"),
            {"customer_name": "Test", "phone": "0909000000", "shipping_address": "HCM", "payment_method": "bank", "bank_code": "VCB"},
        )
        self.order = Order.objects.first()
        self.token = _payment_token(self.order.id)
        self.mobile_url = reverse("orders:bank_payment_mobile", kwargs={"token": self.token, "order_id": self.order.id})

    def test_mobile_token_mismatch_404(self):
        url = reverse("orders:bank_payment_mobile", kwargs={"token": "invalid", "order_id": self.order.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_mobile_get_active(self):
        response = self.client.get(self.mobile_url)
        self.assertEqual(response.status_code, 200)

    def test_mobile_get_expired_after_timeout(self):
        Order.objects.filter(id=self.order.id).update(created_at=timezone.now() - timedelta(minutes=16))
        response = self.client.get(self.mobile_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("expired", response.context)

    def test_mobile_post_confirm_success(self):
        response = self.client.post(self.mobile_url, {"action": "confirm"})
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertTrue(self.order.is_paid)

    def test_mobile_post_cancel_success(self):
        response = self.client.post(self.mobile_url, {"action": "cancel"})
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "cancelled")


class BankPaymentStatusTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="buyer", password="StrongPass123!")
        self.client.login(username="buyer", password="StrongPass123!")

    def test_status_waiting(self):
        order = Order.objects.create(
            user=self.user, customer_name="T", phone="0909", shipping_address="HCM",
            payment_method="bank", total_amount=100000, status="processing", is_paid=False,
        )
        response = self.client.get(reverse("orders:bank_payment_status", kwargs={"order_id": order.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["state"], "waiting")

    def test_status_success(self):
        order = Order.objects.create(
            user=self.user, customer_name="T", phone="0909", shipping_address="HCM",
            payment_method="bank", total_amount=100000, status="processing", is_paid=True,
        )
        response = self.client.get(reverse("orders:bank_payment_status", kwargs={"order_id": order.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["state"], "success")

    def test_status_failed_when_cancelled(self):
        order = Order.objects.create(
            user=self.user, customer_name="T", phone="0909", shipping_address="HCM",
            payment_method="bank", total_amount=100000, status="cancelled", is_paid=False,
        )
        response = self.client.get(reverse("orders:bank_payment_status", kwargs={"order_id": order.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["state"], "failed")


class OrderLookupTest(TestCase):

    def setUp(self):
        from django.core.cache import cache
        cache.clear()
        self.user = User.objects.create_user(username="buyer", password="StrongPass123!")
        self.order = Order.objects.create(
            user=self.user, customer_name="Lookup Test", phone="0912345678",
            shipping_address="HCM", payment_method="cod", total_amount=200000,
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


class SocialLoginTest(TestCase):

    def test_social_login_invalid_provider(self):
        response = self.client.get(reverse("users:social_login", kwargs={"provider": "invalid"}))
        self.assertEqual(response.status_code, 302)

    def test_social_login_not_configured(self):
        response = self.client.get(reverse("users:social_login", kwargs={"provider": "google"}))
        self.assertEqual(response.status_code, 302)


class OrderEditFormTest(TestCase):

    def test_order_edit_form_valid(self):
        form = OrderEditForm(
            data={"customer_name": "Test", "customer_email": "t@t.com", "phone": "0912345678", "shipping_address": "HCM", "note": "", "bank_code": "VCB"},
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


class AdminDashboardFormIntegrationTest(TestCase):

    def setUp(self):
        from django.contrib.auth.models import User
        self.staff = User.objects.create_user(username="staff", password="pass123!", is_staff=True)
        self.admin = User.objects.create_superuser(username="admin", password="pass123!")
        from .models import Coupon
        self.coupon = Coupon.objects.create(
            code="TEST10", discount_type="percent", value=10,
            min_order_amount=100000, is_active=True,
        )

    def test_dashboard_save_coupon_uses_coupon_form(self):
        self.client.login(username="admin", password="pass123!")
        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {
                "action": "save_coupon",
                "code": "NEW20",
                "discount_type": "percent",
                "value": "20",
                "min_order_amount": "50000",
                "is_active": "on",
                "used_count": "0",
            },
        )
        self.assertEqual(response.status_code, 302)
        from .models import Coupon
        self.assertTrue(Coupon.objects.filter(code="NEW20", value=20).exists())

    def test_dashboard_coupon_form_invalid_shows_error(self):
        self.client.login(username="admin", password="pass123!")
        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {
                "action": "save_coupon",
                "code": "",
                "discount_type": "percent",
                "value": "-5",
                "min_order_amount": "0",
                "is_active": "on",
            },
        )
        self.assertEqual(response.status_code, 302)

    def test_dashboard_save_coupon_denied_for_staff(self):
        self.client.login(username="staff", password="pass123!")
        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {
                "action": "save_coupon",
                "code": "STAFFNO",
                "discount_type": "percent",
                "value": "20",
                "min_order_amount": "50000",
                "is_active": "on",
            },
        )
        self.assertEqual(response.status_code, 302)
        from .models import Coupon
        self.assertFalse(Coupon.objects.filter(code="STAFFNO").exists())

    def test_dashboard_delete_coupon_denied_for_staff(self):
        self.client.login(username="staff", password="pass123!")
        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {"action": "delete_coupon", "coupon_id": self.coupon.id},
        )
        self.assertEqual(response.status_code, 302)
        from .models import Coupon
        self.assertTrue(Coupon.objects.filter(id=self.coupon.id).exists())

    def test_dashboard_update_order_status_uses_order_status_form(self):
        self.client.login(username="staff", password="pass123!")
        from .models import Order
        order = Order.objects.create(
            user=self.staff, customer_name="Test", phone="0909",
            shipping_address="HCM", payment_method="cod",
            total_amount=100000, status="pending", is_paid=False,
        )
        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {"action": "update_order_status", "order_id": order.id, "new_status": "shipping"},
        )
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.status, "shipping")

    def test_dashboard_delivered_requires_paid(self):
        self.client.login(username="staff", password="pass123!")
        from .models import Order
        order = Order.objects.create(
            user=self.staff, customer_name="Test", phone="0909",
            shipping_address="HCM", payment_method="cod",
            total_amount=100000, status="shipping", is_paid=False,
        )
        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {"action": "update_order_status", "order_id": order.id, "new_status": "delivered"},
        )
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.status, "shipping")


class PaymentEdgeBranchesTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="payer", password="StrongPass123!")
        self.category_pk = Category.objects.create(name="Phu kien", slug="phu-kien")
        self.product = Product.objects.create(
            category=self.category_pk, name="Vi test", slug="vi-test",
            price=150000, stock=10, available=True,
        )
        self.client.login(username="payer", password="StrongPass123!")

    def _cod_order(self, **kw):
        defaults = dict(
            user=self.user, customer_name="T", phone="0909", shipping_address="HCM",
            payment_method="cod", total_amount=150000, subtotal_amount=150000,
            shipping_fee=30000, discount_amount=0, status="pending", is_paid=False,
        )
        defaults.update(kw)
        return Order.objects.create(**defaults)

    def test_order_success_expired_bank_redirects_failed(self):
        order = Order.objects.create(
            user=self.user, customer_name="T", phone="0909", shipping_address="HCM",
            payment_method="bank", bank_code="VCB", status="processing", is_paid=False, total_amount=150000,
        )
        Order.objects.filter(id=order.id).update(created_at=timezone.now() - timedelta(minutes=16))
        response = self.client.get(reverse("orders:order_success", kwargs={"order_id": order.id}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:order_failed", kwargs={"order_id": order.id}))

    def test_order_success_paid_cod_renders(self):
        order = self._cod_order(is_paid=True)
        response = self.client.get(reverse("orders:order_success", kwargs={"order_id": order.id}))
        self.assertEqual(response.status_code, 200)

    def test_bank_payment_confirm_non_bank_order(self):
        order = self._cod_order()
        response = self.client.post(
            reverse("orders:bank_payment_confirm", kwargs={"order_id": order.id}),
            {"token": _payment_token(order.id)},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:order_success", kwargs={"order_id": order.id}))
        order.refresh_from_db()
        self.assertFalse(order.is_paid)

    def test_bank_payment_confirm_expired_order(self):
        order = Order.objects.create(
            user=self.user, customer_name="T", phone="0909", shipping_address="HCM",
            payment_method="bank", bank_code="VCB", status="processing", is_paid=False, total_amount=150000,
        )
        Order.objects.filter(id=order.id).update(created_at=timezone.now() - timedelta(minutes=16))
        response = self.client.post(
            reverse("orders:bank_payment_confirm", kwargs={"order_id": order.id}),
            {"token": _payment_token(order.id)},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:order_failed", kwargs={"order_id": order.id}))

    def test_bank_payment_confirm_token_mismatch(self):
        order = Order.objects.create(
            user=self.user, customer_name="T", phone="0909", shipping_address="HCM",
            payment_method="bank", bank_code="VCB", status="processing", is_paid=False, total_amount=150000,
        )
        response = self.client.post(
            reverse("orders:bank_payment_confirm", kwargs={"order_id": order.id}),
            {"token": "wrong-token"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:bank_payment_waiting", kwargs={"order_id": order.id}))
        order.refresh_from_db()
        self.assertFalse(order.is_paid)

    def test_bank_payment_cancel_already_cancelled(self):
        order = Order.objects.create(
            user=self.user, customer_name="T", phone="0909", shipping_address="HCM",
            payment_method="bank", bank_code="VCB", status="cancelled", is_paid=False, total_amount=150000,
        )
        response = self.client.post(reverse("orders:bank_payment_cancel", kwargs={"order_id": order.id}))
        self.assertEqual(response.status_code, 302)

    def test_bank_payment_cancel_non_bank(self):
        order = self._cod_order()
        response = self.client.post(reverse("orders:bank_payment_cancel", kwargs={"order_id": order.id}))
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
        response = self.client.get(reverse("orders:order_failed", kwargs={"order_id": order.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["failed_reason"], "Quá 15 phút chưa thanh toán")

    def test_bank_payment_waiting_non_bank_redirects(self):
        order = self._cod_order()
        response = self.client.get(reverse("orders:bank_payment_waiting", kwargs={"order_id": order.id}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:order_success", kwargs={"order_id": order.id}))

    def test_bank_payment_waiting_paid_redirects_success(self):
        order = Order.objects.create(
            user=self.user, customer_name="T", phone="0909", shipping_address="HCM",
            payment_method="bank", bank_code="VCB", status="processing", is_paid=True, total_amount=150000,
        )
        response = self.client.get(reverse("orders:bank_payment_waiting", kwargs={"order_id": order.id}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:order_success", kwargs={"order_id": order.id}))


class OrderViewEdgeBranchesTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="orderview", password="StrongPass123!")
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
            user=self.user, customer_name="T", phone="0909", shipping_address="HCM",
            payment_method="cod", total_amount=100000, status="processing", is_paid=True,
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
            user=self.user, customer_name="S", phone="0909", shipping_address="HCM",
            payment_method="cod", total_amount=100000, status="shipping", is_paid=True,
        )
        response = self.client.get(reverse("orders:my_orders"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"#{order.id}")
        self.assertNotContains(response, "Cần theo dõi ngay")

    def test_user_cancel_order_not_cancellable_state(self):
        order = Order.objects.create(
            user=self.user, customer_name="T", phone="0909", shipping_address="HCM",
            payment_method="cod", total_amount=100000, status="delivered", is_paid=True,
        )
        response = self.client.post(reverse("orders:user_cancel_order", kwargs={"order_id": order.id}))
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.status, "delivered")


class AdminFormsEdgeTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(name="Ao", slug="ao")

    def test_product_form_empty_name_invalid(self):
        form = ProductForm(data={"name": "  ", "category": self.category.id, "price": 100000})
        self.assertFalse(form.is_valid())

    def test_variant_formset_validation_errors(self):
        from django import forms
        from django.http import QueryDict
        from .admin_forms import ProductVariantFormSet
        data = QueryDict(
            "variant_row_key[]=row-1&variant_row_key[]=row-2"
            "&variant_color_name[]=Do&variant_color_name[]="
            "&variant_size[]=M&variant_size[]="
            "&variant_stock[]=3&variant_stock[]=abc"
        )
        with self.assertRaises(forms.ValidationError) as ctx:
            ProductVariantFormSet.validate_variants(data)
        errors = str(ctx.exception)
        self.assertIn("thiếu size", errors)
        self.assertIn("Tồn kho biến thể ở dòng 2", errors)

    def test_variant_formset_valid(self):
        from django.http import QueryDict
        from .admin_forms import ProductVariantFormSet
        data = QueryDict(
            "variant_row_key[]=row-1"
            "&variant_color_name[]=Den"
            "&variant_color_code[]=#111111"
            "&variant_size[]=L"
            "&variant_stock[]=5"
            "&variant_is_active[]=row-1"
        )
        cleaned = ProductVariantFormSet.validate_variants(data)
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned[0]["stock"], 5)
        self.assertTrue(cleaned[0]["is_active"])

    def test_variant_formset_skips_empty_rows(self):
        from django.http import QueryDict
        from .admin_forms import ProductVariantFormSet
        data = QueryDict(
            "variant_row_key[]=row-1&variant_row_key[]=row-2"
            "&variant_color_name[]=Den&variant_color_name[]="
            "&variant_size[]=L&variant_size[]="
            "&variant_stock[]=&variant_stock[]="
        )
        cleaned = ProductVariantFormSet.validate_variants(data)
        self.assertEqual(len(cleaned), 1)

    def test_order_search_form_invalid_dates(self):
        from .admin_forms import OrderSearchForm
        form = OrderSearchForm(data={"date_from": "not-a-date", "date_to": "also-bad"})
        self.assertFalse(form.is_valid())

    def test_order_edit_form_unknown_bank_falls_back_vcb(self):
        from .admin_forms import OrderEditForm
        form = OrderEditForm(
            data={"customer_name": "T", "customer_email": "", "phone": "0912345678", "shipping_address": "HCM", "bank_code": "UNKNOWN"}
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["bank_code"], "VCB")


class CartHelperTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(name="Phu kien", slug="phu-kien")
        self.product = Product.objects.create(
            category=self.category, name="Test cart helper", slug="test-cart-helper",
            price=100000, stock=5, available=True,
        )

    def _fake_request(self):
        from types import SimpleNamespace
        class FakeSession(dict):
            modified = False
        return SimpleNamespace(session=FakeSession())

    def test_safe_int_invalid_falls_back(self):
        from .cart import safe_int
        self.assertEqual(safe_int("abc", default=1, minimum=1), 1)
        self.assertEqual(safe_int(None, default=7, minimum=0), 7)

    def test_parse_item_key_invalid(self):
        from .cart import _parse_item_key
        self.assertEqual(_parse_item_key("bad-key"), (None, None))

    def test_add_cart_variant_not_found(self):
        from .cart import add_cart
        request = self._fake_request()
        success, msg = add_cart(request, self.product.id, variant_id=999999)
        self.assertFalse(success)
        self.assertIn("Biến thể", msg)

    def test_add_cart_out_of_stock(self):
        from .cart import add_cart
        self.product.stock = 0
        self.product.save()
        request = self._fake_request()
        success, msg = add_cart(request, self.product.id)
        self.assertFalse(success)
        self.assertIn("hết hàng", msg)

    def test_add_cart_override_quantity(self):
        from .cart import add_cart
        request = self._fake_request()
        add_cart(request, self.product.id, quantity=2)
        success, _ = add_cart(request, self.product.id, quantity=1, override_quantity=True)
        self.assertTrue(success)
        cart = request.session["cart"]
        key = f"{self.product.id}:0"
        self.assertEqual(cart[key]["quantity"], 1)

    def test_iter_cart_skips_bad_keys_and_unavailable(self):
        from .cart import iter_cart
        request = self._fake_request()
        request.session["cart"] = {
            "bad-key": {"quantity": 1},
            f"{self.product.id}:0": {"quantity": 1, "price": "100000"},
            "99999:0": {"quantity": 1},
        }
        rows, total = iter_cart(request)
        self.assertEqual(len(rows), 1)
        self.assertEqual(total, Decimal("100000"))

    def test_cart_count(self):
        from .cart import cart_count
        request = self._fake_request()
        request.session["cart"] = {
            f"{self.product.id}:0": {"quantity": 2},
            "abc:1": {"quantity": 3},
        }
        self.assertEqual(cart_count(request), 5)


class CouponModelTest(TestCase):

    def test_is_usable_now_branches(self):
        coupon = Coupon.objects.create(
            code="BRANCH",
            discount_type=Coupon.TYPE_FIXED,
            value=Decimal("50000"),
            min_order_amount=Decimal("0"),
            is_active=True,
        )
        self.assertTrue(coupon.is_usable_now())

        coupon.is_active = False
        self.assertFalse(coupon.is_usable_now())
        coupon.is_active = True

        coupon.starts_at = timezone.now() + timedelta(days=1)
        self.assertFalse(coupon.is_usable_now())
        coupon.starts_at = None

        coupon.ends_at = timezone.now() - timedelta(days=1)
        self.assertFalse(coupon.is_usable_now())
        coupon.ends_at = None

        coupon.usage_limit = 1
        coupon.used_count = 1
        self.assertFalse(coupon.is_usable_now())
        coupon.usage_limit = None
        self.assertTrue(coupon.is_usable_now())

    def test_coupon_str(self):
        coupon = Coupon.objects.create(code="STRTEST", discount_type="percent", value=10, is_active=True)
        self.assertEqual(str(coupon), "STRTEST")

    def test_order_str(self):
        user = User.objects.create_user(username="ostr", password="StrongPass123!")
        order = Order.objects.create(
            user=user, customer_name="T", phone="0909", shipping_address="HCM",
            payment_method="cod", total_amount=100000,
        )
        self.assertIn("Order", str(order))

    def test_order_item_str_and_subtotal(self):
        category = Category.objects.create(name="Ao", slug="ao")
        product = Product.objects.create(
            category=category, name="Ao subtotal", slug="ao-subtotal",
            price=200000, stock=5, available=True,
        )
        user = User.objects.create_user(username="oitem", password="StrongPass123!")
        order = Order.objects.create(
            user=user, customer_name="T", phone="0909", shipping_address="HCM",
            payment_method="cod", total_amount=200000,
        )
        item = OrderItem.objects.create(order=order, product=product, quantity=2, price=200000)
        self.assertEqual(str(item), "2 x Ao subtotal")
        self.assertEqual(item.subtotal(), Decimal("400000"))


class CouponDiscountMathTest(TestCase):

    def setUp(self):
        self.coupon_percent = Coupon.objects.create(code="P", discount_type="percent", value=Decimal("10"), is_active=True)
        self.coupon_fixed = Coupon.objects.create(code="F", discount_type="fixed", value=Decimal("50000"), is_active=True)
        self.coupon_freeship = Coupon.objects.create(code="S", discount_type="freeship", value=Decimal("0"), is_active=True)

    def test_shipping_fee_threshold(self):
        from .views.cart import calculate_shipping_fee
        self.assertEqual(calculate_shipping_fee(Decimal("499000")), Decimal("0"))
        self.assertEqual(calculate_shipping_fee(Decimal("100000")), Decimal("30000"))

    def test_coupon_discount_branches(self):
        from .views.cart import calculate_coupon_discount
        self.assertEqual(calculate_coupon_discount(None, Decimal("200000"), Decimal("30000")), Decimal("0"))
        self.assertEqual(calculate_coupon_discount(self.coupon_percent, Decimal("200000"), Decimal("30000")), Decimal("20000"))
        self.assertEqual(calculate_coupon_discount(self.coupon_fixed, Decimal("200000"), Decimal("30000")), Decimal("50000"))
        self.assertEqual(calculate_coupon_discount(self.coupon_freeship, Decimal("200000"), Decimal("30000")), Decimal("30000"))

    def test_coupon_max_discount_cap(self):
        from .views.cart import calculate_coupon_discount
        self.coupon_fixed.max_discount_amount = Decimal("10000")
        self.assertEqual(calculate_coupon_discount(self.coupon_fixed, Decimal("200000"), Decimal("30000")), Decimal("10000"))

    def test_coupon_discount_never_negative(self):
        from .views.cart import calculate_coupon_discount
        self.coupon_fixed.value = Decimal("999999")
        result = calculate_coupon_discount(self.coupon_fixed, Decimal("100000"), Decimal("30000"))
        self.assertGreaterEqual(result, Decimal("0"))


class ContextProcessorTest(TestCase):

    def test_wishlist_count_cached(self):
        from types import SimpleNamespace
        user = User.objects.create_user(username="cpuser", password="StrongPass123!")
        from .context_processors import wishlist_count
        class FakeSession(dict):
            def set_expiry(self, value):
                self["_expiry"] = value
        request = SimpleNamespace(user=user, session=FakeSession())
        first = wishlist_count(request)
        second = wishlist_count(request)
        self.assertEqual(first, second)
        self.assertIn(f"_wishlist_count_{user.id}", request.session)

    def test_cart_count_cached_returns_cached(self):
        from types import SimpleNamespace
        from .context_processors import cart_count_cached
        request = SimpleNamespace(session={"cart": {"_cart_item_count": 9, "1:0": {"quantity": 1}}})
        self.assertEqual(cart_count_cached(request), 9)

    def test_cart_count_cached_empty_cart(self):
        from types import SimpleNamespace
        from .context_processors import cart_count_cached
        request = SimpleNamespace(session={})
        self.assertEqual(cart_count_cached(request), 0)


class PaymentExtraBranchesTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="payextra", password="StrongPass123!")
        self.client.login(username="payextra", password="StrongPass123!")

    def _bank_order(self, **kw):
        defaults = dict(
            user=self.user, customer_name="T", phone="0909", shipping_address="HCM",
            payment_method="bank", bank_code="VCB", total_amount=100000,
            status="processing", is_paid=False,
        )
        defaults.update(kw)
        return Order.objects.create(**defaults)

    def test_order_success_unpaid_bank_redirects_waiting(self):
        order = self._bank_order()
        response = self.client.get(reverse("orders:order_success", kwargs={"order_id": order.id}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:bank_payment_waiting", kwargs={"order_id": order.id}))

    def test_order_success_paid_bank_renders_with_qr(self):
        order = self._bank_order(is_paid=True)
        response = self.client.get(reverse("orders:order_success", kwargs={"order_id": order.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["qr_url"])

    def test_bank_waiting_cancelled_redirects_failed(self):
        order = self._bank_order(status="cancelled")
        response = self.client.get(reverse("orders:bank_payment_waiting", kwargs={"order_id": order.id}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:order_failed", kwargs={"order_id": order.id}))

    def test_bank_confirm_cancelled_redirects_success(self):
        order = self._bank_order(status="cancelled")
        response = self.client.post(
            reverse("orders:bank_payment_confirm", kwargs={"order_id": order.id}),
            {"token": _payment_token(order.id)},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:order_success", kwargs={"order_id": order.id}))

    def test_bank_confirm_already_paid(self):
        order = self._bank_order(is_paid=True)
        response = self.client.post(
            reverse("orders:bank_payment_confirm", kwargs={"order_id": order.id}),
            {"token": _payment_token(order.id)},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:order_success", kwargs={"order_id": order.id}))

    def test_bank_cancel_already_paid(self):
        order = self._bank_order(is_paid=True)
        response = self.client.post(reverse("orders:bank_payment_cancel", kwargs={"order_id": order.id}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:order_success", kwargs={"order_id": order.id}))

    def _mobile_url(self, order):
        return reverse("orders:bank_payment_mobile", kwargs={"token": _payment_token(order.id), "order_id": order.id})

    def test_mobile_confirm_expired(self):
        order = self._bank_order()
        Order.objects.filter(id=order.id).update(created_at=timezone.now() - timedelta(minutes=16))
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
        Order.objects.filter(id=order.id).update(created_at=timezone.now() - timedelta(minutes=16))
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


class OrderViewExtraBranchesTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="orderextra", password="StrongPass123!")
        self.client.login(username="orderextra", password="StrongPass123!")

    def test_order_review_expired_bank_redirects_failed(self):
        order = Order.objects.create(
            user=self.user, customer_name="T", phone="0909", shipping_address="HCM",
            payment_method="bank", bank_code="VCB", total_amount=100000, status="processing", is_paid=False,
        )
        Order.objects.filter(id=order.id).update(created_at=timezone.now() - timedelta(minutes=16))
        response = self.client.get(reverse("orders:order_review", kwargs={"order_id": order.id}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:order_failed", kwargs={"order_id": order.id}))

    def test_order_review_post_invalid_form_redirects(self):
        order = Order.objects.create(
            user=self.user, customer_name="T", phone="0909", shipping_address="HCM",
            payment_method="cod", total_amount=100000, status="pending", is_paid=False,
        )
        response = self.client.post(
            reverse("orders:order_review", kwargs={"order_id": order.id}),
            {"customer_name": "T", "phone": "abc", "shipping_address": "HCM"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:order_review", kwargs={"order_id": order.id}))

    def test_order_review_get_bank_builds_qr_and_defaults_bank(self):
        order = Order.objects.create(
            user=self.user, customer_name="T", phone="0909", shipping_address="HCM",
            payment_method="bank", bank_code="", total_amount=100000, status="processing", is_paid=False,
        )
        response = self.client.get(reverse("orders:order_review", kwargs={"order_id": order.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["qr_url"])
        self.assertTrue(response.context["selected_bank_name"])

    def test_my_orders_shows_empty_state_without_tracking_card(self):
        Order.objects.create(
            user=self.user, customer_name="T", phone="0909", shipping_address="HCM",
            payment_method="cod", total_amount=100000, status="pending", is_paid=False,
        )
        response = self.client.get(reverse("orders:my_orders"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Cần theo dõi ngay")


class CouponPerUserTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="couponuser", password="StrongPass123!")
        self.client.login(username="couponuser", password="StrongPass123!")
        self.category = Category.objects.create(name="Ao", slug="ao")
        self.product = Product.objects.create(
            category=self.category, name="Ao coupon", slug="ao-coupon",
            price=500000, stock=10, available=True,
        )
        self.coupon = Coupon.objects.create(
            code="PERUSER",
            discount_type=Coupon.TYPE_PERCENT,
            value=Decimal("10"),
            min_order_amount=Decimal("0"),
            max_uses_per_user=1,
            is_active=True,
        )
        self.variant = ProductVariant.objects.create(
            product=self.product, color_name="Den", color_code="#111111", size="L", stock=5, is_active=True,
        )

    def _place_order_with_coupon(self):
        self.client.post(
            reverse("orders:cart_add", kwargs={"product_id": self.product.id}),
            {"quantity": 1, "variant_id": self.variant.id},
        )
        return self.client.post(
            reverse("orders:checkout"),
            {
                "customer_name": "Coupon User",
                "customer_email": "coupon@test.com",
                "phone": "0909000000",
                "shipping_address": "1 Test Street",
                "payment_method": "cod",
                "coupon_code": "PERUSER",
            },
        )

    def test_coupon_usage_recorded_and_second_use_blocked(self):
        response = self._place_order_with_coupon()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Order.objects.count(), 1)
        self.coupon.refresh_from_db()
        self.assertEqual(self.coupon.used_count, 1)
        self.assertEqual(self.coupon.redemptions.count(), 1)
        self.assertEqual(self.coupon.redemptions.first().user, self.user)

        self.client.post(
            reverse("orders:cart_add", kwargs={"product_id": self.product.id}),
            {"quantity": 1, "variant_id": self.variant.id},
        )
        second = self.client.post(
            reverse("orders:checkout"),
            {
                "customer_name": "Coupon User",
                "customer_email": "coupon@test.com",
                "phone": "0909000000",
                "shipping_address": "1 Test Street",
                "payment_method": "cod",
                "coupon_code": "PERUSER",
            },
        )
        self.assertEqual(second.status_code, 200)
        self.assertContains(second, "hết lượt")
        self.assertEqual(Order.objects.count(), 1)

    def test_unlimited_per_user_allows_multiple_uses(self):
        self.coupon.max_uses_per_user = None
        self.coupon.save(update_fields=["max_uses_per_user"])
        self._place_order_with_coupon()
        self.client.post(
            reverse("orders:cart_add", kwargs={"product_id": self.product.id}),
            {"quantity": 1, "variant_id": self.variant.id},
        )
        second = self.client.post(
            reverse("orders:checkout"),
            {
                "customer_name": "Coupon User",
                "customer_email": "coupon@test.com",
                "phone": "0909000000",
                "shipping_address": "1 Test Street",
                "payment_method": "cod",
                "coupon_code": "PERUSER",
            },
        )
        self.assertEqual(second.status_code, 302)
        self.assertEqual(Order.objects.count(), 2)


class ReorderTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="reorder", password="StrongPass123!")
        self.client.login(username="reorder", password="StrongPass123!")
        self.category = Category.objects.create(name="Ao", slug="ao")
        self.product = Product.objects.create(
            category=self.category, name="Ao reorder", slug="ao-reorder",
            price=300000, stock=5, available=True,
        )
        self.variant = ProductVariant.objects.create(
            product=self.product, color_name="Den", color_code="#111111", size="L", stock=3, is_active=True,
        )
        self.order = Order.objects.create(
            user=self.user, customer_name="T", phone="0909", shipping_address="HCM",
            payment_method="cod", total_amount=300000, status="delivered", is_paid=True,
        )
        OrderItem.objects.create(order=self.order, product=self.product, variant=self.variant, quantity=2, price=300000)

    def test_reorder_adds_items_to_cart(self):
        response = self.client.post(reverse("orders:reorder_order", kwargs={"order_id": self.order.id}))
        self.assertRedirects(response, reverse("orders:cart_detail"))
        cart = self.client.session.get("cart", {})
        self.assertEqual(cart[f"{self.product.id}:{self.variant.id}"]["quantity"], 2)

    def test_reorder_requires_post(self):
        response = self.client.get(reverse("orders:reorder_order", kwargs={"order_id": self.order.id}))
        self.assertEqual(response.status_code, 405)

    def test_reorder_skips_unavailable_products(self):
        self.product.available = False
        self.product.save(update_fields=["available"])
        response = self.client.post(reverse("orders:reorder_order", kwargs={"order_id": self.order.id}))
        self.assertRedirects(response, reverse("orders:cart_detail"))
        self.assertEqual(self.client.session.get("cart", {}), {})

    def test_reorder_requires_own_order(self):
        other = User.objects.create_user(username="otheruser", password="StrongPass123!")
        order = Order.objects.create(
            user=other, customer_name="T", phone="0909", shipping_address="HCM",
            payment_method="cod", total_amount=100000, status="delivered", is_paid=True,
        )
        response = self.client.post(reverse("orders:reorder_order", kwargs={"order_id": order.id}))
        self.assertEqual(response.status_code, 404)


VNPAY_CONFIG = {
    "VNPAY_URL": "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html",
    "VNPAY_TMN_CODE": "TESTTMN",
    "VNPAY_HASH_SECRET": "tests3cret",
}


@override_settings(**VNPAY_CONFIG)
class VNPayTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="buyer", password="StrongPass123!")
        self.category = Category.objects.create(name="Ao", slug="ao")
        self.product = Product.objects.create(
            category=self.category, name="Ao vnpay", slug="ao-vnpay",
            price=300000, stock=5, available=True,
        )
        self.variant = ProductVariant.objects.create(
            product=self.product, color_name="Den", color_code="#111111", size="L", stock=3, is_active=True,
        )
        self.order = Order.objects.create(
            user=self.user, customer_name="T", phone="0909", shipping_address="HCM",
            payment_method="vnpay", total_amount=300000, status="processing", is_paid=False,
        )
        OrderItem.objects.create(order=self.order, product=self.product, variant=self.variant, quantity=2, price=300000)

    def _signed(self, **extra):
        params = {
            "vnp_Version": "2.1.0",
            "vnp_Command": "pay",
            "vnp_TmnCode": "TESTTMN",
            "vnp_Amount": "30000000",
            "vnp_TxnRef": str(self.order.id),
            "vnp_ResponseCode": "00",
            "vnp_TransactionStatus": "00",
            "vnp_OrderInfo": "Thanh toan don hang test",
        }
        params.update(extra)
        signed = params.copy()
        signed["vnp_SecureHash"] = _secure_hash(params)
        return signed

    def test_payment_redirects_to_gateway_when_configured(self):
        self.client.login(username="buyer", password="StrongPass123!")
        response = self.client.get(reverse("orders:vnpay_payment", kwargs={"order_id": self.order.id}))
        self.assertEqual(response.status_code, 302)
        self.assertIn("sandbox.vnpayment.vn", response.url)

    def test_payment_unconfigured_redirects_review(self):
        with override_settings(VNPAY_TMN_CODE="", VNPAY_HASH_SECRET=""):
            self.client.login(username="buyer", password="StrongPass123!")
            response = self.client.get(reverse("orders:vnpay_payment", kwargs={"order_id": self.order.id}))
            self.assertRedirects(response, reverse("orders:order_review", kwargs={"order_id": self.order.id}))

    def test_payment_rejects_non_vnpay_order(self):
        self.order.payment_method = "cod"
        self.order.save(update_fields=["payment_method"])
        self.client.login(username="buyer", password="StrongPass123!")
        response = self.client.get(reverse("orders:vnpay_payment", kwargs={"order_id": self.order.id}))
        self.assertRedirects(response, reverse("orders:order_success", kwargs={"order_id": self.order.id}))

    def test_payment_rejects_foreign_order(self):
        other = User.objects.create_user(username="otheruser", password="StrongPass123!")
        order = Order.objects.create(
            user=other, customer_name="T", phone="0909", shipping_address="HCM",
            payment_method="vnpay", total_amount=100000, status="processing", is_paid=False,
        )
        self.client.login(username="buyer", password="StrongPass123!")
        response = self.client.get(reverse("orders:vnpay_payment", kwargs={"order_id": order.id}))
        self.assertEqual(response.status_code, 404)

    def test_return_success_marks_paid(self):
        params = self._signed()
        response = self.client.get(reverse("orders:vnpay_return"), params)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:order_success", kwargs={"order_id": self.order.id}))
        self.order.refresh_from_db()
        self.assertTrue(self.order.is_paid)
        self.assertEqual(self.order.status, "processing")

    def test_return_success_idempotent_when_already_paid(self):
        self.order.is_paid = True
        self.order.save(update_fields=["is_paid"])
        params = self._signed(vnp_ResponseCode="99")
        response = self.client.get(reverse("orders:vnpay_return"), params)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:order_success", kwargs={"order_id": self.order.id}))

    def test_return_failure_cancels_and_restores_stock(self):
        params = self._signed(vnp_ResponseCode="24", vnp_TransactionStatus="24")
        response = self.client.get(reverse("orders:vnpay_return"), params)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:order_failed", kwargs={"order_id": self.order.id}))
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
        self.assertEqual(response.url, reverse("orders:vnpay_payment", kwargs={"order_id": order.id}))
        order.refresh_from_db()
        self.assertFalse(order.is_paid)
        self.assertEqual(order.status, "processing")

    def test_vnpay_order_auto_expires_after_15_minutes(self):
        Order.objects.filter(id=self.order.id).update(created_at=timezone.now() - timedelta(minutes=16))
        self.order.refresh_from_db()
        self.client.login(username="buyer", password="StrongPass123!")
        response = self.client.get(reverse("orders:order_success", kwargs={"order_id": self.order.id}))
        self.assertRedirects(response, reverse("orders:order_failed", kwargs={"order_id": self.order.id}))
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "cancelled")
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock, 5)
