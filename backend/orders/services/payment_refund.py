"""
Payment orchestration service - Part 4a: Refund request and gateway refund
"""
from typing import Optional

from django.db import transaction

from orders.models import Order, Payment, Refund
from orders.services.payments import paypal, vnpay
from orders.services.payments.base import GatewayOutcome

from .payment_service import (
    _now_utc, _vnpay_transaction_date, PaymentServiceError, PaymentGatewayError,
)


@transaction.atomic
def request_refund(
    order: Order,
    requested_by,
    amount_minor: Optional[int] = None,
    reason: str = "",
) -> Refund:
    """Create a refund request for an order."""
    if order.status not in {"confirmed", "shipping", "done"}:
        raise PaymentServiceError("Đơn hàng không thể hoàn tiền ở trạng thái này")

    payment = getattr(order, "payment", None)
    if not payment or payment.status != "paid":
        raise PaymentServiceError("Đơn hàng chưa được thanh toán")

    # Default to full amount
    if amount_minor is None:
        amount_minor = payment.amount_minor

    # Check if already has pending refund
    existing = Refund.objects.filter(payment=payment, status__in={"scheduled", "processing"}).first()
    if existing:
        raise PaymentServiceError("Đã có yêu cầu hoàn tiền đang xử lý")

    # Create refund (scheduled - can add holding period logic here)
    refund = Refund.objects.create(
        payment=payment,
        requested_by=requested_by,
        amount_minor=amount_minor,
        currency=payment.currency,
        reason=reason,
        status="scheduled",
        due_at=_now_utc(),  # Immediate processing for now
    )

    # Update payment status
    payment.status = "refund_pending"
    payment.save(update_fields=["status", "updated_at"])

    return refund


@transaction.atomic
def _run_gateway_refund(payment: Payment, refund: Refund) -> GatewayOutcome:
    """Execute refund via payment gateway."""
    if payment.provider == "vnpay":
        if not payment.provider_txn_id:
            raise PaymentGatewayError("Thiếu mã giao dịch VNPay để hoàn tiền")

        trans_date = _vnpay_transaction_date(payment)
        return vnpay.refund(
            txn_ref=payment.txn_ref,
            amount_minor=refund.amount_minor,
            transaction_no=payment.provider_txn_id,
            transaction_date=trans_date,
        )

    elif payment.provider == "paypal":
        if not payment.provider_txn_id:
            raise PaymentGatewayError("Thiếu mã capture PayPal để hoàn tiền")

        return paypal.refund(
            capture_id=payment.provider_txn_id,
            amount_minor=refund.amount_minor,
            currency=refund.currency,
            request_id=f"refund-{refund.id}",
        )

    raise PaymentGatewayError(f"Không hỗ trợ hoàn tiền cho provider: {payment.provider}")