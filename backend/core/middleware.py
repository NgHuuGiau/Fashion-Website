import secrets
import logging

from django.conf import settings
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from core.ratelimit import RateLimiter

logger = logging.getLogger(__name__)


class CSPNonceMiddleware(MiddlewareMixin):
    """Generate CSP nonce per request and attach to request object."""

    def process_request(self, request):
        request.csp_nonce = secrets.token_urlsafe(16)


class CSPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if not getattr(settings, "DEBUG", False):
            nonce = getattr(request, "csp_nonce", secrets.token_urlsafe(16))
            nonce_attr = f"'nonce-{nonce}'"
            response["Content-Security-Policy"] = (
                "default-src 'self'; "
                "img-src 'self' data: https:; "
                f"style-src 'self' {nonce_attr} https://fonts.googleapis.com; "
                f"script-src 'self' {nonce_attr} https://www.googletagmanager.com; "
                "frame-src 'self' https://img.vietqr.io https://www.google.com/maps; "
                "connect-src 'self' https://nominatim.openstreetmap.org https://www.google-analytics.com https://www.googletagmanager.com"
            )
        return response


class ApiRateLimitMiddleware:
    """Bound write traffic for every JSON API endpoint, including plain Django views."""

    METHODS = {"POST", "PUT", "PATCH", "DELETE"}

    def __init__(self, get_response):
        self.get_response = get_response
        self.limiter = RateLimiter("api", max_requests=120, window=60)

    def __call__(self, request):
        if request.path.startswith("/api/") and request.method in self.METHODS:
            try:
                if not self.limiter.consume(request):
                    return self.limiter.get_response(request)
            except Exception:
                logger.exception("Global API rate-limit cache unavailable")
                if not settings.DEBUG:
                    return JsonResponse(
                        {"error": "Dịch vụ tạm thời không khả dụng."}, status=503
                    )
        return self.get_response(request)
