from django.shortcuts import redirect

from core.ratelimit import get_client_ip

from .activity import log_activity
from .models import VisitorSession


class Admin2FAMiddleware:
    """Bat staff xac minh TOTP khi vao /admin/.

    - Chua co thiet bi: chuyen toi trang dang ky.
    - Co thiet bi nhung session chua verify OTP: chuyen toi trang nhap ma.
    """

    ADMIN_PREFIX = "/admin/"
    EXEMPT_NAMES = {
        "twofa_enroll",
        "twofa_verify",
        "twofa_disable",
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._protected(request):
            from django_otp.plugins.otp_totp.models import TOTPDevice

            has_device = TOTPDevice.objects.filter(
                user=request.user, confirmed=True
            ).exists()
            if not has_device:
                return redirect("users:twofa_enroll")
            if not request.user.is_verified():
                return redirect("users:twofa_verify")
        return self.get_response(request)

    def _protected(self, request):
        if not request.path.startswith(self.ADMIN_PREFIX):
            return False
        user = getattr(request, "user", None)
        if user is None or not user.is_authenticated or not user.is_staff:
            return False
        from django.urls import resolve

        try:
            if resolve(request.path_info).url_name in self.EXEMPT_NAMES:
                return False
        except Exception:
            pass
        return True


class VisitorTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.session.session_key:
            request.session.save()

        request.visitor_session = self._bind_visitor(request)
        response = self.get_response(request)

        if not request.path.startswith("/static/") and not request.path.startswith(
            "/media/"
        ):
            event_type = "page_view" if request.method == "GET" else "action"
            log_activity(
                request,
                event_type=event_type,
                metadata={},
                status_code=getattr(response, "status_code", 200),
            )

        return response

    def _bind_visitor(self, request):
        session_key = request.session.session_key
        ip = self._get_ip(request)
        ua = request.META.get("HTTP_USER_AGENT", "")[:500]
        user = request.user if request.user.is_authenticated else None

        visitor, _ = VisitorSession.objects.get_or_create(
            session_key=session_key,
            defaults={
                "user": user,
                "is_authenticated": bool(user),
                "ip_address": ip,
                "user_agent": ua,
            },
        )

        changed = False
        if visitor.user_id != (user.id if user else None):
            visitor.user = user
            changed = True

        is_auth = bool(user)
        if visitor.is_authenticated != is_auth:
            visitor.is_authenticated = is_auth
            changed = True

        if ip and visitor.ip_address != ip:
            visitor.ip_address = ip
            changed = True

        if ua and visitor.user_agent != ua:
            visitor.user_agent = ua
            changed = True

        if changed:
            visitor.save()
        else:
            visitor.save(update_fields=["last_seen"])

        return visitor

    @staticmethod
    def _get_ip(request):
        return get_client_ip(request)
