"""API JSON (tach tu core/api.py monolith). Logic giu nguyen."""

from django.contrib.auth.decorators import login_required

from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST

from users.permissions import is_staff_member

from orders.constants import (
    shop_bank_code,
    shop_bank_meta,
)
from orders.models import Coupon, Order
from orders.views.cart import build_vietqr_url
from orders.views.order import build_delivery_eta, expire_bank_order_if_needed


from .common import (
    _serialize_order,
    api_error,
    api_json,
    int_param,
)


@login_required
@require_GET
def api_my_orders(request: HttpRequest) -> JsonResponse:
    qs = (
        Order.objects.all()
        if is_staff_member(request.user)
        else Order.objects.filter(user=request.user)
    )
    # P1.2: phan trang thay vi cat cung 200 (mac dinh 50, toi da 200)
    limit = int_param(request, "limit", 50) or 50
    limit = max(1, min(limit, 200))
    offset = int_param(request, "offset", 0) or 0
    offset = max(0, offset)
    total = qs.count()
    orders = list(
        qs.prefetch_related("items__product").order_by("-created_at")[
            offset : offset + limit
        ]
    )
    for order in orders:
        expire_bank_order_if_needed(order)
    return api_json(
        {
            "count": total,
            "limit": limit,
            "offset": offset,
            "results": [_serialize_order(o) for o in orders],
        }
    )


@login_required
@require_GET
def api_order_detail(request: HttpRequest, pk: int) -> JsonResponse:
    lookup = {"id": pk}
    if not is_staff_member(request.user):
        lookup["user"] = request.user
    order = get_object_or_404(
        Order.objects.prefetch_related("items__product"), **lookup
    )
    expire_bank_order_if_needed(order)
    data = _serialize_order(order, include_items=True)
    if order.payment_method == "bank":
        bank = shop_bank_meta()
        data["bank"] = {
            "code": shop_bank_code(),
            "name": bank.get("name", ""),
        }
        if not order.is_paid and order.status != "cancelled":
            data["qr_url"] = build_vietqr_url(order.total_amount, f"DH{order.id}")
    eta = build_delivery_eta(order)
    data["eta_label"] = eta["eta_label"]
    data["eta_date"] = eta["eta_date"].isoformat()
    return api_json(data)


@require_POST
def api_order_lookup(request: HttpRequest) -> JsonResponse:
    order_id = request.POST.get("order_id", "").strip()
    phone = request.POST.get("phone", "").strip()
    if not order_id.isdigit() or not phone:
        return api_error("Cần cung cấp order_id và phone.")
    try:
        order = Order.objects.get(id=order_id, phone=phone)
    except Order.DoesNotExist:
        return api_error(
            "Không tìm thấy đơn hàng với mã và số điện thoại này.", status=404
        )
    expire_bank_order_if_needed(order)
    return api_json(_serialize_order(order, include_items=True))


@login_required
@require_POST
def api_coupon_check(request: HttpRequest) -> JsonResponse:
    code = request.POST.get("code", "").strip()
    if not code:
        return api_error("Thiếu mã giảm giá.")
    coupon = Coupon.objects.filter(code__iexact=code).first()
    if not coupon:
        return api_error("Mã giảm giá không tồn tại.", status=404)
    if not coupon.is_usable_now():
        return api_error("Mã giảm giá đã hết hạn hoặc ngừng hoạt động.")
    if not coupon.is_usable_by_user(request.user):
        return api_error("Bạn đã dùng hết lượt cho mã giảm giá này.")
    return api_json(
        {
            "code": coupon.code,
            "discount_type": coupon.discount_type,
            "value": int(coupon.value),
            "min_order_amount": int(coupon.min_order_amount),
            "max_discount_amount": int(coupon.max_discount_amount)
            if coupon.max_discount_amount is not None
            else None,
            "label": coupon.get_discount_type_display(),
        }
    )
