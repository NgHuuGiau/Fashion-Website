"""
Payment orchestration service - Part 4b: Confirm/Reject refund
"""
from datetime import timezone as tz, timedelta as td

from django.db import transaction

from orders.models import Payment, Refund

from .payment_refund import _run_gateway_refund
from .payment_service import _now_utc, PaymentServiceError, PaymentGatewayError

GMT7 = tz(td(hours=7))


@transaction.atomic
def confirm_refund(refund_id: int, admin, reason: str = "") -> Refund:
    """Admin confirms and processes a refund."""
    refund = Refund.objects.select_for_update().get(id=refund_id)

    if refund.status not in {"scheduled", "failed", "processing"}:
        raise PaymentServiceError("Yêu cầu hoàn tiền không thể xác nhận")

    if refund.due_at > _now_utc():
        remaining = refund.due_at - _now_utc()
        hours = max(1, int(remaining.total_seconds() // 3600))
        raise PaymentServiceError(f"Chưa đủ thời gian giữ tiền; còn {hours} giờ nữa")

    payment = Payment.objects.select_for_update().get(id=refund.payment_id)
    if payment.status not in {"paid", "refund_pending"}:
        raise PaymentServiceError("Thanh toán không ở trạng thái có thể hoàn tiền")

    refund.status = "processing"
    refund.confirmed_by = admin
    refund.confirmed_at = _now_utc()
    refund.reason = reason or refund.reason
    refund.updated_at = _now_utc()
    refund.save(update_fields=["status", "confirmed_by", "confirmed_at", "reason", "updated_at"])

    try:
        outcome = _run_gateway_refund(payment, refund)
    except PaymentGatewayError as exc:
        refund.status = "failed"
        refund.raw_payload = {"error": str(exc)}
        refund.updated_at = _now_utc()
        refund.save(update_fields=["status", "raw_payload", "updated_at"])
        raise PaymentServiceError(f"Hoàn tiền thất bại: {exc}") from exc

    refund.raw_payload = outcome.raw
    refund.provider_refund_id = outcome.provider_txn_id
    refund.updated_at = _now_utc()

    if outcome.status == "refunded":
        refund.status = "succeeded"
        payment.status = "refunded"
        payment.provider_status = outcome.provider_status or payment.provider_status
        payment.raw_payload = {**(payment.raw_payload or {}), **outcome.raw}
        payment.save(update_fields=["status", "provider_status", "raw_payload", "updated_at"])

        order = payment.order
        order.status = "refunded"
        order.refunded_amount = refund.amount_minor / 100
        order.is_paid = False
        order.updated_at = _now_utc()
        order.save(update_fields=["status", "refunded_amount", "is_paid", "updated_at"])
    else:
        refund.status = "failed"

    refund.save(update_fields=["status", "provider_refund_id", "raw_payload", "updated_at"])
    return refund


@transaction.atomic
def reject_refund(refund_id: int, admin, reason: str = "") -> Refund:
    """Admin rejects a refund request."""
    refund = Refund.objects.select_for_update().get(id=refund_id)

    if refund.status not in {"scheduled", "failed", "processing"}:
        raise PaymentServiceError("Yêu cầu hoàn tiền không thể từ chối")

    payment = Payment.objects.get(id=refund.payment_id)

    refund.status = "rejected"
    refund.reason = (reason or "").strip()[:255] or refund.reason
    refund.confirmed_by = admin
    refund.confirmed_at = _now_utc()
    refund.updated_at = _now_utc()
    refund.save(update_fields=["status", "reason", "confirmed_by", "confirmed_at", "updated_at"])

    # No money moved, payment returns to paid state
    if payment.status == "refund_pending":
        payment.status = "paid"
        payment.save(update_fields=["status", "updated_at"])

    return refund