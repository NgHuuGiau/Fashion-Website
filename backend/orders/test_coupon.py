from datetime import timedelta
from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from products.models import Category, Product, ProductVariant
from .models import Coupon, Order, OrderItem


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
        coupon = Coupon.objects.create(
            code="STRTEST", discount_type="percent", value=10, is_active=True
        )
        self.assertEqual(str(coupon), "STRTEST")

    def test_order_str(self):
        user = User.objects.create_user(username="ostr", password="StrongPass123!")
        order = Order.objects.create(
            user=user,
            customer_name="T",
            phone="0909",
            shipping_address="HCM",
            payment_method="cod",
            total_amount=100000,
        )
        self.assertIn("Order", str(order))

    def test_order_item_str_and_subtotal(self):
        category = Category.objects.create(name="Ao", slug="ao")
        product = Product.objects.create(
            category=category,
            name="Ao subtotal",
            slug="ao-subtotal",
            price=200000,
            stock=5,
            available=True,
        )
        user = User.objects.create_user(username="oitem", password="StrongPass123!")
        order = Order.objects.create(
            user=user,
            customer_name="T",
            phone="0909",
            shipping_address="HCM",
            payment_method="cod",
            total_amount=200000,
        )
        item = OrderItem.objects.create(
            order=order, product=product, quantity=2, price=200000
        )
        self.assertEqual(str(item), "2 x Ao subtotal")
        self.assertEqual(item.subtotal(), Decimal("400000"))


class CouponDiscountMathTest(TestCase):
    def setUp(self):
        self.coupon_percent = Coupon.objects.create(
            code="P", discount_type="percent", value=Decimal("10"), is_active=True
        )
        self.coupon_fixed = Coupon.objects.create(
            code="F", discount_type="fixed", value=Decimal("50000"), is_active=True
        )
        self.coupon_freeship = Coupon.objects.create(
            code="S", discount_type="freeship", value=Decimal("0"), is_active=True
        )

    def test_shipping_fee_threshold(self):
        from .views.cart import calculate_shipping_fee

        self.assertEqual(calculate_shipping_fee(Decimal("499000")), Decimal("0"))
        self.assertEqual(calculate_shipping_fee(Decimal("100000")), Decimal("30000"))

    def test_coupon_discount_branches(self):
        from .views.cart import calculate_coupon_discount

        self.assertEqual(
            calculate_coupon_discount(None, Decimal("200000"), Decimal("30000")),
            Decimal("0"),
        )
        self.assertEqual(
            calculate_coupon_discount(
                self.coupon_percent, Decimal("200000"), Decimal("30000")
            ),
            Decimal("20000"),
        )
        self.assertEqual(
            calculate_coupon_discount(
                self.coupon_fixed, Decimal("200000"), Decimal("30000")
            ),
            Decimal("50000"),
        )
        self.assertEqual(
            calculate_coupon_discount(
                self.coupon_freeship, Decimal("200000"), Decimal("30000")
            ),
            Decimal("30000"),
        )

    def test_coupon_max_discount_cap(self):
        from .views.cart import calculate_coupon_discount

        self.coupon_fixed.max_discount_amount = Decimal("10000")
        self.assertEqual(
            calculate_coupon_discount(
                self.coupon_fixed, Decimal("200000"), Decimal("30000")
            ),
            Decimal("10000"),
        )

    def test_coupon_discount_never_negative(self):
        from .views.cart import calculate_coupon_discount

        self.coupon_fixed.value = Decimal("999999")
        result = calculate_coupon_discount(
            self.coupon_fixed, Decimal("100000"), Decimal("30000")
        )
        self.assertGreaterEqual(result, Decimal("0"))


class CouponPerUserTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="couponuser", password="StrongPass123!"
        )
        self.client.login(username="couponuser", password="StrongPass123!")
        self.category = Category.objects.create(name="Ao", slug="ao")
        self.product = Product.objects.create(
            category=self.category,
            name="Ao coupon",
            slug="ao-coupon",
            price=500000,
            stock=10,
            available=True,
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
            product=self.product,
            color_name="Den",
            color_code="#111111",
            size="L",
            stock=5,
            is_active=True,
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


class P3StackingPriceTest(TestCase):
    """Bao phu P3: policy cong don + lich su gia + service pricing."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="buyer", password="StrongPass123!"
        )
        self.category = Category.objects.create(name="Ao", slug="ao")
        self.product = Product.objects.create(
            category=self.category,
            name="Ao test",
            slug="ao-test",
            price=500000,
            stock=20,
            available=True,
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            color_name="Den",
            color_code="#111111",
            size="L",
            stock=10,
            is_active=True,
        )
        self.exclusive = Coupon.objects.create(
            code="DOCQUYEN",
            discount_type=Coupon.TYPE_FIXED,
            value=Decimal("50000"),
            is_active=True,
            stackable=False,
        )

    def test_service_exclusive_zeroes_tier_and_points(self):
        import types

        from orders.services.checkout import apply_stacking_policy

        stub = types.SimpleNamespace(stackable=False)
        tier, pts_use, pts_disc, total = apply_stacking_policy(
            coupon=stub,
            subtotal=Decimal("1000000"),
            shipping_fee=Decimal("30000"),
            discount_amount=Decimal("50000"),
            tier_discount_amount=Decimal("50000"),
            points_to_use=100,
            points_discount=Decimal("10000"),
        )
        self.assertEqual(tier, Decimal("0"))
        self.assertEqual(pts_use, 0)
        self.assertEqual(pts_disc, Decimal("0"))
        self.assertEqual(total, Decimal("980000"))

    def test_service_cap_trims_points_first(self):
        from orders.services.checkout import apply_stacking_policy

        tier, pts_use, pts_disc, total = apply_stacking_policy(
            coupon=None,
            subtotal=Decimal("100000"),
            shipping_fee=Decimal("0"),
            discount_amount=Decimal("0"),
            tier_discount_amount=Decimal("40000"),
            points_to_use=500,
            points_discount=Decimal("50000"),
        )
        # cap 50% = 50000: cat 40000 diem truoc, giu 10000 diem + 40000 hang
        self.assertEqual(pts_disc, Decimal("10000"))
        self.assertEqual(pts_use, 100)
        self.assertEqual(tier, Decimal("40000"))
        self.assertEqual(total, Decimal("50000"))

    def test_checkout_exclusive_coupon_skips_tier_and_points(self):
        from users.models import UserProfile

        profile, _ = UserProfile.objects.get_or_create(user=self.user)
        profile.points = 2000
        profile.save(update_fields=["points"])
        self.client.login(username="buyer", password="StrongPass123!")
        self.client.post(
            reverse("orders:cart_add", kwargs={"product_id": self.product.id}),
            {"quantity": 1, "variant_id": self.variant.id},
        )
        response = self.client.post(
            reverse("orders:checkout"),
            {
                "customer_name": "Buyer",
                "phone": "0909000000",
                "shipping_address": "1 Test Street",
                "payment_method": "cod",
                "coupon_code": "DOCQUYEN",
                "points_to_use": 500,
            },
        )
        self.assertEqual(response.status_code, 302)
        order = Order.objects.get()
        self.assertEqual(order.coupon_code, "DOCQUYEN")
        self.assertEqual(order.discount_amount, Decimal("50000"))
        self.assertEqual(order.points_used, 0)
        profile.refresh_from_db()
        self.assertEqual(profile.points, 2000)

    def test_price_history_recorded_on_change_only(self):
        from products.models import PriceHistory

        self.product.price = 600000
        self.product.save()
        entry = PriceHistory.objects.get(product=self.product)
        self.assertEqual(entry.old_price, 500000)
        self.assertEqual(entry.new_price, 600000)
        # save chi stock thi khong ghi lich su
        self.product.save(update_fields=["stock"])
        self.assertEqual(PriceHistory.objects.count(), 1)
