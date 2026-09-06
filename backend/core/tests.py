from django.test import TestCase, override_settings
from django.urls import reverse

from core.ratelimit import rate_limit


class ErrorPageTest(TestCase):
    def test_404_page_renders(self):
        response = self.client.get("/khong-ton-tai/")
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")

    def test_500_page_renders(self):
        from django.template.loader import render_to_string

        rendered = render_to_string("500.html")
        self.assertIn("500", rendered)
        self.assertIn("HUUGIAU", rendered)


class SeoTest(TestCase):
    def test_robots_txt(self):
        response = self.client.get(reverse("robots_txt"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain")
        self.assertIn(b"Disallow: /admin-dashboard/", response.content)

    def test_sitemap_xml(self):
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/xml")
        self.assertIn(b"<urlset", response.content)

    def test_sitemap_includes_available_products(self):
        from products.models import Category, Product

        category = Category.objects.create(name="Áo", slug="ao")
        Product.objects.create(
            category=category,
            name="SP sitemap",
            slug="sp-sitemap",
            price=100000,
            stock=5,
            available=True,
        )
        Product.objects.create(
            category=category,
            name="SP ẩn",
            slug="sp-an",
            price=100000,
            stock=0,
            available=False,
        )
        response = self.client.get("/sitemap.xml")
        self.assertIn(b"sp-sitemap", response.content)
        self.assertNotIn(b"sp-an", response.content)


class CSPMiddlewareTest(TestCase):
    @override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver"])
    def test_csp_header_added_in_production(self):
        response = self.client.get(reverse("products:product_list"))
        self.assertIn("Content-Security-Policy", response.headers)
        csp = response.headers["Content-Security-Policy"]
        self.assertIn("default-src 'self'", csp)
        self.assertIn("img-src 'self' data: https:", csp)
        # CSP now uses nonce instead of unsafe-inline
        self.assertIn("style-src 'self' 'nonce-", csp)
        self.assertIn("script-src 'self' 'nonce-", csp)

    @override_settings(DEBUG=True)
    def test_csp_header_omitted_in_debug(self):
        response = self.client.get(reverse("products:product_list"))
        self.assertNotIn("Content-Security-Policy", response.headers)


class RateLimitTest(TestCase):
    def test_rate_limit_decorator_applies(self):
        self.assertTrue(callable(rate_limit))

    def test_rate_limiter_allows_under_limit(self):
        from core.ratelimit import RateLimiter
        from django.test import RequestFactory

        limiter = RateLimiter("test", max_requests=5, window=60)
        factory = RequestFactory()
        request = factory.get("/test/")
        for _ in range(5):
            self.assertTrue(limiter.is_allowed(request))

    def test_rate_limiter_blocks_over_limit(self):
        from core.ratelimit import RateLimiter
        from django.test import RequestFactory

        limiter = RateLimiter("test_block", max_requests=3, window=60)
        factory = RequestFactory()
        request = factory.get("/test/")
        for _ in range(3):
            self.assertTrue(limiter.is_allowed(request))
            limiter._record_hit(request)
        self.assertFalse(limiter.is_allowed(request))

    def test_rate_limiter_get_remaining_returns_correct(self):
        from core.ratelimit import RateLimiter
        from django.test import RequestFactory

        limiter = RateLimiter("remaining", max_requests=5, window=60)
        factory = RequestFactory()
        request = factory.get("/test/")
        self.assertEqual(limiter.get_remaining(request), 5)
        limiter._record_hit(request)
        self.assertEqual(limiter.get_remaining(request), 4)


class CacheSystemTest(TestCase):
    def test_locmem_cache_works(self):
        from django.core.cache import cache

        cache.set("test_key", "test_value", 10)
        self.assertEqual(cache.get("test_key"), "test_value")

    def test_cache_key_expires(self):
        from django.core.cache import cache

        cache.set("expire_key", "value", 1)
        self.assertEqual(cache.get("expire_key"), "value")


class LoginRateLimitIntegrationTest(TestCase):
    def setUp(self):
        from django.core.cache import cache

        cache.clear()
        from django.contrib.auth.models import User

        User.objects.create_user(username="testuser", password="StrongPass123!")

    def test_login_rate_limit_blocks_after_10_failures(self):
        from django.core.cache import cache

        cache.clear()
        for _ in range(10):
            response = self.client.post(
                "/dang-nhap/", {"username": "testuser", "password": "wrong"}
            )
            self.assertEqual(response.status_code, 200)
        response = self.client.post(
            "/dang-nhap/", {"username": "testuser", "password": "wrong"}
        )
        self.assertEqual(response.status_code, 403)

    def test_login_rate_limit_resets_after_success(self):
        from django.core.cache import cache

        cache.clear()
        for _ in range(5):
            self.client.post(
                "/dang-nhap/", {"username": "testuser", "password": "wrong"}
            )
        response = self.client.post(
            "/dang-nhap/", {"username": "testuser", "password": "StrongPass123!"}
        )
        self.assertEqual(response.status_code, 302)

    def test_login_rate_limit_blocks_same_ip_after_limit(self):
        from django.core.cache import cache

        cache.clear()
        for _ in range(10):
            self.client.post(
                "/dang-nhap/", {"username": "testuser", "password": "wrong"}
            )
        response = self.client.post(
            "/dang-nhap/", {"username": "testuser", "password": "StrongPass123!"}
        )
        self.assertEqual(response.status_code, 403)

    @override_settings(TRUSTED_PROXY=True)
    def test_login_allows_different_ip_after_rate_limit(self):
        from django.core.cache import cache

        cache.clear()
        for _ in range(10):
            self.client.post(
                "/dang-nhap/", {"username": "testuser", "password": "wrong"}
            )
        response = self.client.post(
            "/dang-nhap/",
            {"username": "testuser", "password": "StrongPass123!"},
            HTTP_X_FORWARDED_FOR="10.0.0.1",
        )
        self.assertEqual(response.status_code, 302)


class ApiTest(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User

        self.user = User.objects.create_user(
            username="buyer", password="StrongPass123!"
        )
        self.staff = User.objects.create_user(
            username="adminstaff", password="StrongPass123!", is_staff=True
        )

        from products.models import Category, Product

        self.category = Category.objects.create(name="Ao", slug="ao")
        self.product = Product.objects.create(
            category=self.category,
            name="Ao hoodie API",
            slug="ao-hoodie-api",
            price=500000,
            stock=10,
            available=True,
        )
        from products.models import Review

        self.review = Review.objects.create(
            product=self.product, user=self.user, rating=5, comment="Dep qua"
        )
        Review.objects.create(
            product=self.product,
            user=self.staff,
            rating=2,
            comment="Kem",
            is_published=False,
        )

        from orders.models import Coupon, Order, OrderItem

        self.coupon = Coupon.objects.create(
            code="APISALE",
            discount_type=Coupon.TYPE_PERCENT,
            value=10,
            min_order_amount=0,
            is_active=True,
        )
        self.order = Order.objects.create(
            user=self.user,
            customer_name="Nguyen Van A",
            phone="0901234567",
            shipping_address="Quan 1, TP HCM",
            payment_method="cod",
            subtotal_amount=500000,
            shipping_fee=30000,
            discount_amount=0,
            total_amount=530000,
        )
        OrderItem.objects.create(
            order=self.order, product=self.product, quantity=1, price=500000
        )

    def test_api_root(self):
        response = self.client.get(reverse("api:api_root"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "HUUGIAU Fashion API")

    def test_api_products_list(self):
        response = self.client.get(reverse("api:api_product_list"))
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["results"][0]["name"], "Ao hoodie API")
        self.assertEqual(payload["results"][0]["rating_avg"], 5.0)

    def test_api_products_filter_invalid_category_returns_empty(self):
        response = self.client.get(
            reverse("api:api_product_list"), {"category": "khong-co"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 0)

    def test_api_products_search(self):
        response = self.client.get(reverse("api:api_product_list"), {"q": "hoodie"})
        self.assertEqual(response.json()["count"], 1)

    def test_api_product_detail(self):
        response = self.client.get(
            reverse("api:api_product_detail", kwargs={"pk": self.product.id})
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["rating_count"], 1)
        self.assertEqual(len(payload["reviews"]), 1)
        self.assertEqual(payload["reviews"][0]["rating"], 5)

    def test_api_product_reviews_only_published(self):
        response = self.client.get(
            reverse("api:api_product_reviews", kwargs={"pk": self.product.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)

    def test_api_review_submit_requires_login(self):
        response = self.client.post(
            reverse("api:api_review_submit", kwargs={"pk": self.product.id}),
            {"rating": 4, "comment": "OK"},
        )
        self.assertEqual(response.status_code, 302)

    def test_api_review_submit_creates_review_and_blocks_duplicate(self):
        from django.contrib.auth.models import User
        from products.models import Review

        fresh = User.objects.create_user(
            username="freshbuyer", password="StrongPass123!"
        )
        self.client.login(username="freshbuyer", password="StrongPass123!")

        url = reverse("api:api_review_submit", kwargs={"pk": self.product.id})
        response = self.client.post(url, {"rating": 4, "comment": "Moi"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["review"]["rating"], 4)
        self.assertEqual(
            Review.objects.filter(product=self.product, user=fresh).count(), 1
        )

        duplicate = self.client.post(url, {"rating": 3, "comment": "Lan nua"})
        self.assertEqual(duplicate.status_code, 409)

    def test_api_review_submit_rejects_bad_rating(self):
        self.client.login(username="buyer", password="StrongPass123!")
        response = self.client.post(
            reverse("api:api_review_submit", kwargs={"pk": self.product.id}),
            {"rating": 9, "comment": "Sai"},
        )
        self.assertEqual(response.status_code, 400)

    def test_api_categories(self):
        response = self.client.get(reverse("api:api_categories"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["product_count"], 1)

    def test_api_my_orders_requires_login(self):
        response = self.client.get(reverse("api:api_my_orders"))
        self.assertEqual(response.status_code, 302)

    def test_api_my_orders_lists_own(self):
        self.client.login(username="buyer", password="StrongPass123!")
        response = self.client.get(reverse("api:api_my_orders"))
        self.assertEqual(response.status_code, 200)
        orders = response.json()
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0]["total_amount"], 530000)

    def test_api_order_detail_owner_only(self):
        from django.contrib.auth.models import User

        User.objects.create_user(username="stranger", password="StrongPass123!")
        self.client.login(username="stranger", password="StrongPass123!")
        response = self.client.get(
            reverse("api:api_order_detail", kwargs={"pk": self.order.id})
        )
        self.assertEqual(response.status_code, 404)

    def test_api_order_detail_staff_can_view(self):
        self.client.login(username="adminstaff", password="StrongPass123!")
        response = self.client.get(
            reverse("api:api_order_detail", kwargs={"pk": self.order.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["items"]), 1)

    def test_api_order_lookup_found_and_not_found(self):
        response = self.client.post(
            reverse("api:api_order_lookup"),
            {"order_id": self.order.id, "phone": "0901234567"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], self.order.id)

        response = self.client.post(
            reverse("api:api_order_lookup"),
            {"order_id": self.order.id, "phone": "0000000000"},
        )
        self.assertEqual(response.status_code, 404)

    def test_api_coupon_check(self):
        self.client.login(username="buyer", password="StrongPass123!")
        response = self.client.post(
            reverse("api:api_coupon_check"), {"code": "APISALE"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["discount_type"], "percent")

        response = self.client.post(
            reverse("api:api_coupon_check"), {"code": "KHONGTONTAI"}
        )
        self.assertEqual(response.status_code, 404)

    def test_api_admin_requires_staff(self):
        self.client.login(username="buyer", password="StrongPass123!")
        response = self.client.get(reverse("api:api_admin_stats"))
        self.assertEqual(response.status_code, 403)

    def test_api_admin_stats(self):
        self.client.login(username="adminstaff", password="StrongPass123!")
        response = self.client.get(reverse("api:api_admin_stats"))
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("total_orders", payload)
        self.assertEqual(payload["total_orders"], 1)

    def test_api_admin_orders_and_detail(self):
        self.client.login(username="adminstaff", password="StrongPass123!")
        response = self.client.get(reverse("api:api_admin_orders"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)

        response = self.client.get(
            reverse("api:api_admin_order_detail", kwargs={"pk": self.order.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["items"]), 1)

    def test_api_admin_order_status_change(self):
        self.client.login(username="adminstaff", password="StrongPass123!")
        response = self.client.post(
            reverse("api:api_admin_order_status", kwargs={"pk": self.order.id}),
            {"status": "shipping"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "shipping")

    def test_api_admin_order_refund(self):
        self.client.login(username="adminstaff", password="StrongPass123!")
        self.order.status = "delivered"
        self.order.is_paid = True
        self.order.save()
        response = self.client.post(
            reverse("api:api_admin_order_refund", kwargs={"pk": self.order.id})
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["refunded"])
        self.assertEqual(payload["status"], "cancelled")

    def test_api_admin_invoice(self):
        self.client.login(username="adminstaff", password="StrongPass123!")
        response = self.client.get(
            reverse("api:api_admin_invoice", kwargs={"pk": self.order.id})
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("shop", payload)
        self.assertEqual(len(payload["items"]), 1)

    def test_api_admin_export(self):
        self.client.login(username="adminstaff", password="StrongPass123!")
        response = self.client.get(reverse("api:api_admin_export"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_api_admin_products_users_coupons(self):
        self.client.login(username="adminstaff", password="StrongPass123!")
        self.assertEqual(
            self.client.get(reverse("api:api_admin_products")).status_code, 200
        )
        self.assertEqual(
            self.client.get(reverse("api:api_admin_users")).status_code, 200
        )
        response = self.client.get(reverse("api:api_admin_coupons"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["code"], "APISALE")

    def test_api_admin_reviews_moderate(self):
        self.client.login(username="adminstaff", password="StrongPass123!")
        url = reverse("api:api_admin_reviews")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 2)

        response = self.client.post(
            url, {"review_id": self.review.id, "is_published": "0"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["is_published"])

        response = self.client.get(
            reverse("api:api_product_reviews", kwargs={"pk": self.product.id})
        )
        self.assertEqual(response.json()["count"], 0)


class InvoicePrintTest(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User

        self.staff = User.objects.create_user(
            username="boss", password="StrongPass123!", is_staff=True
        )
        self.user = User.objects.create_user(
            username="nobody", password="StrongPass123!"
        )

        from products.models import Category, Product

        category = Category.objects.create(name="Phu kien", slug="phu-kien")
        product = Product.objects.create(
            category=category,
            name="Non",
            slug="non",
            price=200000,
            stock=5,
            available=True,
        )
        from orders.models import Order, OrderItem

        self.order = Order.objects.create(
            user=self.user,
            customer_name="Le Van B",
            phone="0987654321",
            shipping_address="Ha Noi",
            payment_method="cod",
            subtotal_amount=200000,
            shipping_fee=30000,
            discount_amount=0,
            total_amount=230000,
        )
        OrderItem.objects.create(
            order=self.order, product=product, quantity=1, price=200000
        )

    def test_print_invoice_requires_staff(self):
        self.client.login(username="nobody", password="StrongPass123!")
        response = self.client.get(
            reverse("orders:admin_print_invoice", kwargs={"order_id": self.order.id})
        )
        self.assertEqual(response.status_code, 404)

    def test_print_invoice_renders_for_staff(self):
        self.client.login(username="boss", password="StrongPass123!")
        response = self.client.get(
            reverse("orders:admin_print_invoice", kwargs={"order_id": self.order.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "HOÁ ĐƠN")
        self.assertContains(response, "230.000")
        self.assertContains(response, "DH{}".format(self.order.id))
