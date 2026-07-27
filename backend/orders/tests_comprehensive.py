from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils import timezone


class MockSession(dict):
    modified = False

from products.models import Category, Product, ProductVariant, WishlistItem
from users.models import UserProfile
from .cart import safe_int, add_cart, remove_cart, clear_cart, iter_cart, cart_count
from .constants import (
    BANKS, SHOP_BANK_ACCOUNT, SHOP_ACCOUNT_NAME,
    FREESHIP_THRESHOLD, STANDARD_SHIPPING_FEE, PAYMENT_TIMEOUT_MINUTES, BANK_CHOICES,
)
from .context_processors import cart_info as cart_info_fn
from .models import Coupon, Order, OrderItem
from .views import (
    build_vietqr_url, normalize_shipping_address, estimate_delivery_days,
    build_delivery_eta, decorate_order_tracking, calculate_shipping_fee,
    calculate_coupon_discount, validate_coupon, restore_order_stock,
    is_bank_order_expired, expire_bank_order_if_needed,
)



class SafeIntUnitTest(TestCase):
    def test_parses_valid_int(self):
        self.assertEqual(safe_int("5"), 5)

    def test_fallback_to_default(self):
        self.assertEqual(safe_int("abc"), 1)

    def test_minimum_clamp(self):
        self.assertEqual(safe_int("0"), 1)

    def test_custom_default_and_minimum(self):
        self.assertEqual(safe_int("abc", default=3, minimum=2), 3)

    def test_negative_clamped_to_minimum(self):
        self.assertEqual(safe_int("-5"), 1)

    def test_none_value(self):
        self.assertEqual(safe_int(None), 1)

    def test_float_string_truncated(self):
        self.assertEqual(safe_int("3.7"), 1)



class CartFunctionUnitTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get("/")
        self.request.session = MockSession()

        self.category = Category.objects.create(name="Phu kien", slug="phu-kien")
        self.product = Product.objects.create(
            category=self.category, name="Non test", slug="non-test",
            price=200000, stock=8, available=True,
        )

    def test_add_cart_new_item(self):
        add_cart(self.request, self.product.id, quantity=3)
        cart = self.request.session["cart"]
        key = f"{self.product.id}:0"
        self.assertIn(key, cart)
        self.assertEqual(cart[key]["quantity"], 3)
        self.assertEqual(cart[key]["price"], "200000")
        self.assertTrue(self.request.session.modified)

    def test_add_cart_multiple_times_accumulates(self):
        add_cart(self.request, self.product.id, quantity=2)
        add_cart(self.request, self.product.id, quantity=3)
        key = f"{self.product.id}:0"
        self.assertEqual(self.request.session["cart"][key]["quantity"], 5)

    def test_add_cart_quantity_clamped_to_stock(self):
        add_cart(self.request, self.product.id, quantity=99)
        key = f"{self.product.id}:0"
        self.assertEqual(self.request.session["cart"][key]["quantity"], 8)

    def test_add_cart_override_quantity(self):
        add_cart(self.request, self.product.id, quantity=2)
        add_cart(self.request, self.product.id, quantity=5, override_quantity=True)
        key = f"{self.product.id}:0"
        self.assertEqual(self.request.session["cart"][key]["quantity"], 5)

    def test_add_cart_unavailable_product(self):
        self.product.available = False
        self.product.save()
        result = add_cart(self.request, self.product.id)
        self.assertIsNone(result)
        self.assertEqual(self.request.session.get("cart", {}), {})

    def test_remove_cart_existing_item(self):
        add_cart(self.request, self.product.id)
        key = f"{self.product.id}:0"
        self.assertIn(key, self.request.session["cart"])
        remove_cart(self.request, item_key=key)
        self.assertNotIn(key, self.request.session["cart"])

    def test_remove_cart_non_existent_does_not_crash(self):
        remove_cart(self.request, item_key="99999:0")

    def test_clear_cart_removes_session_key(self):
        add_cart(self.request, self.product.id)
        clear_cart(self.request)
        self.assertNotIn("cart", self.request.session)

    def test_cart_count_zero_when_empty(self):
        self.assertEqual(cart_count(self.request), 0)

    def test_cart_count_after_adding(self):
        add_cart(self.request, self.product.id, quantity=3)
        self.assertEqual(cart_count(self.request), 3)

    def test_iter_cart_empty(self):
        rows, total = iter_cart(self.request)
        self.assertEqual(rows, [])
        self.assertEqual(total, Decimal("0"))

    def test_iter_cart_with_items(self):
        add_cart(self.request, self.product.id, quantity=2)
        rows, total = iter_cart(self.request)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["product"].id, self.product.id)
        self.assertEqual(rows[0]["quantity"], 2)
        self.assertEqual(rows[0]["price"], Decimal("200000"))
        self.assertEqual(rows[0]["subtotal"], Decimal("400000"))
        self.assertEqual(total, Decimal("400000"))

    def test_iter_cart_skips_unavailable_product(self):
        add_cart(self.request, self.product.id, quantity=1)
        self.product.available = False
        self.product.save()
        rows, total = iter_cart(self.request)
        self.assertEqual(rows, [])
        self.assertEqual(total, Decimal("0"))



class CouponModelUnitTest(TestCase):
    def setUp(self):
        self.coupon = Coupon.objects.create(
            code="TEST10", discount_type=Coupon.TYPE_PERCENT,
            value=Decimal("10"), min_order_amount=Decimal("0"),
            is_active=True,
        )

    def test_str_returns_code(self):
        self.assertEqual(str(self.coupon), "TEST10")

    def test_is_usable_now_active(self):
        self.assertTrue(self.coupon.is_usable_now())

    def test_is_usable_now_inactive(self):
        self.coupon.is_active = False
        self.assertFalse(self.coupon.is_usable_now())

    def test_is_usable_now_not_started(self):
        self.coupon.starts_at = timezone.now() + timedelta(days=1)
        self.assertFalse(self.coupon.is_usable_now())

    def test_is_usable_now_expired(self):
        self.coupon.ends_at = timezone.now() - timedelta(days=1)
        self.assertFalse(self.coupon.is_usable_now())

    def test_is_usable_now_usage_limit_reached(self):
        self.coupon.usage_limit = 5
        self.coupon.used_count = 5
        self.assertFalse(self.coupon.is_usable_now())

    def test_is_usable_now_usage_limit_not_reached(self):
        self.coupon.usage_limit = 5
        self.coupon.used_count = 4
        self.assertTrue(self.coupon.is_usable_now())

    def test_is_usable_now_within_date_range(self):
        self.coupon.starts_at = timezone.now() - timedelta(days=1)
        self.coupon.ends_at = timezone.now() + timedelta(days=1)
        self.assertTrue(self.coupon.is_usable_now())



class OrderModelUnitTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="buyer", password="pass")
        self.category = Category.objects.create(name="Ao", slug="ao")
        self.product = Product.objects.create(
            category=self.category, name="Ao test", slug="ao-test",
            price=300000, stock=10, available=True,
        )
        self.order = Order.objects.create(
            user=self.user, customer_name="Test", phone="0909",
            shipping_address="test", payment_method="cod",
            subtotal_amount=Decimal("300000"), total_amount=Decimal("330000"),
        )
        self.item = OrderItem.objects.create(
            order=self.order, product=self.product,
            quantity=2, price=Decimal("300000"),
        )

    def test_order_str(self):
        self.assertIn("buyer", str(self.order))

    def test_order_item_str(self):
        self.assertIn("Ao test", str(self.item))

    def test_order_item_subtotal(self):
        self.assertEqual(self.item.subtotal(), Decimal("600000"))

    def test_order_item_subtotal_single(self):
        item = OrderItem.objects.create(
            order=self.order, product=self.product,
            quantity=1, price=Decimal("150000"),
        )
        self.assertEqual(item.subtotal(), Decimal("150000"))



class CalculateShippingFeeUnitTest(TestCase):
    def test_free_when_at_threshold(self):
        self.assertEqual(calculate_shipping_fee(FREESHIP_THRESHOLD), Decimal("0"))

    def test_free_when_above_threshold(self):
        self.assertEqual(calculate_shipping_fee(FREESHIP_THRESHOLD + Decimal("1000")), Decimal("0"))

    def test_standard_when_below_threshold(self):
        self.assertEqual(calculate_shipping_fee(FREESHIP_THRESHOLD - Decimal("1000")), STANDARD_SHIPPING_FEE)

    def test_standard_when_zero(self):
        self.assertEqual(calculate_shipping_fee(Decimal("0")), STANDARD_SHIPPING_FEE)



class ValidateCouponUnitTest(TestCase):
    def setUp(self):
        self.coupon = Coupon.objects.create(
            code="GIAM20", discount_type=Coupon.TYPE_PERCENT,
            value=Decimal("20"), min_order_amount=Decimal("100000"),
            is_active=True,
        )

    def test_empty_code_returns_none(self):
        coupon, err = validate_coupon("", Decimal("500000"))
        self.assertIsNone(coupon)
        self.assertEqual(err, "")

    def test_none_code_returns_none(self):
        coupon, err = validate_coupon(None, Decimal("500000"))
        self.assertIsNone(coupon)
        self.assertEqual(err, "")

    def test_invalid_code_returns_error(self):
        coupon, err = validate_coupon("INVALID", Decimal("500000"))
        self.assertIsNone(coupon)
        self.assertIn("không tồn tại", err)

    def test_expired_coupon_returns_error(self):
        self.coupon.is_active = False
        self.coupon.save()
        coupon, err = validate_coupon("GIAM20", Decimal("500000"))
        self.assertIsNone(coupon)
        self.assertIn("hết hạn", err)

    def test_below_min_order_returns_error(self):
        coupon, err = validate_coupon("GIAM20", Decimal("50000"))
        self.assertIsNone(coupon)
        self.assertIn("tối thiểu", err)

    def test_valid_coupon_returns_coupon(self):
        coupon, err = validate_coupon("GIAM20", Decimal("500000"))
        self.assertIsNotNone(coupon)
        self.assertEqual(err, "")
        self.assertEqual(coupon.code, "GIAM20")



class CalculateCouponDiscountUnitTest(TestCase):
    def setUp(self):
        self.coupon = Coupon.objects.create(
            code="TEST", discount_type=Coupon.TYPE_PERCENT,
            value=Decimal("10"), is_active=True,
        )

    def test_none_coupon_returns_zero(self):
        self.assertEqual(calculate_coupon_discount(None, Decimal("100000"), Decimal("30000")), Decimal("0"))

    def test_percent_discount(self):
        self.assertEqual(calculate_coupon_discount(self.coupon, Decimal("200000"), Decimal("30000")), Decimal("20000"))

    def test_fixed_discount(self):
        self.coupon.discount_type = Coupon.TYPE_FIXED
        self.coupon.value = Decimal("50000")
        self.assertEqual(calculate_coupon_discount(self.coupon, Decimal("200000"), Decimal("30000")), Decimal("50000"))

    def test_freeship_discount(self):
        self.coupon.discount_type = Coupon.TYPE_FREESHIP
        self.assertEqual(calculate_coupon_discount(self.coupon, Decimal("200000"), Decimal("30000")), Decimal("30000"))

    def test_max_discount_amount_cap(self):
        self.coupon.max_discount_amount = Decimal("15000")
        self.assertEqual(calculate_coupon_discount(self.coupon, Decimal("200000"), Decimal("30000")), Decimal("15000"))

    def test_discount_not_exceed_subtotal_plus_shipping(self):
        self.coupon.discount_type = Coupon.TYPE_FIXED
        self.coupon.value = Decimal("999999")
        result = calculate_coupon_discount(self.coupon, Decimal("100000"), Decimal("30000"))
        self.assertEqual(result, Decimal("130000"))

    def test_discount_not_negative(self):
        self.coupon.discount_type = Coupon.TYPE_FIXED
        self.coupon.value = Decimal("-50000")
        result = calculate_coupon_discount(self.coupon, Decimal("100000"), Decimal("30000"))
        self.assertGreaterEqual(result, Decimal("0"))



class BuildVietQRUrlUnitTest(TestCase):
    def test_valid_bank_returns_url(self):
        url = build_vietqr_url("VCB", 150000, "DH123")
        self.assertIn("970436", url)
        self.assertIn(SHOP_BANK_ACCOUNT, url)
        self.assertIn("amount=150000", url)
        self.assertIn("DH123", url)

    def test_invalid_bank_returns_empty(self):
        self.assertEqual(build_vietqr_url("INVALID", 100000, "note"), "")

    def test_empty_bank_code_returns_empty(self):
        self.assertEqual(build_vietqr_url("", 100000, "note"), "")

    def test_all_banks_produce_valid_url(self):
        for code in BANKS:
            url = build_vietqr_url(code, 50000, "TEST")
            self.assertIn(BANKS[code]["bin"], url)



class EstimateDeliveryDaysUnitTest(TestCase):
    def test_hcm_address_returns_2(self):
        self.assertEqual(estimate_delivery_days("123, Quan 1, TP HCM"), 2)

    def test_near_hcm_address_returns_3(self):
        self.assertEqual(estimate_delivery_days("Binh Duong, Di An"), 3)

    def test_northern_address_returns_7(self):
        self.assertEqual(estimate_delivery_days("Ha Noi, Hoan Kiem"), 7)

    def test_other_address_returns_5(self):
        self.assertEqual(estimate_delivery_days("Da Nang, Son Tra"), 5)

    def test_hcm_variants_all_work(self):
        for keyword in ["ho chi minh", "sai gon", "thu duc", "go vap"]:
            with self.subTest(keyword=keyword):
                self.assertEqual(estimate_delivery_days(keyword), 2)



class BuildDeliveryEtaUnitTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="buyer", password="pass")
        self.order = Order.objects.create(
            user=self.user, customer_name="Test", phone="0909",
            shipping_address="Ha Noi", payment_method="cod",
            created_at=timezone.now(),
        )

    def test_eta_contains_required_keys(self):
        eta = build_delivery_eta(self.order)
        self.assertIn("eta_days", eta)
        self.assertIn("eta_date", eta)
        self.assertIn("eta_label", eta)

    def test_eta_label_includes_days(self):
        eta = build_delivery_eta(self.order)
        self.assertIn("ngày", eta["eta_label"])

    def test_eta_days_for_northern_address(self):
        eta = build_delivery_eta(self.order)
        self.assertEqual(eta["eta_days"], 7)

    def test_decorate_order_tracking_attaches_attrs(self):
        decorate_order_tracking(self.order)
        self.assertIsNotNone(self.order.eta_days)
        self.assertIsNotNone(self.order.eta_date)
        self.assertIsNotNone(self.order.eta_label)



class IsBankOrderExpiredUnitTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="buyer", password="pass")
        self.order = Order.objects.create(
            user=self.user, customer_name="Test", phone="0909",
            shipping_address="test", payment_method="bank",
            bank_code="VCB", status="processing", is_paid=False,
        )
        Order.objects.filter(id=self.order.id).update(
            created_at=timezone.now() - timedelta(minutes=PAYMENT_TIMEOUT_MINUTES + 1)
        )
        self.order.refresh_from_db()

    def test_not_bank_payment(self):
        self.order.payment_method = "cod"
        self.assertFalse(is_bank_order_expired(self.order))

    def test_already_paid(self):
        self.order.is_paid = True
        self.assertFalse(is_bank_order_expired(self.order))

    def test_not_processing(self):
        self.order.status = "pending"
        self.assertFalse(is_bank_order_expired(self.order))

    def test_expired_returns_true(self):
        self.assertTrue(is_bank_order_expired(self.order))

    def test_not_yet_expired(self):
        Order.objects.filter(id=self.order.id).update(created_at=timezone.now())
        self.order.refresh_from_db()
        self.assertFalse(is_bank_order_expired(self.order))



class RestoreOrderStockUnitTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="buyer", password="pass")
        self.category = Category.objects.create(name="Ao", slug="ao")
        self.product = Product.objects.create(
            category=self.category, name="Ao test", slug="ao-test",
            price=300000, stock=5, available=True,
        )
        self.variant = ProductVariant.objects.create(
            product=self.product, color_name="Den", color_code="#111",
            size="L", stock=3, is_active=True,
        )
        self.order = Order.objects.create(
            user=self.user, customer_name="Test", phone="0909",
            shipping_address="test", payment_method="cod",
        )
        self.item = OrderItem.objects.create(
            order=self.order, product=self.product,
            variant=self.variant, quantity=2, price=Decimal("300000"),
        )

    def test_restore_stock_for_variant_item(self):
        self.product.stock = 0
        self.product.save()
        self.variant.stock = 0
        self.variant.save()
        restore_order_stock(self.order)
        self.variant.refresh_from_db()
        self.product.refresh_from_db()
        self.assertEqual(self.variant.stock, 2)
        self.assertEqual(self.product.stock, 2)

    def test_restore_stock_for_non_variant_item(self):
        self.item.variant = None
        self.item.save()
        self.product.stock = 0
        self.product.save()
        restore_order_stock(self.order)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 2)



class BankPaymentStatusViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="buyer", password="pass")
        self.client.login(username="buyer", password="pass")
        self.order = Order.objects.create(
            user=self.user, customer_name="Test", phone="0909",
            shipping_address="test", payment_method="bank",
            bank_code="VCB", status="processing", is_paid=False,
            total_amount=150000,
        )

    def test_requires_login(self):
        self.client.logout()
        url = reverse("orders:bank_payment_status", kwargs={"order_id": self.order.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_returns_waiting_state_for_unpaid(self):
        response = self.client.get(
            reverse("orders:bank_payment_status", kwargs={"order_id": self.order.id})
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["state"], "waiting")
        self.assertFalse(data["is_paid"])

    def test_returns_success_state_when_paid(self):
        self.order.is_paid = True
        self.order.save()
        response = self.client.get(
            reverse("orders:bank_payment_status", kwargs={"order_id": self.order.id})
        )
        data = response.json()
        self.assertEqual(data["state"], "success")
        self.assertTrue(data["is_paid"])

    def test_returns_failed_state_when_cancelled(self):
        self.order.status = "cancelled"
        self.order.save()
        response = self.client.get(
            reverse("orders:bank_payment_status", kwargs={"order_id": self.order.id})
        )
        data = response.json()
        self.assertEqual(data["state"], "failed")

    def test_other_users_order_returns_404(self):
        other = User.objects.create_user(username="other", password="pass")
        self.client.login(username="other", password="pass")
        response = self.client.get(
            reverse("orders:bank_payment_status", kwargs={"order_id": self.order.id})
        )
        self.assertEqual(response.status_code, 404)

    def test_returns_json_content_type(self):
        response = self.client.get(
            reverse("orders:bank_payment_status", kwargs={"order_id": self.order.id})
        )
        self.assertEqual(response["Content-Type"], "application/json")



class OrderSuccessViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="buyer", password="pass")
        self.client.login(username="buyer", password="pass")
        self.category = Category.objects.create(name="Ao", slug="ao")
        self.product = Product.objects.create(
            category=self.category, name="Ao test", slug="ao-test",
            price=300000, stock=10, available=True,
        )

    def test_cod_order_renders_success_page(self):
        order = Order.objects.create(
            user=self.user, customer_name="Test", phone="0909",
            shipping_address="test", payment_method="cod",
            status="processing", subtotal_amount=Decimal("300000"),
            shipping_fee=Decimal("0"), total_amount=Decimal("300000"),
        )
        OrderItem.objects.create(
            order=order, product=self.product, quantity=1, price=Decimal("300000"),
        )
        response = self.client.get(
            reverse("orders:order_success", kwargs={"order_id": order.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Đặt hàng thành công")

    def test_unpaid_bank_order_redirects_to_waiting(self):
        order = Order.objects.create(
            user=self.user, customer_name="Test", phone="0909",
            shipping_address="test", payment_method="bank",
            bank_code="VCB", status="processing", is_paid=False,
            total_amount=300000,
        )
        response = self.client.get(
            reverse("orders:order_success", kwargs={"order_id": order.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("ngan-hang", response.url)

    def test_requires_login(self):
        order = Order.objects.create(
            user=self.user, customer_name="Test", phone="0909",
            shipping_address="test", payment_method="cod",
            total_amount=100000,
        )
        self.client.logout()
        response = self.client.get(
            reverse("orders:order_success", kwargs={"order_id": order.id})
        )
        self.assertEqual(response.status_code, 302)

    def test_other_users_order_returns_404(self):
        order = Order.objects.create(
            user=self.user, customer_name="Test", phone="0909",
            shipping_address="test", payment_method="cod",
            total_amount=100000,
        )
        other = User.objects.create_user(username="other", password="pass")
        self.client.login(username="other", password="pass")
        response = self.client.get(
            reverse("orders:order_success", kwargs={"order_id": order.id})
        )
        self.assertEqual(response.status_code, 404)



class OrderFailedViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="buyer", password="pass")
        self.client.login(username="buyer", password="pass")
        self.order = Order.objects.create(
            user=self.user, customer_name="Test", phone="0909",
            shipping_address="test", payment_method="bank",
            bank_code="VCB", status="cancelled", is_paid=False,
            total_amount=100000,
        )

    def test_renders_failed_page(self):
        response = self.client.get(
            reverse("orders:order_failed", kwargs={"order_id": self.order.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Đã hủy")

    def test_expired_reason_shown_when_note_contains_timeout(self):
        self.order.note = "[AUTO_TIMEOUT_15_MIN]"
        self.order.save()
        response = self.client.get(
            reverse("orders:order_failed", kwargs={"order_id": self.order.id})
        )
        self.assertContains(response, "15 phút")

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(
            reverse("orders:order_failed", kwargs={"order_id": self.order.id})
        )
        self.assertEqual(response.status_code, 302)

    def test_other_users_order_returns_404(self):
        other = User.objects.create_user(username="other", password="pass")
        self.client.login(username="other", password="pass")
        response = self.client.get(
            reverse("orders:order_failed", kwargs={"order_id": self.order.id})
        )
        self.assertEqual(response.status_code, 404)



class ProfileViewPostTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="buyer", email="old@test.com",
            password="StrongPass123!",
            first_name="Old", last_name="Name",
        )
        UserProfile.objects.create(user=self.user, phone_number="0909000000")
        self.client.login(username="buyer", password="StrongPass123!")

    def test_post_updates_name_and_email(self):
        response = self.client.post(
            reverse("users:profile"),
            {
                "first_name": "New",
                "last_name": "Name",
                "email": "new@test.com",
                "phone_number": "0909000000",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "New")
        self.assertEqual(self.user.email, "new@test.com")

    def test_post_updates_phone_number(self):
        response = self.client.post(
            reverse("users:profile"),
            {
                "first_name": "Buyer",
                "last_name": "Test",
                "email": "buyer@test.com",
                "phone_number": "0911222333",
            },
        )
        self.assertEqual(response.status_code, 302)
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.phone_number, "0911222333")

    def test_post_with_blank_phone_does_not_crash(self):
        response = self.client.post(
            reverse("users:profile"),
            {
                "first_name": "Buyer",
                "last_name": "Test",
                "email": "buyer@test.com",
                "phone_number": "",
            },
        )
        self.assertIn(response.status_code, (200, 302))

    def test_get_returns_form(self):
        response = self.client.get(reverse("users:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)
        self.assertIn("profile", response.context)
        self.assertIn("display_name", response.context)
        self.assertIn("display_initials", response.context)

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("users:profile"))
        self.assertEqual(response.status_code, 302)



class SecurityIsolationTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="pass1")
        self.user2 = User.objects.create_user(username="user2", password="pass2")
        self.category = Category.objects.create(name="Ao", slug="ao")
        self.product = Product.objects.create(
            category=self.category, name="Ao test", slug="ao-test",
            price=300000, stock=10, available=True,
        )

    def test_cannot_view_other_users_order_success(self):
        order = Order.objects.create(
            user=self.user1, customer_name="U1", phone="0909",
            shipping_address="test", payment_method="cod",
            total_amount=100000,
        )
        self.client.login(username="user2", password="pass2")
        response = self.client.get(
            reverse("orders:order_success", kwargs={"order_id": order.id})
        )
        self.assertEqual(response.status_code, 404)

    def test_cannot_view_other_users_order_failed(self):
        order = Order.objects.create(
            user=self.user1, customer_name="U1", phone="0909",
            shipping_address="test", payment_method="cod",
            total_amount=100000, status="cancelled",
        )
        self.client.login(username="user2", password="pass2")
        response = self.client.get(
            reverse("orders:order_failed", kwargs={"order_id": order.id})
        )
        self.assertEqual(response.status_code, 404)

    def test_cannot_view_other_users_order_review(self):
        order = Order.objects.create(
            user=self.user1, customer_name="U1", phone="0909",
            shipping_address="test", payment_method="cod",
            total_amount=100000,
        )
        self.client.login(username="user2", password="pass2")
        response = self.client.get(
            reverse("orders:order_review", kwargs={"order_id": order.id})
        )
        self.assertEqual(response.status_code, 404)

    def test_cannot_confirm_payment_for_other_users_order(self):
        order = Order.objects.create(
            user=self.user1, customer_name="U1", phone="0909",
            shipping_address="test", payment_method="bank",
            bank_code="VCB", status="processing", is_paid=False,
            total_amount=100000,
        )
        self.client.login(username="user2", password="pass2")
        response = self.client.post(
            reverse("orders:bank_payment_confirm", kwargs={"order_id": order.id})
        )
        self.assertEqual(response.status_code, 404)

    def test_admin_dashboard_blocks_non_staff(self):
        self.client.login(username="user1", password="pass1")
        response = self.client.get(reverse("orders:admin_dashboard"))
        self.assertEqual(response.status_code, 302)



class ProductModelUnitTest(TestCase):
    def setUp(self):
        self.ao_cat = Category.objects.create(name="Áo", slug="ao")
        self.pk_cat = Category.objects.create(name="Phụ kiện", slug="phu-kien")
        self.product_ao = Product.objects.create(
            category=self.ao_cat, name="Áo hoodie", slug="ao-hoodie",
            price=350000, stock=10, available=True,
        )
        self.product_pk = Product.objects.create(
            category=self.pk_cat, name="Mũ lưỡi trai", slug="mu-luoi-trai",
            price=150000, stock=20, available=True,
        )

    def test_product_str(self):
        self.assertEqual(str(self.product_ao), "Áo hoodie")

    def test_product_requires_variants_true_for_ao(self):
        self.assertTrue(self.product_ao.requires_variants)

    def test_product_requires_variants_false_for_pk(self):
        self.assertFalse(self.product_pk.requires_variants)

    def test_product_requires_variants_true_for_quan(self):
        quan_cat = Category.objects.create(name="Quần", slug="quan")
        product = Product.objects.create(
            category=quan_cat, name="Quần jogger", slug="quan-jogger",
            price=250000, stock=10, available=True,
        )
        self.assertTrue(product.requires_variants)

    def test_get_image_returns_placeholder_when_no_image(self):
        image = self.product_ao.get_image()
        self.assertIsNotNone(image)

    def test_get_image_returns_image_url_when_set(self):
        self.product_ao.image_url = "https://example.com/img.jpg"
        self.assertEqual(self.product_ao.get_image(), "https://example.com/img.jpg")

    def test_category_str(self):
        self.assertEqual(str(self.ao_cat), "Áo")

    def test_product_variant_str(self):
        variant = ProductVariant.objects.create(
            product=self.product_ao, color_name="Den",
            color_code="#111", size="L", stock=5, is_active=True,
        )
        self.assertIn("Áo hoodie", str(variant))
        self.assertIn("Den", str(variant))
        self.assertIn("L", str(variant))

    def test_model_meta_ordering_is_newest_first(self):
        self.assertEqual(Product._meta.ordering, ("-created",))



class ContextProcessorUnitTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.category = Category.objects.create(name="Ao", slug="ao")
        self.product = Product.objects.create(
            category=self.category, name="Ao test", slug="ao-test",
            price=200000, stock=10, available=True,
        )

    def test_cart_info_returns_zero_counts_for_guest(self):
        request = self.factory.get("/")
        request.session = MockSession()
        request.user = AnonymousUser()
        result = cart_info_fn(request)
        self.assertEqual(result["cart_item_count"], 0)
        self.assertEqual(result["wishlist_item_count"], 0)

    def test_cart_info_returns_cart_count(self):
        request = self.factory.get("/")
        request.session = MockSession({"cart": {f"{self.product.id}:0": {"quantity": 3, "price": "200000"}}})
        request.user = AnonymousUser()
        result = cart_info_fn(request)
        self.assertEqual(result["cart_item_count"], 3)

    def test_cart_info_returns_wishlist_count_for_auth_user(self):
        user = User.objects.create_user(username="buyer", password="pass")
        WishlistItem.objects.create(user=user, product=self.product)

        request = self.factory.get("/")
        request.session = MockSession()
        request.user = user
        result = cart_info_fn(request)
        self.assertEqual(result["cart_item_count"], 0)
        self.assertEqual(result["wishlist_item_count"], 1)



class NormalizeShippingAddressUnitTest(TestCase):
    def test_returns_lowercase_stripped_text(self):
        result = normalize_shipping_address("  Da Nang  ")
        self.assertIn("da nang", result)



class ExpireBankOrderIfNeededUnitTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="buyer", password="pass")
        self.category = Category.objects.create(name="Ao", slug="ao")
        self.product = Product.objects.create(
            category=self.category, name="Ao test", slug="ao-test",
            price=300000, stock=5, available=True,
        )
        self.variant = ProductVariant.objects.create(
            product=self.product, color_name="Den", color_code="#111",
            size="L", stock=3, is_active=True,
        )

    def test_does_not_expire_recent_order(self):
        order = Order.objects.create(
            user=self.user, customer_name="Test", phone="0909",
            shipping_address="test", payment_method="bank",
            bank_code="VCB", status="processing", is_paid=False,
            created_at=timezone.now(), total_amount=300000,
        )
        result = expire_bank_order_if_needed(order)
        self.assertFalse(result)

    def test_expires_old_order_and_restores_stock(self):
        order = Order.objects.create(
            user=self.user, customer_name="Test", phone="0909",
            shipping_address="test", payment_method="bank",
            bank_code="VCB", status="processing", is_paid=False,
            total_amount=300000,
        )
        Order.objects.filter(id=order.id).update(
            created_at=timezone.now() - timedelta(minutes=PAYMENT_TIMEOUT_MINUTES + 1)
        )
        order.refresh_from_db()
        OrderItem.objects.create(
            order=order, product=self.product,
            variant=self.variant, quantity=2, price=Decimal("300000"),
        )
        self.variant.stock = 1
        self.variant.save()

        result = expire_bank_order_if_needed(order)
        self.assertTrue(result)
        order.refresh_from_db()
        self.assertEqual(order.status, "cancelled")
        self.assertIn("AUTO_TIMEOUT_15_MIN", order.note)
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock, 3)



class ConstantsTest(TestCase):
    def test_banks_contains_expected_keys(self):
        expected = {"VCB", "TCB", "MB", "ACB", "BIDV", "VPB", "VIB", "HDB", "OCB", "MSB", "TPB", "SCB", "SHB", "LPB", "NAB", "SSB", "EIB", "STB", "DAB", "PGB", "BVB", "ABB", "KLB"}
        self.assertEqual(set(BANKS.keys()), expected)

    def test_bank_choices_has_empty_first_option(self):
        self.assertEqual(BANK_CHOICES[0], ("", "-- Chọn ngân hàng --"))

    def test_bank_choices_include_all_banks(self):
        self.assertEqual(len(BANK_CHOICES), len(BANKS) + 1)

    def test_constants_values(self):
        self.assertEqual(SHOP_BANK_ACCOUNT, "1234567890")
        self.assertEqual(SHOP_ACCOUNT_NAME, "HUUGIAU LOCAL BRAND")
        self.assertEqual(PAYMENT_TIMEOUT_MINUTES, 15)
        self.assertEqual(STANDARD_SHIPPING_FEE, Decimal("30000"))
        self.assertEqual(FREESHIP_THRESHOLD, Decimal("499000"))



class OrderReviewViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="buyer", password="pass")
        self.other = User.objects.create_user(username="other", password="pass")
        self.category = Category.objects.create(name="Ao", slug="ao")
        self.product = Product.objects.create(
            category=self.category, name="Ao test", slug="ao-test",
            price=300000, stock=10, available=True,
        )
        self.order = Order.objects.create(
            user=self.user, customer_name="Test", phone="0909",
            shipping_address="test", payment_method="bank",
            bank_code="VCB", status="processing", is_paid=False,
            total_amount=300000,
        )
        OrderItem.objects.create(
            order=self.order, product=self.product, quantity=1, price=Decimal("300000"),
        )

    def test_get_returns_200(self):
        self.client.login(username="buyer", password="pass")
        response = self.client.get(
            reverse("orders:order_review", kwargs={"order_id": self.order.id})
        )
        self.assertEqual(response.status_code, 200)

    def test_other_users_order_returns_404(self):
        self.client.login(username="other", password="pass")
        response = self.client.get(
            reverse("orders:order_review", kwargs={"order_id": self.order.id})
        )
        self.assertEqual(response.status_code, 404)

    def test_post_updates_order_info(self):
        self.client.login(username="buyer", password="pass")
        response = self.client.post(
            reverse("orders:order_review", kwargs={"order_id": self.order.id}),
            {"customer_name": "New Name", "customer_email": "new@test.com",
             "phone": "0911111111", "shipping_address": "new address",
             "note": "updated", "bank_code": "MB", "action": "pay_now"},
        )
        self.assertEqual(response.status_code, 302)
        self.order.refresh_from_db()
        self.assertEqual(self.order.customer_name, "New Name")
        self.assertEqual(self.order.bank_code, "MB")



class CartRemoveViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="buyer", password="pass")
        self.category = Category.objects.create(name="Phu kien", slug="phu-kien")
        self.product = Product.objects.create(
            category=self.category, name="Non test", slug="non-test",
            price=200000, stock=8, available=True,
        )

    def test_remove_single_item(self):
        self.client.login(username="buyer", password="pass")
        add_url = reverse("orders:cart_add", kwargs={"product_id": self.product.id})
        self.client.post(add_url, {"quantity": 1})
        cart = self.client.session.get("cart", {})
        key = f"{self.product.id}:0"
        self.assertIn(key, cart)

        remove_url = reverse("orders:cart_remove")
        self.client.post(remove_url, {"item_key": key})
        cart = self.client.session.get("cart", {})
        self.assertNotIn(key, cart)



class CartDetailViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="buyer", password="pass")
        self.category = Category.objects.create(name="Phu kien", slug="phu-kien")
        self.product = Product.objects.create(
            category=self.category, name="Non test", slug="non-test",
            price=200000, stock=8, available=True,
        )

    def test_freeship_applied_when_above_threshold(self):
        expensive = Product.objects.create(
            category=self.category, name="Tui test", slug="tui-test",
            price=500000, stock=5, available=True,
        )
        self.client.login(username="buyer", password="pass")
        self.client.post(
            reverse("orders:cart_add", kwargs={"product_id": expensive.id}),
            {"quantity": 1},
        )
        response = self.client.get(reverse("orders:cart_detail"))
        self.assertEqual(response.context["shipping_fee"], Decimal("0"))

    def test_empty_cart_still_renders(self):
        self.client.login(username="buyer", password="pass")
        response = self.client.get(reverse("orders:cart_detail"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["subtotal"], Decimal("0"))
