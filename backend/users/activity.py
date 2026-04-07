from .models import UserActivity



# --------------------------------------
# | HÀM XỬ LÝ (FUNCTION): LOG_ACTIVITY |
# --------------------------------------
def log_activity(request, event_type="action", metadata=None, status_code=200):
    if metadata is None:
        metadata = {}

    visitor = getattr(request, "visitor_session", None)
    user = request.user if getattr(request, "user", None) and request.user.is_authenticated else None

    UserActivity.objects.create(
        visitor=visitor,
        user=user,
        event_type=event_type,
        path=getattr(request, "path", "")[:255],
        method=getattr(request, "method", ""),
        status_code=status_code,
        metadata=metadata,
    )
