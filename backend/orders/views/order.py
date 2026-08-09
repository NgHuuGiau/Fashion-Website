from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from core.ratelimit import rate_limit

from ..admin_forms import OrderEditForm, OrderLookupForm
from ..constants import BANKS, SHOP_ACCOUNT_NAME, SHOP_BANK_ACCOUNT
from ..models import Order
from .cart import build_vietqr_url, expire_bank_order_if_needed, normalize_shipping_address, restore_order_stock

HCMC_KEYWORDS = (
    "ho chi minh",
    "hcm",
    "tp hcm",
    "tphcm",
    "sai gon",
    "quan 1",
    "quan 2",
    "quan 3",
    "quan 4",
    "quan 5",
    "quan 6",
    "quan 7",
    "quan 8",
    "quan 9",
    "quan 10",
    "quan 11",
    "quan 12",
    "thu duc",
    "go vap",
    "binh thanh",
    "tan binh",
    "tan phu",
    "phu nhuan",
    "binh tan",
)
NEAR_HCMC_KEYWORDS = (
    "binh duong",
    "dong nai",
    "tay ninh",
    "ba ria",
    "vung tau",
    "long an",
    "tien giang",
    "ben tre",
)
NORTHERN_KEYWORDS = (
    "ha noi",
    "hanoi",
    "hai phong",
    "quang ninh",
    "bac ninh",
    "bac giang",
    "hung yen",
    "hai duong",
    "nam dinh",
    "thai binh",
    "ninh binh",
    "ha nam",
    "vinh phuc",
    "phu tho",
    "tuyen quang",
    "yen bai",
    "lao cai",
    "ha giang",
    "cao bang",
    "lang son",
    "thai nguyen",
    "bac kan",
    "son la",
    "dien bien",
    "lai chau",
    "hoa binh",
    "nghe an",
    "thanh hoa",
)


def estimate_delivery_days(shipping_address):
    normalized = normalize_shipping_address(shipping_address)
    if any(keyword in normalized for keyword in HCMC_KEYWORDS):
        return 2
    if any(keyword in normalized for keyword in NEAR_HCMC_KEYWORDS):
        return 3
    if any(keyword in normalized for keyword in NORTHERN_KEYWORDS):
        return 7
    return 5


def build_delivery_eta(order):
    eta_days = estimate_delivery_days(order.shipping_address)
    base_time = order.created_at
    eta_date = base_time + timedelta(days=eta_days)
    return {
        "eta_days": eta_days,
        "eta_date": eta_date,
        "eta_label": f"Dự kiến giao trong khoảng {eta_days} ngày",
    }


def auto_advance_order_status(order):
    now = timezone.now()
    if order.status in ("cancelled", "delivered"):
        return order
    if order.status == "pending" and now > order.created_at + timedelta(hours=24):
        order.status = "shipping"
        order.save(update_fields=["status", "updated_at"])
    elif order.status == "processing" and order.is_paid and now > order.created_at + timedelta(hours=24):
        order.status = "shipping"
        order.save(update_fields=["status", "updated_at"])
    if order.status == "shipping":
        eta = build_delivery_eta(order)
        if now > eta["eta_date"]:
            order.status = "delivered"
            if not order.is_paid:
                order.is_paid = True
            order.save(update_fields=["status", "is_paid", "updated_at"])
    return order


def decorate_order_tracking(order):
    auto_advance_order_status(order)
    eta = build_delivery_eta(order)
    order.eta_days = eta["eta_days"]
    order.eta_date = eta["eta_date"]
    order.eta_label = eta["eta_label"]
    return order


@login_required
def order_review(request: HttpRequest, order_id) -> HttpResponse:
    lookup = {"id": order_id}
    if not request.user.is_staff:
        lookup["user"] = request.user
    order = get_object_or_404(
        Order.objects.prefetch_related("items__product", "items__variant"),
        **lookup,
    )
    decorate_order_tracking(order)
    if expire_bank_order_if_needed(order):
        messages.warning(request, "Đơn hàng quá 15 phút chưa thanh toán, hệ thống đã tự hủy.")
        return redirect("orders:order_failed", order_id=order.id)

    editable_statuses = {"pending", "processing"}
    can_edit = (not order.is_paid) and (order.status in editable_statuses)

    if request.method == "POST":
        if not can_edit:
            messages.error(request, "Đơn hàng này không thể chỉnh sửa.")
            return redirect("orders:order_review", order_id=order.id)

        form = OrderEditForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, "Đã cập nhật thông tin đơn hàng.")
            if request.POST.get("action") == "pay_now" and order.payment_method == "bank" and not order.is_paid:
                return redirect("orders:bank_payment_waiting", order_id=order.id)
        else:
            for field, field_errors in form.errors.items():
                for err in field_errors:
                    messages.error(request, err)
        return redirect("orders:order_review", order_id=order.id)

    if order.payment_method == "bank" and not order.bank_code:
        order.bank_code = "VCB"

    qr_url = ""
    selected_bank_name = ""
    if order.payment_method == "bank" and not order.is_paid and order.status != "cancelled":
        bank_meta = BANKS.get(order.bank_code) or BANKS["VCB"]
        selected_bank_name = bank_meta["name"]
        qr_url = build_vietqr_url(order.bank_code or "VCB", order.total_amount, f"DH{order.id}")

    return render(
        request,
        "account/order_review.html",
        {
            "order": order,
            "can_edit": can_edit,
            "tracking_order": order,
            "bank_choices": BANKS.items(),
            "selected_bank_name": selected_bank_name,
            "qr_url": qr_url,
            "shop_bank_account": SHOP_BANK_ACCOUNT,
            "shop_account_name": SHOP_ACCOUNT_NAME,
        },
    )


@login_required
def my_orders(request: HttpRequest) -> HttpResponse:
    qs = Order.objects.all() if request.user.is_staff else Order.objects.filter(user=request.user)
    orders = list(
        qs.prefetch_related("items__product", "items__variant").order_by("-created_at")
    )
    for order in orders:
        expire_bank_order_if_needed(order)
        decorate_order_tracking(order)
    active_tracking_order = next((order for order in orders if order.status == "shipping"), None)
    if active_tracking_order is None:
        active_tracking_order = next((order for order in orders if order.status == "processing"), None)
    return render(
        request,
        "account/my_orders.html",
        {
            "orders": orders,
            "active_tracking_order": active_tracking_order,
        },
    )


@rate_limit("order_lookup", max_requests=15, window=60, error_msg="Quá nhiều yêu cầu tra cứu. Vui lòng thử lại sau.")
def order_lookup(request: HttpRequest) -> HttpResponse:
    form = OrderLookupForm()
    if request.method == "POST":
        form = OrderLookupForm(request.POST)
        if form.is_valid():
            try:
                order = Order.objects.get(id=form.cleaned_data["order_id"], phone=form.cleaned_data["phone"])
                expire_bank_order_if_needed(order)
                decorate_order_tracking(order)
                return render(request, "shop/order_lookup.html", {"looked_up_order": order, "form": form})
            except Order.DoesNotExist:
                return render(request, "shop/order_lookup.html", {"lookup_error": "Không tìm thấy đơn hàng. Kiểm tra lại mã đơn và số điện thoại.", "form": form})
        return render(request, "shop/order_lookup.html", {"lookup_error": "Vui lòng nhập đúng mã đơn và số điện thoại.", "form": form})
    return render(request, "shop/order_lookup.html", {"form": form})


@login_required
@require_POST
@transaction.atomic
def user_cancel_order(request: HttpRequest, order_id) -> HttpResponse:
    order = get_object_or_404(Order.objects.select_for_update(), id=order_id, user=request.user)
    expire_bank_order_if_needed(order)
    if order.status in ("pending", "processing") and not order.is_paid:
        order.status = "cancelled"
        order.is_paid = False
        order.save(update_fields=["status", "is_paid"])
        restore_order_stock(order)
        messages.success(request, f"Đã huỷ đơn hàng #{order.id}.")
    else:
        messages.error(request, "Không thể huỷ đơn hàng ở trạng thái hiện tại.")
    return redirect("orders:my_orders")
