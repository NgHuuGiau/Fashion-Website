from django.conf import settings


class CSPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if not getattr(settings, "DEBUG", False):
            response["Content-Security-Policy"] = (
                "default-src 'self'; "
                "img-src 'self' data: https:; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://www.googletagmanager.com; "
                "frame-src 'self' https://img.vietqr.io https://www.google.com/maps; "
                "connect-src 'self' https://nominatim.openstreetmap.org https://www.google-analytics.com https://www.googletagmanager.com"
            )
        return response
