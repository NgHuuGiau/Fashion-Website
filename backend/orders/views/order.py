from datetime import timedelta
import random

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from core.ratelimit import rate_limit

from ..admin_forms import OrderEditForm, OrderLookupForm
from ..constants import BANKS, SHOP_ACCOUNT_NAME, SHOP_BANK_ACCOUNT
from ..forms import ReturnRequestForm
from ..models import Order, ReturnRequest

from users.models import UserProfile
from .cart import (
    build_vietqr_url,
    expire_bank_order_if_needed,
    normalize_shipping_address,
    restore_order_stock,
)

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
    elif (
        order.status == "processing"
        and order.is_paid
        and now > order.created_at + timedelta(hours=24)
    ):
        order.status = "shipping"
        order.save(update_fields=["status", "updated_at"])
    if order.status == "shipping":
        eta = build_delivery_eta(order)
        if now > eta["eta_date"]:
            order.status = "delivered"
            if not order.is_paid:
                order.is_paid = True
            order.save(update_fields=["status", "is_paid", "updated_at"])
            from ..services.order_email import send_order_email

            send_order_email(order, event="delivered")
            _grant_order_points(order)
    return order


def _grant_order_points(order):
    """Tích 1% giá trị đơn thành điểm (10đ = 1 điểm) khi giao thành công."""
    if order.points_earned or not order.user_id:
        return
    earned = int(order.total_amount // 10)
    if not earned:
        return
    profile, _ = UserProfile.objects.get_or_create(user=order.user)
    profile.points += earned
    profile.save(update_fields=["points"])
    Order.objects.filter(id=order.id).update(points_earned=earned)


def pick_carrier(shipping_address):
    """Chọn đơn vị vận chuyển theo khu vực giao hàng."""
    normalized = normalize_shipping_address(shipping_address)
    if any(keyword in normalized for keyword in HCMC_KEYWORDS + NEAR_HCMC_KEYWORDS):
        return "ghn"
    if any(keyword in normalized for keyword in NORTHERN_KEYWORDS):
        return "ghtk"
    return "vnpost"


def generate_tracking_code(carrier, order_id):
    prefix = {"ghn": "GHD", "ghtk": "GHTK", "vnpost": "VNPN"}[carrier]
    return f"{prefix}{order_id:05d}{random.randint(100, 999)}"


def mark_order_shipped(order):
    """Gán đơn vị vận chuyển + mã vận đơn khi đơn sang 'Đang giao'. Idempotent."""
    if order.status != "shipping" or order.carrier:
        return order
    order.carrier = pick_carrier(order.shipping_address)
    order.tracking_code = generate_tracking_code(order.carrier, order.id)
    order.save(update_fields=["carrier", "tracking_code", "updated_at"])
    from ..services.order_email import send_order_email

    send_order_email(order, event="shipping")
    return order


def decorate_order_tracking(order):
    auto_advance_order_status(order)
    mark_order_shipped(order)
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
        messages.warning(
            request, "Đơn hàng quá 15 phút chưa thanh toán, hệ thống đã tự hủy."
        )
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
            if request.POST.get("action") == "pay_now" and not order.is_paid:
                if order.payment_method == "bank":
                    return redirect("orders:bank_payment_waiting", order_id=order.id)
                if order.payment_method == "vnpay":
                    return redirect("orders:vnpay_payment", order_id=order.id)
        else:
            for field, field_errors in form.errors.items():
                for err in field_errors:
                    messages.error(request, err)
        return redirect("orders:order_review", order_id=order.id)

    if order.payment_method == "bank" and not order.bank_code:
        order.bank_code = "VCB"

    qr_url = ""
    selected_bank_name = ""
    if (
        order.payment_method == "bank"
        and not order.is_paid
        and order.status != "cancelled"
    ):
        bank_meta = BANKS.get(order.bank_code) or BANKS["VCB"]
        selected_bank_name = bank_meta["name"]
        qr_url = build_vietqr_url(
            order.bank_code or "VCB", order.total_amount, f"DH{order.id}"
        )

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
    qs = (
        Order.objects.all()
        if request.user.is_staff
        else Order.objects.filter(user=request.user)
    )
    orders = qs.prefetch_related("items__product", "items__variant").order_by(
        "-created_at"
    )
    paginator = Paginator(orders, 15)
    page_obj = paginator.get_page(request.GET.get("page"))
    for order in page_obj.object_list:
        expire_bank_order_if_needed(order)
        decorate_order_tracking(order)
    return render(
        request,
        "account/my_orders.html",
        {
            "orders": page_obj,
        },
    )


@login_required
def create_return_request(request: HttpRequest, order_id) -> HttpResponse:
    lookup = {"id": order_id}
    if not request.user.is_staff:
        lookup["user"] = request.user
    order = get_object_or_404(
        Order.objects.prefetch_related("items__product", "items__variant"),
        **lookup,
    )

    if not order.can_request_return:
        messages.error(request, "Đơn hàng này không đủ điều kiện tạo yêu cầu đổi trả.")
        return redirect("orders:order_review", order_id=order.id)

    if request.method == "POST":
        form = ReturnRequestForm(request.POST, order=order)
        if form.is_valid():
            item_ids = form.cleaned_data["item_ids"]
            chosen_items = (
                order.items.filter(id__in=item_ids) if item_ids else order.items.all()
            )
            refund_amount = sum(item.price * item.quantity for item in chosen_items)
            ReturnRequest.objects.create(
                order=order,
                return_type=form.cleaned_data["return_type"],
                reason=form.cleaned_data["reason"],
                note=form.cleaned_data["note"],
                refund_amount=refund_amount,
                items=[
                    {
                        "product": item.product.name,
                        "variant": item.selected_size,
                        "qty": item.quantity,
                        "price": str(item.price),
                    }
                    for item in chosen_items
                ],
            )
            messages.success(
                request,
                "Đã gửi yêu cầu đổi trả. Shop sẽ liên hệ xác nhận trong 1–2 ngày làm việc.",
            )
            return redirect("orders:order_review", order_id=order.id)
        for field, field_errors in form.errors.items():
            for err in field_errors:
                messages.error(request, err)

    return render(
        request,
        "account/return_request.html",
        {
            "order": order,
            "form": ReturnRequestForm(order=order),
            "return_reasons": dict(ReturnRequest.REASON_CHOICES),
        },
    )


@rate_limit(
    "order_lookup",
    max_requests=15,
    window=60,
    error_msg="Quá nhiều yêu cầu tra cứu. Vui lòng thử lại sau.",
)
def order_lookup(request: HttpRequest) -> HttpResponse:
    form = OrderLookupForm()
    if request.method == "POST":
        form = OrderLookupForm(request.POST)
        if form.is_valid():
            try:
                order = Order.objects.get(
                    id=form.cleaned_data["order_id"], phone=form.cleaned_data["phone"]
                )
                expire_bank_order_if_needed(order)
                decorate_order_tracking(order)
                return render(
                    request,
                    "shop/order_lookup.html",
                    {"looked_up_order": order, "form": form},
                )
            except Order.DoesNotExist:
                return render(
                    request,
                    "shop/order_lookup.html",
                    {
                        "lookup_error": "Không tìm thấy đơn hàng. Kiểm tra lại mã đơn và số điện thoại.",
                        "form": form,
                    },
                )
        return render(
            request,
            "shop/order_lookup.html",
            {
                "lookup_error": "Vui lòng nhập đúng mã đơn và số điện thoại.",
                "form": form,
            },
        )
    return render(request, "shop/order_lookup.html", {"form": form})


@login_required
@require_POST
@transaction.atomic
def user_cancel_order(request: HttpRequest, order_id) -> HttpResponse:
    order = get_object_or_404(
        Order.objects.select_for_update(), id=order_id, user=request.user
    )
    expire_bank_order_if_needed(order)
    if order.status in ("pending", "processing") and not order.is_paid:
        restore_order_stock(order)
        order.status = "cancelled"
        order.is_paid = False
        order.save(update_fields=["status", "is_paid"])
        from ..services.order_email import send_order_email

        send_order_email(order, event="cancelled")
        messages.success(request, f"Đã huỷ đơn hàng #{order.id}.")
    else:
        messages.error(request, "Không thể huỷ đơn hàng ở trạng thái hiện tại.")
    return redirect("orders:my_orders")


@login_required
@require_POST
def reorder_order(request: HttpRequest, order_id) -> HttpResponse:
    order = get_object_or_404(
        Order.objects.prefetch_related("items__product", "items__variant"),
        id=order_id,
        user=request.user,
    )

    from ..cart import add_cart

    added = 0
    skipped = 0
    for item in order.items.all():
        product = item.product
        variant = item.variant
        if not product.available or (variant and not variant.is_active):
            skipped += 1
            continue
        success, _ = add_cart(
            request,
            product.id,
            quantity=item.quantity,
            variant_id=variant.id if variant else None,
        )
        if success:
            added += 1
        else:
            skipped += 1

    if added:
        messages.success(
            request, f"Đã thêm {added} món từ đơn #{order.id} vào giỏ hàng."
        )
    if skipped:
        messages.warning(
            request,
            f"{skipped} món không còn hàng hoặc đã ngừng bán nên không thêm vào giỏ.",
        )
    if not added and not skipped:
        messages.info(request, "Không có sản phẩm nào để mua lại.")
    return redirect("orders:cart_detail")
