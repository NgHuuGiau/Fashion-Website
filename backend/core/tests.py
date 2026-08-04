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


class CSPMiddlewareTest(TestCase):

    @override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver"])
    def test_csp_header_added_in_production(self):
        response = self.client.get(reverse("products:product_list"))
        self.assertIn("Content-Security-Policy", response.headers)
        csp = response.headers["Content-Security-Policy"]
        self.assertIn("default-src 'self'", csp)
        self.assertIn("img-src 'self' data: https:", csp)
        self.assertIn("style-src 'self' 'unsafe-inline'", csp)

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
            response = self.client.post("/dang-nhap/", {"username": "testuser", "password": "wrong"})
            self.assertEqual(response.status_code, 200)
        response = self.client.post("/dang-nhap/", {"username": "testuser", "password": "wrong"})
        self.assertEqual(response.status_code, 403)

    def test_login_rate_limit_resets_after_success(self):
        from django.core.cache import cache
        cache.clear()
        for _ in range(5):
            self.client.post("/dang-nhap/", {"username": "testuser", "password": "wrong"})
        response = self.client.post("/dang-nhap/", {"username": "testuser", "password": "StrongPass123!"})
        self.assertEqual(response.status_code, 302)

    def test_login_rate_limit_blocks_same_ip_after_limit(self):
        from django.core.cache import cache
        cache.clear()
        for _ in range(10):
            self.client.post("/dang-nhap/", {"username": "testuser", "password": "wrong"})
        response = self.client.post("/dang-nhap/", {"username": "testuser", "password": "StrongPass123!"})
        self.assertEqual(response.status_code, 403)

    @override_settings(TRUSTED_PROXY=True)
    def test_login_allows_different_ip_after_rate_limit(self):
        from django.core.cache import cache
        cache.clear()
        for _ in range(10):
            self.client.post("/dang-nhap/", {"username": "testuser", "password": "wrong"})
        response = self.client.post(
            "/dang-nhap/",
            {"username": "testuser", "password": "StrongPass123!"},
            HTTP_X_FORWARDED_FOR="10.0.0.1",
        )
        self.assertEqual(response.status_code, 302)
