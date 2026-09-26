"""API JSON (tach tu core/api.py monolith). Logic giu nguyen."""

from django.contrib.auth.decorators import login_required
import json

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from core.ratelimit import rate_limit


from .common import (
    api_error,
    api_json,
)


@csrf_exempt
def api_geocode(request: HttpRequest) -> JsonResponse:
    """Geoapify Geocoding proxy: search forward or reverse without exposing the key."""
    import urllib.parse
    import urllib.request
    from django.conf import settings

    key = getattr(settings, "GEOAPIFY_API_KEY", "")
    if not key:
        return api_json({"error": "Chưa cấu hình GEOAPIFY_API_KEY."}, status=503)

    lat = request.GET.get("lat")
    lng = request.GET.get("lng")
    q = request.GET.get("q")

    lang = "vi"

    if q:
        params = {
            "text": q,
            "apiKey": key,
            "lang": lang,
            "filter": "countrycode:vn",
            "limit": 1,
        }
        end = "https://api.geoapify.com/v1/geocode/search?" + urllib.parse.urlencode(
            params
        )
    elif lat and lng:
        params = {"lat": lat, "lon": lng, "apiKey": key, "lang": lang}
        end = "https://api.geoapify.com/v1/geocode/reverse?" + urllib.parse.urlencode(
            params
        )
    else:
        return api_json({"error": "Thiếu q hoặc lat/lng."}, status=400)

    try:
        with urllib.request.urlopen(end, timeout=10) as resp:  # nosec
            data = json.loads(resp.read().decode("utf-8"))
    except Exception:
        return api_json({"error": "Không gọi được Geoapify."}, status=502)

    if data.get("features"):
        r = data["features"][0]
        p = r.get("properties", {})
        loc = r.get("geometry", {}).get("coordinates", [])
        return api_json(
            {
                "lat": loc[1] if len(loc) == 2 else None,
                "lng": loc[0] if len(loc) == 2 else None,
                "address": p.get("formatted") or p.get("address_line2") or "",
            }
        )
    return api_json({"error": "Không tìm thấy địa chỉ."}, status=404)


@csrf_exempt
def api_root(request: HttpRequest) -> JsonResponse:
    endpoints = {
        "products": "/api/products/",
        "product_detail": "/api/products/<id>/",
        "product_reviews": "/api/products/<id>/reviews/",
        "categories": "/api/categories/",
        "orders": "/api/orders/",
        "order_detail": "/api/orders/<id>/",
        "order_lookup": "/api/orders/lookup/",
        "coupon_check": "/api/coupons/check/",
        "geocode": "/api/geocode/?q=... | ?lat=...&lng=...",
        "admin": {
            "stats": "/api/admin/stats/",
            "orders": "/api/admin/orders/",
            "order_detail": "/api/admin/orders/<id>/",
            "order_status": "/api/admin/orders/<id>/status/",
            "order_refund": "/api/admin/orders/<id>/refund/",
            "invoice": "/api/admin/orders/<id>/invoice/",
            "export": "/api/admin/export/",
            "products": "/api/admin/products/",
            "users": "/api/admin/users/",
            "coupons": "/api/admin/coupons/",
            "reviews": "/api/admin/reviews/",
        },
    }
    return api_json(
        {"name": "HUUGIAU Fashion API", "version": "1.0", "endpoints": endpoints}
    )


@login_required
@require_GET
def api_gdpr_export(request: HttpRequest) -> JsonResponse:
    """GDPR Art. 15/20: Xuất toàn bộ dữ liệu cá nhân của user."""
    from orders.models import Order, CouponRedemption, ReturnRequest, GiftCardUsage
    from products.models import (
        Review,
        WishlistItem,
        ProductQuestion,
        BackInStock,
        NewsletterSubscriber,
    )
    from users.models import (
        UserAddress,
        UserProfile,
        VisitorSession,
        UserActivity,
    )
    from users.models_referral import ReferralCode, ReferralReward

    user = request.user

    # Basic user data
    data = {
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "date_joined": user.date_joined.isoformat() if user.date_joined else None,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "is_active": user.is_active,
        },
        "profile": {},
        "addresses": [],
        "orders": [],
        "coupon_redemptions": [],
        "returns": [],
        "gift_card_usages": [],
        "reviews": [],
        "wishlist": [],
        "questions": [],
        "back_in_stock_requests": [],
        "newsletter": [],
        "visitor_sessions": [],
        "activities": [],
        "referral_codes": [],
        "referral_rewards": [],
    }

    # Profile
    try:
        profile = UserProfile.objects.get(user=user)
        data["profile"] = {
            "phone_number": profile.phone_number,
            "birthday": profile.birthday.isoformat() if profile.birthday else None,
            "points": profile.points,
            "points_expire_at": profile.points_expire_at.isoformat()
            if profile.points_expire_at
            else None,
        }
    except Exception:
        pass

    # Addresses
    for addr in UserAddress.objects.filter(user=user).values():
        data["addresses"].append(addr)

    # Orders
    for order in Order.objects.filter(user=user).prefetch_related(
        "items__product", "items__variant"
    ):
        data["orders"].append(
            {
                "id": order.id,
                "status": order.status,
                "total_amount": str(order.total_amount),
                "created_at": order.created_at.isoformat(),
                "items": [
                    {
                        "product_id": item.product_id,
                        "variant_id": item.variant_id,
                        "quantity": item.quantity,
                        "price": str(item.price),
                    }
                    for item in order.items.all()
                ],
            }
        )

    # Coupon redemptions
    for cr in CouponRedemption.objects.filter(user=user).select_related("coupon"):
        data["coupon_redemptions"].append(
            {
                "coupon_code": cr.coupon.code,
                "order_id": cr.order_id,
                "redeemed_at": cr.used_at.isoformat() if cr.used_at else None,
            }
        )

    # Returns
    for ret in ReturnRequest.objects.filter(order__user=user).select_related("order"):
        data["returns"].append(
            {
                "id": ret.id,
                "order_id": ret.order_id,
                "return_type": ret.return_type,
                "reason": ret.reason,
                "status": ret.status,
                "created_at": ret.created_at.isoformat(),
            }
        )

    # Gift card usages
    for gcu in GiftCardUsage.objects.filter(order__user=user).select_related(
        "gift_card"
    ):
        data["gift_card_usages"].append(
            {
                "gift_card_code": gcu.gift_card.code,
                "amount": str(gcu.amount),
                "used_at": gcu.used_at.isoformat() if gcu.used_at else None,
            }
        )

    # Reviews
    for rev in Review.objects.filter(user=user).select_related("product"):
        data["reviews"].append(
            {
                "product_id": rev.product_id,
                "rating": rev.rating,
                "comment": rev.comment,
                "created_at": rev.created.isoformat(),
            }
        )

    # Wishlist
    for wi in WishlistItem.objects.filter(user=user).select_related("product"):
        data["wishlist"].append(
            {
                "product_id": wi.product_id,
                "created_at": wi.created.isoformat(),
            }
        )

    # Questions
    for q in ProductQuestion.objects.filter(user=user).select_related("product"):
        data["questions"].append(
            {
                "product_id": q.product_id,
                "question": q.question,
                "answer": q.answer,
                "created_at": q.created.isoformat(),
            }
        )

    # Back in stock
    for bs in BackInStock.objects.filter(email=user.email).select_related(
        "product"
    ):
        data["back_in_stock_requests"].append(
            {
                "product_id": bs.product_id,
                "created_at": bs.created.isoformat(),
            }
        )

    # Newsletter
    try:
        from products.models import NewsletterSubscriber

        ns = NewsletterSubscriber.objects.filter(email=user.email).first()
        if ns:
            data["newsletter"] = {
                "email": ns.email,
                "is_active": ns.is_active,
                "subscribed_at": ns.subscribed_at.isoformat()
                if ns.subscribed_at
                else None,
            }
    except Exception:
        pass

    # Visitor sessions
    for vs in VisitorSession.objects.filter(user=user).values():
        data["visitor_sessions"].append(vs)

    # Activities
    for act in UserActivity.objects.filter(user=user).values():
        data["activities"].append(act)

    # Referral codes
    for rc in ReferralCode.objects.filter(user=user).values():
        data["referral_codes"].append(rc)

    # Referral rewards
    from django.db.models import Q

    for rr in (
        ReferralReward.objects.filter(Q(referrer=user) | Q(referred_user=user))
        .select_related("referral_code")
        .values()
    ):
        data["referral_rewards"].append(rr)

    # Return as downloadable JSON
    from django.core.serializers.json import DjangoJSONEncoder
    from django.http import HttpResponse
    import json

    filename = f"gdpr-export-user-{user.id}-{timezone.now().strftime('%Y%m%d')}.json"
    resp = HttpResponse(
        json.dumps(data, ensure_ascii=False, indent=2, cls=DjangoJSONEncoder),
        content_type="application/json; charset=utf-8",
    )
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    return resp


@login_required
@require_POST
def api_gdpr_delete(request: HttpRequest) -> JsonResponse:
    """Deactivate an account; this endpoint does not erase retained order records."""
    user = request.user

    # Confirm password
    import json

    try:
        payload = json.loads(request.body)
        password = payload.get("password", "")
    except Exception:
        password = request.POST.get("password", "")

    if not user.check_password(password):
        return api_error("Mật khẩu không đúng.", status=400)

    user_id = user.id
    # Preserve order history; order records may still contain personal data.
    user.username = f"deleted_{user_id}"
    user.email = f"deleted_{user_id}@example.com"
    user.first_name = ""
    user.last_name = ""
    user.is_active = False
    user.set_unusable_password()
    user.save()

    return api_json(
        {
            "success": True,
            "message": "Tài khoản đã được vô hiệu hóa. Thông tin trong hồ sơ và đơn hàng liên quan có thể vẫn được lưu.",
        }
    )


@rate_limit(
    "gdpr_guest_export",
    max_requests=5,
    window=60,
    error_msg="Quá nhiều yêu cầu xuất dữ liệu. Vui lòng thử lại sau.",
    methods=("GET",),
)
@require_GET
def api_gdpr_guest_export(request: HttpRequest) -> JsonResponse:
    """GDPR export cho guest order (tra cứu bằng order_id + phone/email)."""
    order_id = request.GET.get("order_id", "").strip()
    phone = request.GET.get("phone", "").strip()
    email = request.GET.get("email", "").strip()

    if not order_id.isdecimal() or not (phone or email):
        return api_error("Không tìm thấy đơn hàng.", status=404)

    from orders.models import Order

    order = Order.objects.filter(id=order_id).first()
    if order is None:
        return api_error("Không tìm thấy đơn hàng.", status=404)

    if (phone and order.phone != phone) or (
        email and order.customer_email.casefold() != email.casefold()
    ):
        return api_error("Không tìm thấy đơn hàng.", status=404)

    data = {
        "order": {
            "id": order.id,
            "customer_name": order.customer_name,
            "customer_email": order.customer_email,
            "phone": order.phone,
            "shipping_address": order.shipping_address,
            "status": order.status,
            "total_amount": str(order.total_amount),
            "created_at": order.created_at.isoformat(),
        }
    }

    from django.http import HttpResponse
    import json

    filename = f"gdpr-guest-order-{order.id}.json"
    resp = HttpResponse(
        json.dumps(data, ensure_ascii=False, indent=2),
        content_type="application/json; charset=utf-8",
    )
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    return resp


@require_GET
def api_schema_file(request: HttpRequest) -> HttpResponse:
    """Serve the generated OpenAPI schema file (YAML)."""
    import os
    from django.conf import settings
    from django.http import HttpResponse, Http404

    candidates = (
        os.path.join(settings.BASE_DIR, "backend", "openapi.yaml"),
        os.path.join(settings.BASE_DIR, "openapi.yaml"),
    )
    schema_path = next((p for p in candidates if os.path.exists(p)), None)
    if schema_path is None:
        raise Http404(
            "OpenAPI schema file not found. Run `python manage.py generate_schema` first."
        )

    with open(schema_path, "rb") as f:
        content = f.read()

    response = HttpResponse(
        content, content_type="application/vnd.oai.openapi; charset=utf-8"
    )
    response["Content-Disposition"] = 'attachment; filename="openapi.yaml"'
    return response
