import logging
from datetime import timedelta

from django.contrib import messages
from django.db import transaction
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from core.ratelimit import rate_limit

from users.activity import log_activity

from .cart import (
    build_vietqr_url,
    expire_bank_order_if_needed,
    _payment_token,
    restore_order_stock,
)
from .order import decorate_order_tracking
from ..constants import (
    PAYMENT_TIMEOUT_MINUTES,
    SHOP_ACCOUNT_NAME,
    SHOP_BANK_ACCOUNT,
    bank_transfer_is_enabled,
    shop_bank_meta,
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
    if order.payment_method == "bank" and shop_bank_meta():
        selected_bank_name = shop_bank_meta()["name"]
        qr_url = build_vietqr_url(order.total_amount, f"DH{order.id}")

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

    selected_bank = shop_bank_meta()
    expires_at = order.created_at + timedelta(minutes=PAYMENT_TIMEOUT_MINUTES)
    qr_url = build_vietqr_url(order.total_amount, f"DH{order.id}")
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
            "selected_bank_name": selected_bank.get("name", ""),
            "shop_bank_account": SHOP_BANK_ACCOUNT,
            "shop_account_name": SHOP_ACCOUNT_NAME,
            "qr_url": qr_url,
            "mobile_url": mobile_url,
            "confirm_url": confirm_url,
            "token": token,
            "expires_at_iso": expires_at.isoformat(),
            "payment_timeout_minutes": PAYMENT_TIMEOUT_MINUTES,
            "bank_transfer_enabled": bank_transfer_is_enabled(),
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

    logger.info(
        "Customer requested bank payment verification. order=%s user=%s ip=%s",
        order.id,
        request.user.id,
        request.META.get("REMOTE_ADDR"),
    )
    messages.info(
        request,
        "Đã gửi yêu cầu kiểm tra. Đơn hàng chỉ được ghi nhận đã thanh toán sau khi shop đối soát giao dịch.",
    )
    return redirect("orders:bank_payment_waiting", order_id=order.id)


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


@transaction.atomic
def vnpay_return(request: HttpRequest) -> HttpResponse:
    """VNPay chuyển hướng về đây sau khi khách thanh toán."""
    from ..vnpay import amount_matches, verify_return

    params = request.GET.dict()
    if not verify_return(params):
        messages.error(request, "Chữ ký thanh toán không hợp lệ.")
        return redirect("products:product_list")

    txn_ref = params.get("vnp_TxnRef", "")
    response_code = params.get("vnp_ResponseCode", "")
    order = Order.objects.select_for_update().filter(id=txn_ref).first()
    if not order:
        messages.error(request, "Không tìm thấy đơn hàng.")
        return redirect("orders:my_orders")
    if order.payment_method != "vnpay" or not amount_matches(order, params):
        messages.error(request, "Số tiền thanh toán không khớp đơn hàng.")
        return redirect("orders:my_orders")

    transaction_id = params.get("vnp_TransactionNo", "").strip()
    succeeded = (
        response_code == "00"
        and params.get("vnp_TransactionStatus") == "00"
        and bool(transaction_id)
    )
    if order.is_paid:
        if transaction_id and order.vnpay_transaction_id not in (None, transaction_id):
            logger.error("VNPay transaction mismatch for paid order %s", order.id)
            messages.error(request, "Giao dịch không khớp; shop cần đối soát đơn hàng.")
            return redirect("orders:my_orders")
        messages.info(request, "Đơn hàng đã được thanh toán trước đó.")
        return redirect("orders:order_success", order_id=order.id)
    if succeeded:
        order.is_paid = True
        order.vnpay_transaction_id = transaction_id
        fields = ["is_paid", "vnpay_transaction_id", "updated_at"]
        if order.status == "cancelled":
            logger.error(
                "Late VNPay payment captured for cancelled order %s; manual reconciliation required",
                order.id,
            )
            messages.warning(
                request,
                "VNPay đã thu tiền nhưng đơn đã bị hủy. Shop cần đối soát và xử lý hoàn tiền; đơn chưa được mở giao lại.",
            )
        else:
            order.status = "processing"
            fields.append("status")
            from ..services.order_email import send_order_email

            send_order_email(order, event="paid")
            messages.success(request, "Thanh toán VNPay thành công.")
            order._status_change_source = "vnpay_return"
            order._status_change_transaction_id = transaction_id
            order._status_change_note = "VNPay xác nhận thanh toán thành công."
        order.save(update_fields=fields)
        log_activity(
            request,
            event_type="payment_confirm",
            metadata={
                "order_id": order.id,
                "payment_method": "vnpay",
                "vnp_ResponseCode": response_code,
                "vnp_TransactionNo": transaction_id,
            },
        )
        return redirect("orders:order_success", order_id=order.id)

    if order.status != "cancelled":
        restore_order_stock(order)
        order.status = "cancelled"
        order._status_change_source = "vnpay_return"
        order._status_change_transaction_id = transaction_id
        order._status_change_note = (
            f"VNPay từ chối giao dịch, mã phản hồi {response_code}."
        )
        order.save(update_fields=["status", "updated_at"])
        from ..services.order_email import send_order_email

        send_order_email(order, event="cancelled")
    return redirect("orders:order_failed", order_id=order.id)


@transaction.atomic
def vnpay_ipn(request: HttpRequest) -> HttpResponse:
    """Server-to-server IPN của VNPay gọi lại. Trả về RspCode để VNPay xác nhận."""
    from ..vnpay import amount_matches, verify_return

    params = request.GET.dict()
    order_id = params.get("vnp_TxnRef", "")
    if not verify_return(params):
        return JsonResponse({"RspCode": "97", "Message": "Invalid signature"})
    with transaction.atomic():
        order = Order.objects.select_for_update().filter(id=order_id).first()
        if order is None:
            return JsonResponse({"RspCode": "01", "Message": "Order not found"})
        if order.payment_method != "vnpay" or not amount_matches(order, params):
            return JsonResponse({"RspCode": "97", "Message": "Amount mismatch"})
        response_code = params.get("vnp_ResponseCode", "")
        transaction_status = params.get("vnp_TransactionStatus", "")
        transaction_id = params.get("vnp_TransactionNo", "").strip()
        if order.is_paid:
            if transaction_id and order.vnpay_transaction_id not in (
                None,
                transaction_id,
            ):
                logger.error("VNPay transaction mismatch for paid order %s", order.id)
                return JsonResponse(
                    {"RspCode": "97", "Message": "Transaction mismatch"}
                )
            return JsonResponse({"RspCode": "02", "Message": "Order already confirmed"})
        if response_code != "00" or transaction_status != "00" or not transaction_id:
            if order.status != "cancelled":
                restore_order_stock(order)
                order.status = "cancelled"
                order._status_change_source = "vnpay_ipn"
                order._status_change_transaction_id = transaction_id
                order._status_change_note = (
                    f"VNPay IPN thất bại, mã phản hồi {response_code}."
                )
                order.save(update_fields=["status", "updated_at"])
                from ..services.order_email import send_order_email

                send_order_email(order, event="cancelled")
            return JsonResponse({"RspCode": "97", "Message": "Payment not successful"})

        order.is_paid = True
        order.vnpay_transaction_id = transaction_id
        fields = ["is_paid", "vnpay_transaction_id", "updated_at"]
        if order.status != "cancelled":
            order.status = "processing"
            fields.append("status")
            from ..services.order_email import send_order_email

            send_order_email(order, event="paid")
        else:
            logger.error(
                "Late VNPay IPN for cancelled order %s; manual reconciliation required",
                order.id,
            )
        if "status" in fields:
            order._status_change_source = "vnpay_ipn"
            order._status_change_transaction_id = transaction_id
            order._status_change_note = "VNPay IPN xác nhận thanh toán thành công."
        order.save(update_fields=fields)
        return JsonResponse({"RspCode": "00", "Message": "Confirm Success"})


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
    order._status_changed_by_id = (
        request.user.pk if request.user.is_authenticated else None
    )
    order._status_change_source = "bank_payment_cancel"
    order._status_change_note = "Khách hủy giao dịch chuyển khoản."
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
        "bank_transfer_enabled": bank_transfer_is_enabled(),
    }

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "confirm":
            if not bank_transfer_is_enabled():
                ctx.update({"bank_transfer_unavailable": True})
                return render(request, "shop/bank_payment_mobile.html", ctx)
            if expire_bank_order_if_needed(order):
                ctx.update({"expired": True})
                return render(request, "shop/bank_payment_mobile.html", ctx)
            if order.status == "cancelled":
                ctx.update({"cancelled": True})
                return render(request, "shop/bank_payment_mobile.html", ctx)
            if order.is_paid:
                ctx.update({"paid": True, "just_paid": True})
                return render(request, "shop/bank_payment_mobile.html", ctx)
            logger.info(
                "Customer requested bank payment verification. order=%s user=%s ip=%s",
                order.id,
                request.user.id,
                request.META.get("REMOTE_ADDR"),
            )
            ctx.update({"verification_pending": True})
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
            order._status_changed_by_id = (
                request.user.pk if request.user.is_authenticated else None
            )
            order._status_change_source = "bank_payment_cancel"
            order._status_change_note = (
                "Khách hủy giao dịch chuyển khoản trên điện thoại."
            )
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

    selected_bank = shop_bank_meta()
    ctx.update(
        {
            "selected_bank_name": selected_bank.get("name", ""),
            "shop_bank_account": SHOP_BANK_ACCOUNT,
            "shop_account_name": SHOP_ACCOUNT_NAME,
            "qr_url": build_vietqr_url(order.total_amount, f"DH{order.id}"),
            "expired": False,
            "paid": False,
            "bank_transfer_enabled": bank_transfer_is_enabled(),
        }
    )
    return render(request, "shop/bank_payment_mobile.html", ctx)


@require_POST
@rate_limit(
    "vnpay_refund",
    max_requests=10,
    window=300,
    error_msg="Quá nhiều yêu cầu hoàn tiền. Vui lòng thử lại sau.",
)
def vnpay_refund(request: HttpRequest) -> JsonResponse:
    """API hoàn tiền VNPay (hỗ trợ partial refund).

    POST data:
    - order_id: ID đơn hàng
    - amount: Số tiền hoàn (VND)
    - trans_id: Transaction ID từ VNPay (vnp_TransactionNo)
    - reason: Lý do hoàn tiền (optional)
    """
    import json
    import re

    # Refunds are financial operations and require the order-management role.
    from users.permissions import can_manage_orders

    if not request.user.is_authenticated or not can_manage_orders(request.user):
        return JsonResponse(
            {"success": False, "message": "Không có quyền truy cập"}, status=403
        )

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Invalid JSON"}, status=400)

    order_id = data.get("order_id")
    amount = data.get("amount")
    trans_id = data.get("trans_id")
    reason = data.get("reason", "Hoàn tiền theo yêu cầu")
    request_id = request.headers.get("Idempotency-Key") or data.get("request_id")

    if not order_id or amount is None or not trans_id or not request_id:
        return JsonResponse(
            {
                "success": False,
                "message": "Cần order_id, amount, trans_id và Idempotency-Key (8–32 ký tự).",
            },
            status=400,
        )
    request_id = str(request_id).strip()
    trans_id = str(trans_id).strip()
    if isinstance(order_id, bool) or not str(order_id).isdecimal():
        return JsonResponse(
            {"success": False, "message": "Mã đơn hàng không hợp lệ."}, status=400
        )
    order_id = int(order_id)
    if not re.fullmatch(r"[A-Za-z0-9_-]{8,32}", request_id):
        return JsonResponse(
            {"success": False, "message": "Idempotency-Key không hợp lệ."}, status=400
        )
    if not trans_id or len(trans_id) > 64:
        return JsonResponse(
            {"success": False, "message": "Mã giao dịch không hợp lệ."}, status=400
        )

    if isinstance(amount, bool) or not (
        isinstance(amount, int) or isinstance(amount, str) and amount.isdecimal()
    ):
        return JsonResponse(
            {"success": False, "message": "Số tiền không hợp lệ"}, status=400
        )
    amount = int(amount)
    if amount <= 0:
        return JsonResponse(
            {"success": False, "message": "Số tiền hoàn phải lớn hơn 0"}, status=400
        )

    from ..models import RefundRecord

    with transaction.atomic():
        order = get_object_or_404(Order.objects.select_for_update(), id=order_id)
        existing = RefundRecord.objects.filter(request_id=request_id).first()
        if existing:
            if (
                existing.order_id != order.id
                or int(existing.amount) != amount
                or existing.transaction_id != trans_id
            ):
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Idempotency-Key đã dùng cho yêu cầu khác.",
                    },
                    status=409,
                )
            if existing.status == "succeeded":
                return JsonResponse(
                    {
                        "success": True,
                        "message": "Yêu cầu này đã hoàn trước đó.",
                        "refund_amount": int(existing.amount),
                        "request_id": request_id,
                    }
                )
            if existing.status == "pending":
                return JsonResponse(
                    {
                        "success": False,
                        "pending": True,
                        "message": "Yêu cầu đang chờ đối soát; không gửi lại để tránh hoàn trùng.",
                        "request_id": request_id,
                    },
                    status=202,
                )
            return JsonResponse(
                {
                    "success": False,
                    "message": "VNPay đã từ chối yêu cầu này; dùng mã yêu cầu mới sau khi kiểm tra.",
                    "request_id": request_id,
                },
                status=409,
            )

        if order.payment_method != "vnpay" or not order.is_paid:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Đơn phải được thanh toán thành công qua VNPay.",
                },
                status=400,
            )
        if order.vnpay_transaction_id and order.vnpay_transaction_id != trans_id:
            return JsonResponse(
                {"success": False, "message": "Mã giao dịch không khớp đơn hàng."},
                status=400,
            )
        return_request = None
        if order.status in {"shipping", "delivered"}:
            return_request = order.return_requests.filter(
                status="received", return_type="refund"
            ).first()
            if return_request is None:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Chỉ hoàn đơn đang giao/đã giao sau khi shop nhận và kiểm tra hàng trả.",
                    },
                    status=409,
                )
        reserved_amount = sum(
            RefundRecord.objects.filter(
                order=order, status__in=["pending", "succeeded"]
            ).values_list("amount", flat=True)
        )
        if amount + reserved_amount > order.total_amount:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Tổng tiền hoàn vượt quá số tiền đơn đã thanh toán.",
                },
                status=400,
            )
        if return_request and amount + reserved_amount > return_request.refund_amount:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Số tiền hoàn vượt giá trị các sản phẩm đã nhận trả.",
                },
                status=400,
            )
        record = RefundRecord.objects.create(
            order=order,
            request_id=request_id,
            transaction_id=trans_id,
            amount=amount,
            reason=str(reason)[:255],
            requested_by=request.user,
        )

    # Gọi API refund VNPay
    from orders.vnpay import refund_transaction

    result = refund_transaction(
        order, amount, trans_id, request.user.username, request_id=request_id
    )
    with transaction.atomic():
        record = RefundRecord.objects.select_for_update().get(pk=record.pk)
        record.gateway_code = str(result.get("response_code") or "")[:20]
        record.gateway_response = result.get("data") or {}
        if result.get("success"):
            record.status = "succeeded"
        elif not result.get("ambiguous"):
            record.status = "failed"
        record.save(
            update_fields=["status", "gateway_code", "gateway_response", "updated_at"]
        )
        if record.status == "succeeded":
            order = Order.objects.select_for_update().get(pk=record.order_id)
            order.refunded_amount = sum(
                RefundRecord.objects.filter(
                    order=order, status="succeeded"
                ).values_list("amount", flat=True)
            )
            fields = ["refunded_amount", "updated_at"]
            if order.refunded_amount >= order.total_amount and order.status in {
                "pending",
                "processing",
            }:
                restore_order_stock(order)
                order.status = "cancelled"
                order._status_changed_by_id = request.user.pk
                order._status_change_source = "vnpay_refund"
                order._status_change_transaction_id = trans_id
                order._status_change_note = (
                    f"Hoàn toàn bộ đơn qua VNPay; mã yêu cầu {request_id}."
                )
                fields.append("status")
            order.save(update_fields=fields)

    if result.get("success"):
        log_activity(
            request,
            event_type="refund",
            metadata={
                "order_id": order.id,
                "amount": amount,
                "trans_id": trans_id,
                "request_id": request_id,
                "reason": reason,
                "vnpay_response": result.get("data"),
            },
        )

        return JsonResponse(
            {
                "success": True,
                "message": "VNPay đã xác nhận hoàn tiền.",
                "refund_amount": amount,
                "refunded_total": int(order.refunded_amount),
                "request_id": request_id,
            }
        )
    if result.get("ambiguous"):
        logger.error(
            "VNPay refund outcome unknown; manual reconciliation required: %s",
            request_id,
        )
        return JsonResponse(
            {
                "success": False,
                "pending": True,
                "message": "Chưa xác định được kết quả từ VNPay; cần đối soát, không gửi lại yêu cầu.",
                "request_id": request_id,
            },
            status=202,
        )
    return JsonResponse(
        {
            "success": False,
            "message": result.get("message", "VNPay từ chối hoàn tiền."),
            "request_id": request_id,
        },
        status=400,
    )
