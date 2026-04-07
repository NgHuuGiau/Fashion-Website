from .activity import log_activity
from .models import VisitorSession



# -----------------------------------------------
# | KHỐI LỚP (CLASS): VISITORTRACKINGMIDDLEWARE |
# -----------------------------------------------
class VisitorTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.session.session_key:
            request.session.save()

        request.visitor_session = self._bind_visitor(request)
        response = self.get_response(request)

        if not request.path.startswith("/static/") and not request.path.startswith("/media/"):
            event_type = "page_view" if request.method == "GET" else "action"
            log_activity(
                request,
                event_type=event_type,
                metadata={"query": request.GET.dict() if request.method == "GET" else {}},
                status_code=getattr(response, "status_code", 200),
            )

        return response


    # ---------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): _BIND_VISITOR |
    # ---------------------------------------
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

    # ---------------------------------
    # | HÀM XỬ LÝ (FUNCTION): _GET_IP |
    # ---------------------------------
    def _get_ip(request):
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
