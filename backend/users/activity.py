from .models import UserActivity


def _safe_activity_path(request):
    match = getattr(request, "resolver_match", None)
    if getattr(match, "url_name", None) == "password_reset_confirm":
        return "/quen-mat-khau/dat-lai/[redacted]/"
    return getattr(request, "path", "")[:255]


def log_activity(request, event_type="action", metadata=None, status_code=200):
    if metadata is None:
        metadata = {}

    visitor = getattr(request, "visitor_session", None)
    user = (
        request.user
        if getattr(request, "user", None) and request.user.is_authenticated
        else None
    )

    UserActivity.objects.create(
        visitor=visitor,
        user=user,
        event_type=event_type,
        path=_safe_activity_path(request),
        method=getattr(request, "method", ""),
        status_code=status_code,
        metadata=metadata,
    )
