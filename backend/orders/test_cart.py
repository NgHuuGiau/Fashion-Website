import hashlib
from datetime import timedelta
from decimal import Decimal
from unittest import mock
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Sum
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from products.models import Category, Product, ProductVariant
from users.test_client import VerifiedStaffClient
from .models import Coupon, Order, OrderItem


def _payment_token(order_id):
    raw = f"bank:{order_id}:qr:{settings.SECRET_KEY}"
    return hashlib.sha256(raw.encode()).hexdigest()


@override_settings(
    BANK_TRANSFER_ENABLED=True,
    SHOP_BANK_CODE="VCB",
    SHOP_BANK_ACCOUNT="12345678",
    SHOP_ACCOUNT_NAME="HUUGIAU TEST",
)
class CartCheckoutAndAdminTest(TestCase):
    client_class = VerifiedStaffClient

    def setUp(self):
        self.user = User.objects.create_user(
            username="buyer", password="StrongPass123!"
        )
        self.staff = User.objects.create_user(
            username="staff", password="StrongPass123!", is_staff=True
        )

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
        add_url = reverse(
            "orders:cart_add", kwargs={"product_id": self.product_accessory.id}
        )
        response = self.client.post(add_url, {"quantity": 2})
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            f"{self.product_accessory.id}:0", self.client.session.get("cart", {})
        )

    def test_cart_add_invalid_variant_is_rejected(self):
        add_url = reverse("orders:cart_add", kwargs={"product_id": self.product_ao.id})
        response = self.client.post(add_url, {"quantity": 1, "variant_id": 999999})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session.get("cart", {}), {})

    def test_cart_add_quantity_clamped_to_variant_stock(self):
        add_url = reverse("orders:cart_add", kwargs={"product_id": self.product_ao.id})
        self.client.post(
            add_url, {"quantity": 99, "variant_id": self.variant_black_l.id}
        )
        cart = self.client.session.get("cart", {})
        self.assertEqual(
            cart[f"{self.product_ao.id}:{self.variant_black_l.id}"]["quantity"], 5
        )

    def test_cart_update_with_invalid_item_key_does_not_crash(self):
        update_url = reverse("orders:cart_update")
        response = self.client.post(
            update_url, {"item_key": "wrong-format", "quantity": 2}
        )
        self.assertEqual(response.status_code, 302)

    def test_cart_update_non_numeric_quantity_fallback(self):
        add_url = reverse("orders:cart_add", kwargs={"product_id": self.product_ao.id})
        self.client.post(
            add_url, {"quantity": 2, "variant_id": self.variant_black_l.id}
        )
        key = f"{self.product_ao.id}:{self.variant_black_l.id}"

        update_url = reverse("orders:cart_update")
        self.client.post(update_url, {"item_key": key, "quantity": "abc"})
        cart = self.client.session.get("cart", {})
        self.assertEqual(cart[key]["quantity"], 2)

    def test_cart_clear_all_empties_session_cart(self):
        self.client.post(
            reverse(
                "orders:cart_add", kwargs={"product_id": self.product_accessory.id}
            ),
            {"quantity": 2},
        )
        self.assertTrue(self.client.session.get("cart"))

        response = self.client.post(reverse("orders:cart_clear_all"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session.get("cart", {}), {})

    def test_cart_detail_calculates_shipping_fee(self):
        self.client.post(
            reverse(
                "orders:cart_add", kwargs={"product_id": self.product_accessory.id}
            ),
            {"quantity": 1},
        )
        response = self.client.get(reverse("orders:cart_detail"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["subtotal"], Decimal("200000"))
        self.assertEqual(response.context["shipping_fee"], Decimal("30000"))
        self.assertEqual(response.context["total"], Decimal("230000"))

    def test_order_item_snapshots_product_name(self):
        self.client.login(username="buyer", password="StrongPass123!")
        self.client.post(
            reverse(
                "orders:cart_add", kwargs={"product_id": self.product_accessory.id}
            ),
            {"quantity": 1},
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
            },
        )
        self.assertEqual(response.status_code, 302)
        order = Order.objects.latest("id")
        item = order.items.get()
        self.assertEqual(item.product_name, "Non test")
        self.product_accessory.name = "Non DOI TEN"
        self.product_accessory.save(update_fields=["name"])
        response = self.client.get(
            reverse("orders:order_review", kwargs={"order_id": order.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Non test")
        self.assertNotContains(response, "Non DOI TEN")

    def test_cart_detail_links_guest_to_checkout(self):
        self.client.post(
            reverse(
                "orders:cart_add", kwargs={"product_id": self.product_accessory.id}
            ),
            {"quantity": 1},
        )
        response = self.client.get(reverse("orders:cart_detail"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, reverse("orders:checkout"), msg_prefix="guest checkout link"
        )
        self.assertNotContains(response, "Đăng nhập để thanh toán")

    def _checkout_payload(self, phone="0909000000"):
        return {
            "customer_name": "Buyer Test",
            "customer_email": "buyer@test.com",
            "phone": phone,
            "shipping_address": "1 Test Street",
            "payment_method": "cod",
            "coupon_code": "",
        }

    def test_checkout_reuses_saved_address_without_duplicate(self):
        from users.models import UserAddress

        self.client.login(username="buyer", password="StrongPass123!")
        UserAddress.objects.create(
            user=self.user,
            recipient_name="Buyer Test",
            phone="0909000000",
            address="1 Test Street",
            is_default=True,
            is_phone_verified=True,
        )
        self.client.post(
            reverse(
                "orders:cart_add", kwargs={"product_id": self.product_accessory.id}
            ),
            {"quantity": 1},
        )
        response = self.client.post(
            reverse("orders:checkout"), self._checkout_payload()
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(UserAddress.objects.filter(user=self.user).count(), 1)

    def test_checkout_edited_info_creates_new_address(self):
        from users.models import UserAddress

        self.client.login(username="buyer", password="StrongPass123!")
        UserAddress.objects.create(
            user=self.user,
            recipient_name="Buyer Test",
            phone="0909000000",
            address="1 Test Street",
            is_default=True,
            is_phone_verified=True,
        )
        self.client.post(
            reverse(
                "orders:cart_add", kwargs={"product_id": self.product_accessory.id}
            ),
            {"quantity": 1},
        )
        payload = self._checkout_payload(phone="0911111111")
        response = self.client.post(reverse("orders:checkout"), payload)
        self.assertEqual(response.status_code, 302)
        addrs = UserAddress.objects.filter(user=self.user).order_by("id")
        self.assertEqual(addrs.count(), 2)
        self.assertTrue(addrs[0].is_default)
        self.assertFalse(addrs[1].is_default)

    def test_checkout_allows_guest(self):
        self.client.post(
            reverse(
                "orders:cart_add", kwargs={"product_id": self.product_accessory.id}
            ),
            {"quantity": 1},
        )
        response = self.client.get(reverse("orders:checkout"))
        self.assertEqual(response.status_code, 200)

    def test_checkout_empty_cart_redirects(self):
        self.client.login(username="buyer", password="StrongPass123!")
        response = self.client.get(reverse("orders:checkout"))
        self.assertEqual(response.status_code, 302)

    def test_cart_add_rejects_bad_quantity(self):
        add_url = reverse(
            "orders:cart_add", kwargs={"product_id": self.product_accessory.id}
        )
        for bad in ("-5", "0", "abc", ""):
            response = self.client.post(add_url, {"quantity": bad})
            self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session.get("cart", {}), {})

    def test_cart_update_zero_removes_item(self):
        add_url = reverse(
            "orders:cart_add", kwargs={"product_id": self.product_accessory.id}
        )
        self.client.post(add_url, {"quantity": 2})
        key = f"{self.product_accessory.id}:0"
        self.assertIn(key, self.client.session.get("cart", {}))
        response = self.client.post(
            reverse("orders:cart_update"), {"item_key": key, "quantity": 0}
        )
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(key, self.client.session.get("cart", {}))

    def test_cart_add_caps_at_stock(self):
        add_url = reverse(
            "orders:cart_add", kwargs={"product_id": self.product_accessory.id}
        )
        self.client.post(add_url, {"quantity": 999999})
        cart = self.client.session.get("cart", {})
        self.assertLessEqual(cart[f"{self.product_accessory.id}:0"]["quantity"], 8)

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

    def test_checkout_requires_review_when_cart_price_changed(self):
        self.client.post(
            reverse(
                "orders:cart_add", kwargs={"product_id": self.product_accessory.id}
            ),
            {"quantity": 1},
        )
        self.product_accessory.price = 250000
        self.product_accessory.save(update_fields=["price", "updated"])
        payload = {
            "customer_name": "Buyer Test",
            "phone": "0909000000",
            "shipping_address": "1 Test Street",
            "payment_method": "cod",
        }

        response = self.client.post(reverse("orders:checkout"), payload)

        self.assertRedirects(
            response, reverse("orders:checkout"), fetch_redirect_response=False
        )
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(
            self.client.session["cart"][f"{self.product_accessory.id}:0"]["price"],
            "250000",
        )

        self.client.post(reverse("orders:checkout"), payload)
        order = Order.objects.get()
        self.assertEqual(order.subtotal_amount, Decimal("250000"))
        self.assertEqual(order.items.get().price, Decimal("250000"))

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
        self.client.post(
            reverse(
                "orders:cart_add", kwargs={"product_id": self.product_accessory.id}
            ),
            {"quantity": 1},
        )

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
        self.client.post(
            reverse(
                "orders:cart_add", kwargs={"product_id": self.product_accessory.id}
            ),
            {"quantity": 1},
        )

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

    def test_gift_coupon_adds_free_gift_item_and_decrements_stock(self):
        gift = Product.objects.create(
            category=self.category_pk,
            name="Tui qua tang",
            slug="tui-qua-tang",
            price=150000,
            stock=5,
            available=True,
        )
        Coupon.objects.create(
            code="QUATANG",
            discount_type=Coupon.TYPE_GIFT,
            value=Decimal("0"),
            gift_product=gift,
            min_order_amount=Decimal("100000"),
            is_active=True,
        )
        self.client.login(username="buyer", password="StrongPass123!")
        self.client.post(
            reverse(
                "orders:cart_add", kwargs={"product_id": self.product_accessory.id}
            ),
            {"quantity": 1},
        )
        response = self.client.post(
            reverse("orders:checkout"),
            {
                "customer_name": "Buyer Test",
                "customer_email": "buyer@test.com",
                "phone": "0909000000",
                "shipping_address": "1 Test Street",
                "payment_method": "cod",
                "coupon_code": "QUATANG",
                "note": "gift coupon",
            },
        )
        self.assertEqual(response.status_code, 302)
        order = Order.objects.get()
        gift_item = order.items.get(product=gift)
        self.assertEqual(gift_item.price, Decimal("0"))
        self.assertEqual(gift_item.quantity, 1)
        self.assertIn("Quà tặng", gift_item.product_name)
        self.assertEqual(order.discount_amount, Decimal("0"))
        gift.refresh_from_db()
        self.assertEqual(gift.stock, 4)

    def test_gift_coupon_out_of_stock_gift_rolls_back_order(self):
        gift = Product.objects.create(
            category=self.category_pk,
            name="Qua het hang",
            slug="qua-het-hang",
            price=150000,
            stock=0,
            available=True,
        )
        Coupon.objects.create(
            code="QUA0",
            discount_type=Coupon.TYPE_GIFT,
            value=Decimal("0"),
            gift_product=gift,
            min_order_amount=Decimal("100000"),
            is_active=True,
        )
        self.client.login(username="buyer", password="StrongPass123!")
        self.client.post(
            reverse(
                "orders:cart_add", kwargs={"product_id": self.product_accessory.id}
            ),
            {"quantity": 1},
        )
        response = self.client.post(
            reverse("orders:checkout"),
            {
                "customer_name": "Buyer Test",
                "customer_email": "buyer@test.com",
                "phone": "0909000000",
                "shipping_address": "1 Test Street",
                "payment_method": "cod",
                "coupon_code": "QUA0",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Order.objects.count(), 0)

    def test_validate_coupon_gift_without_product_errors(self):
        from .services.checkout import validate_coupon

        Coupon.objects.create(
            code="QUANOT",
            discount_type=Coupon.TYPE_GIFT,
            value=Decimal("0"),
            gift_product=None,
            min_order_amount=Decimal("0"),
            is_active=True,
        )
        coupon, error = validate_coupon("QUANOT", Decimal("200000"))
        self.assertIsNone(coupon)
        self.assertIn("chưa được cấu hình", error)

    @override_settings(SHOP_BANK_CODE="ICB")
    def test_checkout_shows_fixed_shop_bank_for_qr(self):
        self.client.login(username="buyer", password="StrongPass123!")
        self.client.post(
            reverse("orders:cart_add", kwargs={"product_id": self.product_ao.id}),
            {"quantity": 1, "variant_id": self.variant_red_m.id},
        )

        response = self.client.get(reverse("orders:checkout"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "VietinBank")
        self.assertContains(response, 'id="id_bank_code" value="ICB"')
        self.assertNotContains(response, 'id="bank-picker"')

    def test_checkout_bank_uses_shop_receiver_even_if_customer_posts_another_bank(self):
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
                "bank_code": "TCB",
                "coupon_code": "",
                "note": "bank payment",
            },
        )
        self.assertEqual(response.status_code, 302)
        order = Order.objects.first()
        self.assertEqual(
            response.url,
            reverse("orders:bank_payment_waiting", kwargs={"order_id": order.id}),
        )
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
        response = self.client.get(
            reverse("orders:bank_payment_waiting", kwargs={"order_id": order.id})
        )
        self.assertEqual(response.status_code, 200)

    def test_checkout_bank_does_not_require_customer_bank_selection(self):
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
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Order.objects.first().bank_code, "VCB")

    @mock.patch("orders.vnpay.is_configured", return_value=False)
    def test_checkout_vnpay_unconfigured_blocks_order(self, _mock_cfg):
        self.client.login(username="buyer", password="StrongPass123!")
        self.client.post(
            reverse("orders:cart_add", kwargs={"product_id": self.product_ao.id}),
            {"quantity": 1, "variant_id": self.variant_red_m.id},
        )
        before = Order.objects.count()
        response = self.client.post(
            reverse("orders:checkout"),
            {
                "customer_name": "Buyer Test",
                "customer_email": "buyer@test.com",
                "phone": "0909000000",
                "shipping_address": "1 Test Street",
                "payment_method": "vnpay",
                "bank_code": "",
                "coupon_code": "",
                "note": "",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "VNPay ch\u01b0a \u0111\u01b0\u1ee3c c\u1ea5u h\u00ecnh"
        )
        self.assertEqual(Order.objects.count(), before)

    @mock.patch("orders.vnpay.is_configured", return_value=False)
    def test_order_success_vnpay_unconfigured_guest_no_loop(self, _mock_cfg):
        order = Order.objects.create(
            user=None,
            customer_name="Guest Vnpay",
            phone="0909",
            shipping_address="test",
            payment_method="vnpay",
            total_amount=100000,
            status="processing",
            is_paid=False,
        )
        session = self.client.session
        session["guest_orders"] = [order.id]
        session.save()
        response = self.client.get(
            reverse("orders:order_success", kwargs={"order_id": order.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "VNPay ch\u01b0a \u0111\u01b0\u1ee3c c\u1ea5u h\u00ecnh"
        )

    @mock.patch("orders.vnpay.is_configured", return_value=False)
    def test_vnpay_payment_guest_unconfigured_goes_order_success(self, _mock_cfg):
        order = Order.objects.create(
            user=None,
            customer_name="Guest Vnpay2",
            phone="0909",
            shipping_address="test",
            payment_method="vnpay",
            total_amount=100000,
            status="processing",
            is_paid=False,
        )
        session = self.client.session
        session["guest_orders"] = [order.id]
        session.save()
        response = self.client.get(
            reverse("orders:vnpay_payment", kwargs={"order_id": order.id}),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain[-1][1], 302)

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
        self.assertFalse(order.is_paid)
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

        response = self.client.post(
            reverse("orders:bank_payment_cancel", kwargs={"order_id": order.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, reverse("orders:order_failed", kwargs={"order_id": order.id})
        )
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
        response = self.client.get(
            reverse("orders:order_success", kwargs={"order_id": order.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, reverse("orders:order_failed", kwargs={"order_id": order.id})
        )

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
        Order.objects.filter(id=order.id).update(
            created_at=timezone.now() - timedelta(minutes=16)
        )

        response = self.client.get(
            reverse("orders:bank_payment_waiting", kwargs={"order_id": order.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, reverse("orders:order_failed", kwargs={"order_id": order.id})
        )

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
        response = self.client.get(
            reverse("orders:order_review", kwargs={"order_id": order.id})
        )
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
        self.assertEqual(
            response.url,
            reverse("orders:bank_payment_waiting", kwargs={"order_id": order.id}),
        )
        order.refresh_from_db()
        self.assertEqual(order.customer_name, "Buyer New")
        self.assertEqual(order.bank_code, "VCB")

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
            {
                "customer_name": "Test",
                "phone": "0900000000",
                "shipping_address": "HCM",
                "payment_method": "cod",
            },
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
            {
                "customer_name": "Test",
                "phone": "0900000000",
                "shipping_address": "HCM",
                "payment_method": "cod",
            },
        )
        order = Order.objects.first()
        self.assertIsNotNone(order)
        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {
                "action": "update_order_status",
                "order_id": order.id,
                "new_status": "shipping",
            },
        )
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.status, "shipping")

    def test_admin_mark_shipping_does_not_fabricate_carrier_or_tracking(self):
        self.client.login(username="staff", password="StrongPass123!")
        self.client.post(
            reverse("orders:cart_add", kwargs={"product_id": self.product_ao.id}),
            {"quantity": 1, "variant_id": self.variant_black_l.id},
        )
        with self.captureOnCommitCallbacks(execute=True):
            self.client.post(
                reverse("orders:checkout"),
                {
                    "customer_name": "Test",
                    "phone": "0900000000",
                    "shipping_address": "HCM",
                    "payment_method": "cod",
                },
            )
        order = Order.objects.first()
        self.client.post(
            reverse("orders:admin_dashboard"),
            {
                "action": "update_order_status",
                "order_id": order.id,
                "new_status": "shipping",
            },
        )
        order.refresh_from_db()
        self.assertEqual(order.status, "shipping")
        self.assertEqual(order.carrier, "ghn")
        self.assertEqual(order.tracking_code, "")

    def test_tracking_decoration_does_not_auto_advance_old_order(self):
        order = Order.objects.create(
            user=self.user,
            customer_name="Old pending",
            phone="0909",
            shipping_address="HCM",
            payment_method="cod",
            total_amount=100000,
            status="pending",
            is_paid=False,
        )
        Order.objects.filter(id=order.id).update(
            created_at=timezone.now() - timedelta(days=30)
        )

        from .views.order import decorate_order_tracking

        decorate_order_tracking(order)
        order.refresh_from_db()
        self.assertEqual(order.status, "pending")
        self.assertFalse(order.is_paid)

    def test_admin_mark_delivered_grants_points(self):
        self.client.login(username="staff", password="StrongPass123!")
        self.client.post(
            reverse("orders:cart_add", kwargs={"product_id": self.product_ao.id}),
            {"quantity": 1, "variant_id": self.variant_black_l.id},
        )
        self.client.post(
            reverse("orders:checkout"),
            {
                "customer_name": "Test",
                "phone": "0900000000",
                "shipping_address": "HCM",
                "payment_method": "cod",
            },
        )
        order = Order.objects.first()
        self.client.post(
            reverse("orders:admin_dashboard"),
            {
                "action": "update_order_status",
                "order_id": order.id,
                "new_status": "delivered",
                "is_paid": "on",
            },
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
            {
                "customer_name": "Test",
                "phone": "0900000000",
                "shipping_address": "HCM",
                "payment_method": "cod",
            },
        )
        order = Order.objects.first()
        self.assertIsNotNone(order)
        response = self.client.get(
            reverse("orders:user_cancel_order", kwargs={"order_id": order.id})
        )
        self.assertEqual(response.status_code, 405)

    def test_user_cancel_order_via_post(self):
        self.client.login(username="staff", password="StrongPass123!")
        self.client.post(
            reverse("orders:cart_add", kwargs={"product_id": self.product_ao.id}),
            {"quantity": 1, "variant_id": self.variant_black_l.id},
        )
        self.client.post(
            reverse("orders:checkout"),
            {
                "customer_name": "Test",
                "phone": "0900000000",
                "shipping_address": "HCM",
                "payment_method": "cod",
            },
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
        self.assertContains(
            response, "Danh mục áo/quần cần ít nhất một biến thể màu và size."
        )
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

    def test_admin_dashboard_edit_link_opens_product_form(self):
        self.client.login(username="staff", password="StrongPass123!")
        response = self.client.get(
            reverse("orders:admin_dashboard"), {"edit": self.product_ao.id}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="admin-product-form"')
        # Trang sửa sản phẩm phải mở sẵn tab biểu mẫu, không phải tab tổng quan.
        html = response.content.decode()
        form_idx = html.index('id="admin-product-form"')
        self.assertIn("admin-tab-content active", html[form_idx - 40 : form_idx])
        self.assertContains(response, "Chỉnh sửa sản phẩm")

    def test_admin_product_update_preserves_order_variant_for_stock_restore(self):
        self.variant_black_l.stock = 3
        self.variant_black_l.save(update_fields=["stock"])
        order = Order.objects.create(
            customer_name="Buyer",
            phone="0900000000",
            shipping_address="Test address",
            payment_method="cod",
            status="pending",
            subtotal_amount=Decimal("100000"),
            total_amount=Decimal("100000"),
        )
        item = OrderItem.objects.create(
            order=order,
            product=self.product_ao,
            variant=self.variant_black_l,
            selected_color="Den",
            selected_size="L",
            quantity=2,
            price=Decimal("50000"),
        )
        self.client.login(username="staff", password="StrongPass123!")

        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {
                "action": "save_product",
                "product_id": str(self.product_ao.id),
                "category_id": str(self.category_ao.id),
                "name": self.product_ao.name,
                "price": "500000",
                "stock": "0",
                "variant_row_key[]": ["row-1"],
                "variant_color_name[]": ["Den"],
                "variant_color_code[]": ["#111111"],
                "variant_size[]": ["L"],
                "variant_stock[]": ["3"],
                "variant_is_active[]": ["row-1"],
            },
        )

        self.assertEqual(response.status_code, 302)
        item.refresh_from_db()
        self.assertEqual(item.variant_id, self.variant_black_l.id)
        from .views.cart import apply_order_status_change

        apply_order_status_change(order, "cancelled")
        self.variant_black_l.refresh_from_db()
        self.assertEqual(self.variant_black_l.stock, 5)

    def test_admin_product_update_archives_removed_order_variant(self):
        self.variant_black_l.stock = 3
        self.variant_black_l.save(update_fields=["stock"])
        order = Order.objects.create(
            customer_name="Buyer",
            phone="0900000000",
            shipping_address="Test address",
            payment_method="cod",
            status="pending",
            subtotal_amount=Decimal("100000"),
            total_amount=Decimal("100000"),
        )
        item = OrderItem.objects.create(
            order=order,
            product=self.product_ao,
            variant=self.variant_black_l,
            selected_color="Den",
            selected_size="L",
            quantity=2,
            price=Decimal("50000"),
        )
        self.client.login(username="staff", password="StrongPass123!")

        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {
                "action": "save_product",
                "product_id": str(self.product_ao.id),
                "category_id": str(self.category_ao.id),
                "name": self.product_ao.name,
                "price": "500000",
                "stock": "0",
                "variant_row_key[]": ["row-1"],
                "variant_color_name[]": ["Den"],
                "variant_color_code[]": ["#111111"],
                "variant_size[]": ["XL"],
                "variant_stock[]": ["9"],
                "variant_is_active[]": ["row-1"],
            },
        )

        self.assertEqual(response.status_code, 302)
        item.refresh_from_db()
        self.variant_black_l.refresh_from_db()
        self.assertEqual(item.variant_id, self.variant_black_l.id)
        self.assertFalse(self.variant_black_l.is_active)
        self.assertTrue(
            ProductVariant.objects.filter(
                product=self.product_ao, size="XL", is_active=True
            ).exists()
        )

        from .views.cart import apply_order_status_change

        apply_order_status_change(order, "cancelled")
        self.variant_black_l.refresh_from_db()
        self.product_ao.refresh_from_db()
        self.assertEqual(self.variant_black_l.stock, 5)
        self.assertEqual(self.product_ao.stock, 9)

    def test_admin_dashboard_cancel_order_restores_stock(self):
        self.client.login(username="staff", password="StrongPass123!")
        self.client.post(
            reverse("orders:cart_add", kwargs={"product_id": self.product_ao.id}),
            {"quantity": 2, "variant_id": self.variant_black_l.id},
        )
        self.client.post(
            reverse("orders:checkout"),
            {
                "customer_name": "Test",
                "phone": "0900000000",
                "shipping_address": "HCM",
                "payment_method": "cod",
            },
        )
        order = Order.objects.first()
        self.variant_black_l.refresh_from_db()
        self.assertEqual(self.variant_black_l.stock, 3)

        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {
                "action": "update_order_status",
                "order_id": order.id,
                "new_status": "cancelled",
            },
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
            {
                "customer_name": "Test",
                "phone": "0900000000",
                "shipping_address": "HCM",
                "payment_method": "cod",
            },
        )
        order = Order.objects.first()
        self.client.post(
            reverse("orders:admin_dashboard"),
            {
                "action": "update_order_status",
                "order_id": order.id,
                "new_status": "cancelled",
            },
        )
        order.refresh_from_db()
        self.assertEqual(order.status, "cancelled")

        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {
                "action": "update_order_status",
                "order_id": order.id,
                "new_status": "pending",
            },
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

    def test_admin_cannot_delete_product_with_order_history(self):
        order = Order.objects.create(
            customer_name="Buyer",
            phone="0900000000",
            shipping_address="Test address",
            subtotal_amount=Decimal("200000"),
            total_amount=Decimal("200000"),
        )
        item = OrderItem.objects.create(
            order=order,
            product=self.product_accessory,
            quantity=1,
            price=Decimal("200000"),
        )
        User.objects.create_superuser(username="admin", password="StrongPass123!")
        self.client.login(username="admin", password="StrongPass123!")

        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {"action": "delete_product", "product_id": self.product_accessory.id},
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Product.objects.filter(id=self.product_accessory.id).exists())
        self.assertTrue(OrderItem.objects.filter(pk=item.pk).exists())

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
        admin = User.objects.create_superuser(
            username="admin", password="StrongPass123!"
        )
        self.client.login(username="admin", password="StrongPass123!")
        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {"action": "set_user_role", "user_id": admin.id, "role": "user"},
        )
        self.assertEqual(response.status_code, 302)
        admin.refresh_from_db()
        self.assertTrue(admin.is_superuser)

    def test_admin_dashboard_admin_can_change_own_role_if_another_admin(self):
        admin = User.objects.create_superuser(
            username="admin", password="StrongPass123!"
        )
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
        self.assertEqual(
            response.context["inventory_stats"]["total_products"],
            Product.objects.count(),
        )
        self.assertEqual(
            response.context["inventory_stats"]["total_units"],
            Product.objects.aggregate(total=Sum("stock"))["total"],
        )

    def test_admin_dashboard_inventory_out_filter(self):
        self.client.login(username="staff", password="StrongPass123!")
        response = self.client.get(
            reverse("orders:admin_dashboard"), {"inventory_status": "out"}
        )
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
            {
                "action": "create_user",
                "username": "nhanvien01",
                "password": "matkhau123",
                "email": "nv@shop.vn",
                "role": "staff",
            },
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
            {
                "action": "create_user",
                "username": "boss",
                "password": "matkhau123",
                "role": "admin",
            },
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
            {
                "action": "create_user",
                "username": "buyer",
                "password": "matkhau123",
                "role": "staff",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.filter(username="buyer").count(), 1)

    def test_admin_dashboard_create_user_rejects_short_password(self):
        User.objects.create_superuser(username="admin", password="StrongPass123!")
        self.client.login(username="admin", password="StrongPass123!")
        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {
                "action": "create_user",
                "username": "shortpwd",
                "password": "123",
                "role": "staff",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.filter(username="shortpwd").exists())

    def test_admin_dashboard_staff_cannot_create_user(self):
        self.client.login(username="staff", password="StrongPass123!")
        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {
                "action": "create_user",
                "username": "hacker",
                "password": "matkhau123",
                "role": "staff",
            },
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
        admin = User.objects.create_superuser(
            username="admin", password="StrongPass123!"
        )
        User.objects.create_superuser(username="admin2", password="StrongPass123!")
        self.client.login(username="admin", password="StrongPass123!")
        response = self.client.post(
            reverse("orders:admin_dashboard"),
            {"action": "delete_user", "user_id": admin.id},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(id=admin.id).exists())

    def test_admin_dashboard_admin_cannot_delete_last_superuser(self):
        admin = User.objects.create_superuser(
            username="admin", password="StrongPass123!"
        )
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
            category=self.category_pk,
            name="An het hang",
            slug="an-het-hang",
            price=100000,
            stock=0,
            available=False,
        )
        self.client.login(username="staff", password="StrongPass123!")
        response = self.client.get(
            reverse("orders:admin_dashboard"), {"inventory_status": "out"}
        )
        self.assertEqual(response.status_code, 200)
        ids = [p.id for p in response.context["inventory_products"]]
        self.assertIn(hidden_empty.id, ids)
        for product in response.context["inventory_products"]:
            self.assertEqual(product.stock, 0)

    def test_admin_dashboard_monthly_revenue_context(self):
        Order.objects.create(
            user=self.user,
            customer_name="Buyer",
            phone="0909000000",
            shipping_address="HCM",
            payment_method="cod",
            status="delivered",
            is_paid=True,
            subtotal_amount=200000,
            total_amount=220000,
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
            user=self.user,
            customer_name="Buyer",
            phone="0909000000",
            shipping_address="HCM",
            payment_method="cod",
            status="delivered",
            is_paid=True,
            subtotal_amount=200000,
            total_amount=220000,
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
        response = self.client.post(
            reverse("orders:cart_remove"), {"item_key": "99999:0"}
        )
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
            reverse(
                "orders:cart_add", kwargs={"product_id": self.unavailable_product.id}
            ),
            {"quantity": 1},
        )
        self.assertEqual(response.status_code, 404)

    def test_cart_add_invalid_variant_id_fails(self):
        add_url = reverse(
            "orders:cart_add", kwargs={"product_id": self.available_product.id}
        )
        response = self.client.post(add_url, {"quantity": 1, "variant_id": 999999})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session.get("cart", {}), {})

    def test_cart_update_non_existent_key(self):
        update_url = reverse("orders:cart_update")
        response = self.client.post(update_url, {"item_key": "99999:0", "quantity": 2})
        self.assertEqual(response.status_code, 302)

    def test_cart_update_invalid_item_key_format(self):
        update_url = reverse("orders:cart_update")
        response = self.client.post(
            update_url, {"item_key": "abc:def:ghi", "quantity": 1}
        )
        self.assertEqual(response.status_code, 302)


class CartHelperTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Phu kien", slug="phu-kien")
        self.product = Product.objects.create(
            category=self.category,
            name="Test cart helper",
            slug="test-cart-helper",
            price=100000,
            stock=5,
            available=True,
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
        success, _ = add_cart(
            request, self.product.id, quantity=1, override_quantity=True
        )
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


class ReorderTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="reorder", password="StrongPass123!"
        )
        self.client.login(username="reorder", password="StrongPass123!")
        self.category = Category.objects.create(name="Ao", slug="ao")
        self.product = Product.objects.create(
            category=self.category,
            name="Ao reorder",
            slug="ao-reorder",
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
            payment_method="cod",
            total_amount=300000,
            status="delivered",
            is_paid=True,
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            variant=self.variant,
            quantity=2,
            price=300000,
        )

    def test_reorder_adds_items_to_cart(self):
        response = self.client.post(
            reverse("orders:reorder_order", kwargs={"order_id": self.order.id})
        )
        self.assertRedirects(response, reverse("orders:cart_detail"))
        cart = self.client.session.get("cart", {})
        self.assertEqual(cart[f"{self.product.id}:{self.variant.id}"]["quantity"], 2)

    def test_reorder_requires_post(self):
        response = self.client.get(
            reverse("orders:reorder_order", kwargs={"order_id": self.order.id})
        )
        self.assertEqual(response.status_code, 405)

    def test_reorder_skips_unavailable_products(self):
        self.product.available = False
        self.product.save(update_fields=["available"])
        response = self.client.post(
            reverse("orders:reorder_order", kwargs={"order_id": self.order.id})
        )
        self.assertRedirects(response, reverse("orders:cart_detail"))
        self.assertEqual(self.client.session.get("cart", {}), {})

    def test_reorder_requires_own_order(self):
        other = User.objects.create_user(
            username="otheruser", password="StrongPass123!"
        )
        order = Order.objects.create(
            user=other,
            customer_name="T",
            phone="0909",
            shipping_address="HCM",
            payment_method="cod",
            total_amount=100000,
            status="delivered",
            is_paid=True,
        )
        response = self.client.post(
            reverse("orders:reorder_order", kwargs={"order_id": order.id})
        )
        self.assertEqual(response.status_code, 404)


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    EMAIL_HOST="localhost",
)
class CartReminderTest(TestCase):
    def setUp(self):
        from django.core.cache import cache

        cache.clear()
        self.user = User.objects.create_user(
            username="remind_user", email="remind@test.com", password="StrongPass123!"
        )
        self.client.login(username="remind_user", password="StrongPass123!")
        self.cat = Category.objects.create(name="Áo", slug="ao")
        self.product = Product.objects.create(
            name="Áo reminder",
            slug="ao-reminder",
            category=self.cat,
            price=100000,
            stock=5,
        )

    def test_cart_detail_creates_reminder(self):
        cat = Category.objects.create(name="Phụ kiện", slug="phu-kien")
        product = Product.objects.create(
            name="Nón test", slug="non-test", category=cat, price=100000, stock=5
        )
        self.client.post(
            reverse("orders:cart_add", args=[product.id]),
            {"quantity": 1},
            follow=True,
        )
        resp = self.client.get(reverse("orders:cart_detail"))
        self.assertEqual(resp.status_code, 200)
        from orders.models import CartReminder

        reminder = CartReminder.objects.filter(
            session_key=self.client.session.session_key
        ).first()
        self.assertIsNotNone(reminder)
        self.assertEqual(reminder.email, "remind@test.com")
        self.assertIn("Nón test", reminder.cart_snapshot)

    def test_cart_clear_removes_reminder(self):
        from orders.models import CartReminder

        CartReminder.objects.create(
            session_key="dummy", email="x@test.com", cart_snapshot="[]"
        )
        self.client.session["cart"] = {}
        self.client.get(reverse("orders:cart_detail"))

        self.assertFalse(
            CartReminder.objects.filter(
                session_key=self.client.session.session_key
            ).exists()
        )

    def test_command_marks_reminded(self):
        from django.utils import timezone as tz

        from orders.models import CartReminder

        old = tz.now() - tz.timedelta(hours=4)
        reminder = CartReminder.objects.create(
            session_key="old_session",
            email="old@test.com",
            cart_snapshot='[{"name":"X","meta":"","quantity":1,"subtotal":100}]',
        )
        CartReminder.objects.filter(pk=reminder.pk).update(updated_at=old)
        reminder.refresh_from_db()
        self.assertIsNone(reminder.reminded_at)
        from django.core.management import call_command

        call_command("send_cart_reminders")
        reminder.refresh_from_db()
        self.assertIsNotNone(reminder.reminded_at)

    def test_celery_task_uses_the_supported_reminder_command(self):
        from django.utils import timezone as tz

        from orders.models import CartReminder
        from orders.tasks import send_cart_reminders

        reminder = CartReminder.objects.create(
            session_key="celery_old_session",
            email="celery-old@test.com",
            cart_snapshot='[{"name":"Áo","quantity":1,"subtotal":100000}]',
        )
        CartReminder.objects.filter(pk=reminder.pk).update(
            updated_at=tz.now() - tz.timedelta(hours=4)
        )

        result = send_cart_reminders.run()

        reminder.refresh_from_db()
        self.assertEqual(result, {"status": "completed"})
        self.assertIsNotNone(reminder.reminded_at)
