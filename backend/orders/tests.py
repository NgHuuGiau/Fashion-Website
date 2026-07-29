from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from products.models import Category, Product, ProductVariant
from .models import Coupon, Order, OrderItem



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

        response = self.client.post(reverse("orders:bank_payment_confirm", kwargs={"order_id": order.id}))
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
