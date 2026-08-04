import hashlib
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from products.models import Category, Product, ProductVariant
from .admin_forms import CouponForm, OrderEditForm, OrderLookupForm, OrderSearchForm, OrderStatusForm, ProductForm
from .models import Coupon, Order, OrderItem


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
        from .models import Coupon
        self.coupon = Coupon.objects.create(
            code="TEST10", discount_type="percent", value=10,
            min_order_amount=100000, is_active=True,
        )

    def test_dashboard_save_coupon_uses_coupon_form(self):
        self.client.login(username="staff", password="pass123!")
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
        self.client.login(username="staff", password="pass123!")
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
