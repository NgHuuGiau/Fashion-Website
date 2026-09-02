import logging
from datetime import timedelta

from django.contrib import messages
from django.db import transaction
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from users.activity import log_activity

from .cart import (
    build_vietqr_url,
    expire_bank_order_if_needed,
    _payment_token,
    reserve_order_stock,
    restore_order_stock,
)
from .order import decorate_order_tracking
from ..constants import (
    BANKS,
    PAYMENT_TIMEOUT_MINUTES,
    SHOP_ACCOUNT_NAME,
    SHOP_BANK_ACCOUNT,
)
from ..models import Order

logger = logging.getLogger(__name__)


def get_visitable_order(request: HttpRequest, order_id, queryset=None):
    """Trả đơn mà khách (kể cả khách vãng lai vừa đặt) được xem; else Http404."""
    qs = queryset or Order.objects.all()
    order = get_object_or_404(qs, id=order_id)
    if request.user.is_staff:
        return order
    if request.user.is_authenticated:
        if order.user_id != request.user.id:
            raise Http404
        return order
    if order.user_id is None and order_id in request.session.get("guest_orders", []):
        return order
    raise Http404


def order_success(request: HttpRequest, order_id) -> HttpResponse:
    order = get_visitable_order(request, order_id)
    decorate_order_tracking(order)
    if expire_bank_order_if_needed(order):
        messages.warning(
            request, "Đơn hàng quá 15 phút chưa thanh toán, hệ thống đã tự hủy."
        )
        return redirect("orders:order_failed", order_id=order.id)
    if (
        order.payment_method == "bank"
        and not order.is_paid
        and order.status != "cancelled"
    ):
        return redirect("orders:bank_payment_waiting", order_id=order.id)
    if (
        order.payment_method == "vnpay"
        and not order.is_paid
        and order.status == "processing"
    ):
        from ..vnpay import is_configured

        if is_configured():
            return redirect("orders:vnpay_payment", order_id=order.id)
        messages.error(
            request,
            "Cổng thanh toán VNPay chưa được cấu hình. Vui lòng thử chuyển khoản ngân hàng.",
        )
    if order.status == "cancelled":
        return redirect("orders:order_failed", order_id=order.id)

    qr_url = ""
    selected_bank_name = ""
    if order.payment_method == "bank" and order.bank_code in BANKS:
        selected_bank_name = BANKS[order.bank_code]["name"]
        qr_url = build_vietqr_url(order.bank_code, order.total_amount, f"DH{order.id}")

    return render(
        request,
        "shop/order_success.html",
        {
            "order": order,
            "tracking_order": order,
            "shop_bank_account": SHOP_BANK_ACCOUNT,
            "shop_account_name": SHOP_ACCOUNT_NAME,
            "selected_bank_name": selected_bank_name,
            "qr_url": qr_url,
        },
    )


def bank_payment_waiting(request: HttpRequest, order_id) -> HttpResponse:
    order = get_visitable_order(request, order_id)
    if order.payment_method != "bank":
        return redirect("orders:order_success", order_id=order.id)
    if expire_bank_order_if_needed(order):
        messages.warning(
            request, "Đơn hàng quá 15 phút chưa thanh toán, hệ thống đã tự hủy."
        )
        return redirect("orders:order_failed", order_id=order.id)
    if order.is_paid:
        return redirect("orders:order_success", order_id=order.id)
    if order.status == "cancelled":
        return redirect("orders:order_failed", order_id=order.id)

    selected_bank = BANKS.get(order.bank_code) or BANKS["VCB"]
    expires_at = order.created_at + timedelta(minutes=PAYMENT_TIMEOUT_MINUTES)
    qr_url = build_vietqr_url(order.bank_code, order.total_amount, f"DH{order.id}")
    token = _payment_token(order.id)
    mobile_url = request.build_absolute_uri(
        reverse(
            "orders:bank_payment_mobile", kwargs={"token": token, "order_id": order.id}
        )
    )
    confirm_url = reverse("orders:bank_payment_confirm", kwargs={"order_id": order.id})
    return render(
        request,
        "shop/bank_payment_waiting.html",
        {
            "order": order,
            "selected_bank_name": selected_bank["name"],
            "shop_bank_account": SHOP_BANK_ACCOUNT,
            "shop_account_name": SHOP_ACCOUNT_NAME,
            "qr_url": qr_url,
            "mobile_url": mobile_url,
            "confirm_url": confirm_url,
            "token": token,
            "expires_at_iso": expires_at.isoformat(),
            "payment_timeout_minutes": PAYMENT_TIMEOUT_MINUTES,
        },
    )


def bank_payment_status(request: HttpRequest, order_id) -> JsonResponse:
    order = get_visitable_order(request, order_id)
    expired = expire_bank_order_if_needed(order)
    state = "waiting"
    if order.status == "cancelled" or expired:
        state = "failed"
    elif order.is_paid:
        state = "success"

    return JsonResponse(
        {"state": state, "is_paid": order.is_paid, "status": order.status}
    )


@require_POST
@transaction.atomic
def bank_payment_confirm(request: HttpRequest, order_id) -> HttpResponse:
    order = get_visitable_order(request, order_id, Order.objects.select_for_update())
    if order.payment_method != "bank":
        messages.error(request, "Đơn hàng này không dùng chuyển khoản ngân hàng.")
        return redirect("orders:order_success", order_id=order.id)
    if expire_bank_order_if_needed(order):
        messages.error(
            request, "Đơn hàng đã quá hạn 15 phút nên không thể xác nhận thanh toán."
        )
        return redirect("orders:order_failed", order_id=order.id)
    if order.status == "cancelled":
        messages.error(request, "Đơn hàng đã hủy, không thể xác nhận thanh toán.")
        return redirect("orders:order_success", order_id=order.id)
    if order.is_paid:
        messages.info(request, "Đơn hàng đã được xác nhận thanh toán trước đó.")
        return redirect("orders:order_success", order_id=order.id)

    token = request.POST.get("token", "")
    expected = _payment_token(order.id)
    if not token or token != expected:
        logger.warning(
            "Payment confirm token mismatch. order=%s user=%s ip=%s",
            order.id,
            request.user.id,
            request.META.get("REMOTE_ADDR"),
        )
        messages.error(request, "Mã xác nhận không hợp lệ. Vui lòng quét lại mã QR.")
        return redirect("orders:bank_payment_waiting", order_id=order.id)

    order.is_paid = True
    order.status = "processing"
    order.save(update_fields=["is_paid", "status", "updated_at"])
    from ..services.order_email import send_order_email

    send_order_email(order, event="paid")
    logger.info(
        "Payment confirmed. order=%s user=%s ip=%s",
        order.id,
        request.user.id,
        request.META.get("REMOTE_ADDR"),
    )
    log_activity(
        request,
        event_type="payment_confirm",
        metadata={
            "order_id": order.id,
            "payment_method": "bank",
        },
    )
    messages.success(request, "Đã xác nhận thanh toán chuyển khoản.")
    return redirect("orders:order_success", order_id=order.id)


def vnpay_payment(request: HttpRequest, order_id) -> HttpResponse:
    order = get_visitable_order(request, order_id)
    if order.payment_method != "vnpay":
        return redirect("orders:order_success", order_id=order.id)
    if order.is_paid:
        return redirect("orders:order_success", order_id=order.id)
    if order.status == "cancelled":
        return redirect("orders:order_failed", order_id=order.id)

    from ..vnpay import build_payment_url, is_configured

    if not is_configured():
        messages.error(
            request,
            "Cổng thanh toán VNPay chưa được cấu hình. Vui lòng thử chuyển khoản ngân hàng.",
        )
        return redirect("orders:order_success", order_id=order.id)

    return_url = request.build_absolute_uri(reverse("orders:vnpay_return"))
    ip_addr = request.META.get("REMOTE_ADDR", "127.0.0.1")
    payment_url = build_payment_url(order, ip_addr, return_url)
    if not payment_url:
        messages.error(
            request, "Không tạo được phiên thanh toán VNPay. Vui lòng thử lại."
        )
        return redirect("orders:order_review", order_id=order.id)
    return redirect(payment_url)


def vnpay_return(request: HttpRequest) -> HttpResponse:
    """VNPay chuyển hướng về đây sau khi khách thanh toán."""
    from ..vnpay import verify_return

    params = request.GET.dict()
    if not verify_return(params):
        messages.error(request, "Chữ ký thanh toán không hợp lệ.")
        return redirect("products:product_list")

    txn_ref = params.get("vnp_TxnRef", "")
    response_code = params.get("vnp_ResponseCode", "")
    order = Order.objects.filter(id=txn_ref).first()
    if not order:
        messages.error(request, "Không tìm thấy đơn hàng.")
        return redirect("orders:my_orders")

    if order.is_paid:
        messages.info(request, "Đơn hàng đã được thanh toán trước đó.")
        return redirect("orders:order_success", order_id=order.id)
    if response_code == "00":
        if order.status == "cancelled":
            reserve_order_stock(order)
        order.is_paid = True
        order.status = "processing"
        order.save(update_fields=["is_paid", "status", "updated_at"])
        from ..services.order_email import send_order_email

        send_order_email(order, event="paid")
        log_activity(
            request,
            event_type="payment_confirm",
            metadata={
                "order_id": order.id,
                "payment_method": "vnpay",
                "vnp_ResponseCode": response_code,
            },
        )
        messages.success(request, "Thanh toán VNPay thành công.")
        return redirect("orders:order_success", order_id=order.id)

    restore_order_stock(order)
    order.status = "cancelled"
    order.save(update_fields=["status", "updated_at"])
    from ..services.order_email import send_order_email

    send_order_email(order, event="cancelled")
    return redirect("orders:order_failed", order_id=order.id)


@transaction.atomic
def vnpay_ipn(request: HttpRequest) -> HttpResponse:
    """Server-to-server IPN của VNPay gọi lại. Trả về RspCode để VNPay xác nhận."""
    from ..vnpay import verify_return

    params = request.GET.dict()
    order_id = params.get("vnp_TxnRef", "")
    if not verify_return(params):
        return JsonResponse({"RspCode": "97", "Message": "Invalid signature"})
    order = Order.objects.filter(id=order_id).first()
    if order is None:
        return JsonResponse({"RspCode": "01", "Message": "Order not found"})
    response_code = params.get("vnp_ResponseCode", "")
    transaction_status = params.get("vnp_TransactionStatus", "")
    if response_code == "00" and transaction_status == "00" and not order.is_paid:
        if order.status == "cancelled":
            reserve_order_stock(order)
        order.is_paid = True
        order.status = "processing"
        order.save(update_fields=["is_paid", "status", "updated_at"])
        from ..services.order_email import send_order_email

        send_order_email(order, event="paid")
        return JsonResponse({"RspCode": "00", "Message": "Confirm Success"})
    if order.is_paid:
        return JsonResponse({"RspCode": "02", "Message": "Order already confirmed"})
    return JsonResponse({"RspCode": "97", "Message": "Payment not successful"})


@require_POST
@transaction.atomic
def bank_payment_cancel(request: HttpRequest, order_id) -> HttpResponse:
    order = get_visitable_order(request, order_id, Order.objects.select_for_update())
    if order.payment_method != "bank":
        messages.error(request, "Đơn hàng này không dùng chuyển khoản ngân hàng.")
        return redirect("orders:order_success", order_id=order.id)
    if order.status == "cancelled":
        messages.info(request, "Đơn hàng đã được hủy trước đó.")
        return redirect("orders:order_success", order_id=order.id)
    if order.is_paid:
        messages.error(request, "Đơn hàng đã thanh toán, không thể hủy thanh toán.")
        return redirect("orders:order_success", order_id=order.id)

    restore_order_stock(order)
    order.status = "cancelled"
    order.save(update_fields=["status", "updated_at"])
    messages.warning(request, "Đơn hàng chưa thành công do bạn đã hủy thanh toán.")
    return redirect("orders:order_failed", order_id=order.id)


def order_failed(request: HttpRequest, order_id) -> HttpResponse:
    order = get_visitable_order(request, order_id)
    expired_by_timeout = "[AUTO_TIMEOUT_15_MIN]" in (order.note or "")
    reason = "expired" if expired_by_timeout else "cancelled"
    if request.GET.get("reason"):
        reason = request.GET.get("reason")
    readable_reason = (
        "Quá 15 phút chưa thanh toán" if reason == "expired" else "Đã hủy thanh toán"
    )
    return render(
        request,
        "shop/order_failed.html",
        {"order": order, "failed_reason": readable_reason},
    )


@transaction.atomic
def bank_payment_mobile(request: HttpRequest, token, order_id) -> HttpResponse:
    expected = _payment_token(order_id)
    if token != expected:
        raise Http404
    order = get_object_or_404(
        Order.objects.select_for_update(), id=order_id, payment_method="bank"
    )

    success_url = request.build_absolute_uri(
        reverse("orders:order_success", kwargs={"order_id": order.id})
    )
    failed_url = request.build_absolute_uri(
        reverse("orders:order_failed", kwargs={"order_id": order.id})
    )
    ctx = {
        "order": order,
        "token": token,
        "success_url": success_url,
        "failed_url": failed_url,
    }

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "confirm":
            if expire_bank_order_if_needed(order):
                ctx.update({"expired": True})
                return render(request, "shop/bank_payment_mobile.html", ctx)
            if order.status == "cancelled":
                ctx.update({"cancelled": True})
                return render(request, "shop/bank_payment_mobile.html", ctx)
            if order.is_paid:
                ctx.update({"paid": True, "just_paid": True})
                return render(request, "shop/bank_payment_mobile.html", ctx)
            order.is_paid = True
            order.status = "processing"
            order.save(update_fields=["is_paid", "status", "updated_at"])
            from ..services.order_email import send_order_email

            send_order_email(order, event="paid")
            ctx.update({"paid": True, "just_paid": True})
            return render(request, "shop/bank_payment_mobile.html", ctx)
        elif action == "cancel":
            if order.is_paid:
                ctx.update({"paid": True})
                return render(request, "shop/bank_payment_mobile.html", ctx)
            if expire_bank_order_if_needed(order):
                ctx.update({"expired": True})
                return render(request, "shop/bank_payment_mobile.html", ctx)
            restore_order_stock(order)
            order.status = "cancelled"
            order.save(update_fields=["status", "updated_at"])
            from ..services.order_email import send_order_email

            send_order_email(order, event="cancelled")
            ctx.update({"cancelled": True, "just_cancelled": True})
            return render(request, "shop/bank_payment_mobile.html", ctx)

    if expire_bank_order_if_needed(order):
        ctx.update({"expired": True})
        return render(request, "shop/bank_payment_mobile.html", ctx)
    if order.is_paid:
        ctx.update({"paid": True})
        return render(request, "shop/bank_payment_mobile.html", ctx)
    if order.status == "cancelled":
        ctx.update({"cancelled": True})
        return render(request, "shop/bank_payment_mobile.html", ctx)

    selected_bank = BANKS.get(order.bank_code) or BANKS["VCB"]
    ctx.update(
        {
            "selected_bank_name": selected_bank["name"],
            "shop_bank_account": SHOP_BANK_ACCOUNT,
            "shop_account_name": SHOP_ACCOUNT_NAME,
            "qr_url": build_vietqr_url(
                order.bank_code, order.total_amount, f"DH{order.id}"
            ),
            "expired": False,
            "paid": False,
        }
    )
    return render(request, "shop/bank_payment_mobile.html", ctx)
