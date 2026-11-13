"""
Payment orchestration service - Part 3: Callback handling
"""

from typing import Dict

from django.conf import settings
from django.db import transaction

from orders.models import Payment
from orders.services.payments import paypal, vnpay
from orders.services.payments.base import GatewayOutcome

from .payment_service import (
    _now_utc,
    InvalidSignature,
    PaymentNotFound,
    AmountMismatch,
)


@transaction.atomic
def handle_vnpay_callback(params: Dict[str, str], ip_addr: str) -> GatewayOutcome:
    """Process VNPay callback (return or IPN)."""
    # Verify signature
    vnpay_hash_secret = getattr(settings, "VNPAY_HASH_SECRET", "")
    if not vnpay.verify_callback(params, vnpay_hash_secret):
        raise InvalidSignature("Chữ ký VNPay không hợp lệ")

    # Parse outcome
    outcome = vnpay.outcome_from_callback(params)

    # Find payment by txn_ref
    txn_ref = params.get("vnp_TxnRef", "")
    try:
        payment = Payment.objects.select_for_update().get(txn_ref=txn_ref)
    except Payment.DoesNotExist:
        raise PaymentNotFound(f"Không tìm thấy thanh toán cho txn_ref: {txn_ref}")

    # Verify amount matches
    if (
        outcome.amount_minor is not None
        and outcome.amount_minor != payment.amount_minor
    ):
        raise AmountMismatch("Số tiền callback không khớp")

    # Update payment
    payment.provider_txn_id = outcome.provider_txn_id or ""
    payment.provider_status = outcome.provider_status or ""
    payment.raw_payload = outcome.raw
    payment.status = outcome.status
    payment.updated_at = _now_utc()
    payment.save(
        update_fields=[
            "provider_txn_id",
            "provider_status",
            "raw_payload",
            "status",
            "updated_at",
        ]
    )

    # If paid, update order
    if outcome.status == "paid":
        order = payment.order
        order.is_paid = True
        order.status = "confirmed"
        order.gateway_transaction_id = outcome.provider_txn_id
        order.updated_at = _now_utc()
        order.save(
            update_fields=["is_paid", "status", "gateway_transaction_id", "updated_at"]
        )

    return outcome


@transaction.atomic
def handle_paypal_callback(
    order_code: str, payer_id: str, payment_id: str
) -> GatewayOutcome:
    """Process PayPal callback after user approval."""
    try:
        payment = Payment.objects.select_for_update().get(
            order__order_code=order_code, provider="paypal"
        )
    except Payment.DoesNotExist:
        raise PaymentNotFound(f"Không tìm thấy thanh toán PayPal cho đơn: {order_code}")

    # Capture PayPal order
    outcome = paypal.capture_order(payment.provider_txn_id)

    payment.provider_txn_id = outcome.provider_txn_id or payment_id
    payment.provider_status = outcome.provider_status or ""
    payment.raw_payload = outcome.raw
    payment.status = outcome.status
    payment.updated_at = _now_utc()
    payment.save(
        update_fields=[
            "provider_txn_id",
            "provider_status",
            "raw_payload",
            "status",
            "updated_at",
        ]
    )

    if outcome.status == "paid":
        order = payment.order
        order.is_paid = True
        order.status = "confirmed"
        order.gateway_transaction_id = outcome.provider_txn_id
        order.updated_at = _now_utc()
        order.save(
            update_fields=["is_paid", "status", "gateway_transaction_id", "updated_at"]
        )

    return outcome
