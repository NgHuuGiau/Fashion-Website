"""Web Push subscription - VAPID, Firefox/Chrome/Safari 16+.
ponytail: 1 file, re-use sw.js push handler, khong them app.
"""
import json
import logging

import pywebpush as webpush
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from users.models import UserProfile

logger = logging.getLogger(__name__)


def _vapid_keys():
    return {
        "public_key": getattr(settings, "VAPID_PUBLIC_KEY", ""),
        "private_key": getattr(settings, "VAPID_PRIVATE_KEY", ""),
        "subject": getattr(settings, "VAPID_SUBJECT", "mailto:admin@huugiau.local"),
    }


@require_GET
def push_vapid_key(request):
    """FE goi lay public key de subscribe."""
    pk = _vapid_keys()["public_key"]
    if not pk:
        return JsonResponse({"error": "VAPID not configured"}, status=503)
    return JsonResponse({"publicKey": pk})


@csrf_exempt
@require_POST
def push_subscribe(request):
    """Luu subscription cua user/guest."""
    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    endpoint = data.get("endpoint")
    keys = data.get("keys", {})
    p256dh = keys.get("p256dh")
    auth = keys.get("auth")
    if not (endpoint and p256dh and auth):
        return JsonResponse({"error": "Missing subscription fields"}, status=400)

    # Gắn vào UserProfile nếu đã đăng nhập, hoặc session guest
    if request.user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.push_subscriptions = profile.push_subscriptions or []
        # Tránh trùng endpoint
        profile.push_subscriptions = [s for s in profile.push_subscriptions if s.get("endpoint") != endpoint]
        profile.push_subscriptions.append({"endpoint": endpoint, "keys": keys})
        profile.save(update_fields=["push_subscriptions"])
    else:
        subs = request.session.get("push_subscriptions", [])
        subs = [s for s in subs if s.get("endpoint") != endpoint]
        subs.append({"endpoint": endpoint, "keys": keys})
        request.session["push_subscriptions"] = subs
        request.session.modified = True

    return JsonResponse({"ok": True})


@csrf_exempt
@require_POST
def push_unsubscribe(request):
    """Xoa subscription."""
    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    endpoint = data.get("endpoint")
    if not endpoint:
        return JsonResponse({"error": "Missing endpoint"}, status=400)

    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            profile.push_subscriptions = [s for s in (profile.push_subscriptions or []) if s.get("endpoint") != endpoint]
            profile.save(update_fields=["push_subscriptions"])
        except UserProfile.DoesNotExist:
            pass
    else:
        subs = request.session.get("push_subscriptions", [])
        subs = [s for s in subs if s.get("endpoint") != endpoint]
        request.session["push_subscriptions"] = subs
        request.session.modified = True

    return JsonResponse({"ok": True})


def send_push_to_user(user, payload: dict, ttl: int = 86400) -> int:
    """Gui push den tat ca subscriptions cua user. Tra ve so luong gui thanh cong."""
    try:
        profile = user.profile
        subs = profile.push_subscriptions or []
    except UserProfile.DoesNotExist:
        return 0

    if not subs:
        return 0

    vapid = _vapid_keys()
    if not vapid["public_key"]:
        logger.warning("VAPID not configured, skip push")
        return 0

    sent = 0
    for sub in subs:
        try:
            webpush.webpush(
                subscription_info={"endpoint": sub["endpoint"], "keys": sub["keys"]},
                data=json.dumps(payload),
                vapid_private_key=vapid["private_key"],
                vapid_claims={"sub": vapid["subject"]},
                ttl=ttl,
            )
            sent += 1
        except webpush.WebPushException as e:
            # 410/404 = subscription expired -> xoa
            if e.response and e.response.status_code in (404, 410):
                profile.push_subscriptions = [s for s in profile.push_subscriptions if s.get("endpoint") != sub["endpoint"]]
                profile.save(update_fields=["push_subscriptions"])
            logger.warning(f"Push failed: {e}")
    return sent


def send_push_to_all(payload: dict, ttl: int = 86400) -> int:
    """Broadcast den tat ca subscriptions (user + guest session). Dung de thong bao flash sale."""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    vapid = _vapid_keys()
    if not vapid["public_key"]:
        return 0

    sent = 0
    # Authenticated users
    for profile in UserProfile.objects.exclude(push_subscriptions__exact=[]).iterator():
        for sub in profile.push_subscriptions or []:
            try:
                webpush.webpush(
                    subscription_info={"endpoint": sub["endpoint"], "keys": sub["keys"]},
                    data=json.dumps(payload),
                    vapid_private_key=vapid["private_key"],
                    vapid_claims={"sub": vapid["subject"]},
                    ttl=ttl,
                )
                sent += 1
            except webpush.WebPushException as e:
                if e.response and e.response.status_code in (404, 410):
                    profile.push_subscriptions = [s for s in profile.push_subscriptions if s.get("endpoint") != sub["endpoint"]]
                    profile.save(update_fields=["push_subscriptions"])

    # Guest sessions - can't easily enumerate all sessions without redis scan
    # Delegate to Celery task with session store if needed
    return sent