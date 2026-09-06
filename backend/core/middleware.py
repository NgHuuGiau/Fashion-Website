import secrets
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


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
