"""
Payment orchestration service - Part 2: Session creation
"""

from typing import Dict, Any, Optional

from django.conf import settings
from django.db import transaction

from orders.models import Order, Payment
from orders.services.payments import paypal, vnpay

from .payment_service import (
    _txn_ref,
    get_client_ip,
    get_vnpay_return_url,
    SESSIONABLE,
    PaymentServiceError,
    PaymentGatewayError,
)


@transaction.atomic
def create_payment_session(
    order: Order,
    payment_method: str,
    request,
    ip_addr: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create or resume a payment session for an order.
    Returns dict with provider, url, simulation flag, amount, currency.
    """
    if order.status == "cancelled":
        raise PaymentServiceError("Đơn hàng đã hủy")

    # Get or create payment record
    payment, created = Payment.objects.get_or_create(
        order=order,
        defaults={
            "provider": payment_method,
            "status": "pending",
            "amount_minor": 0,
            "currency": "VND",
        },
    )

    if payment.status not in SESSIONABLE:
        raise PaymentServiceError("Đơn hàng không chờ thanh toán")

    # Mock payment mode
    if getattr(settings, "PAYMENT_MODE", "mock") == "mock" or payment_method == "mock":
        return {
            "provider": "mock",
            "url": request.build_absolute_uri(
                f"/orders/payment/mock/?order_code={order.order_code}"
            ),
            "simulation": True,
            "amount_minor": int(order.total_amount * 100),
            "currency": "VND",
        }

    # Update payment attempt
    attempt = payment.attempt or 1
    if payment.status == "failed" or payment.txn_ref:
        attempt += 1

    payment.provider = payment_method
    payment.attempt = attempt
    payment.txn_ref = _txn_ref(order.order_code, attempt)

    if payment_method == "vnpay":
        payment.currency = "VND"
        payment.amount_minor = int(order.total_amount * 100)
        payment.save(
            update_fields=[
                "provider",
                "attempt",
                "txn_ref",
                "currency",
                "amount_minor",
                "updated_at",
            ]
        )

        try:
            return_url = get_vnpay_return_url(request)
            url = vnpay.build_payment_url(
                txn_ref=payment.txn_ref,
                amount_vnd=order.total_amount,
                order_info=f"Thanh toan don hang {order.order_code}",
                ip_addr=ip_addr or get_client_ip(request),
                return_url=return_url,
            )
        except PaymentGatewayError as exc:
            raise PaymentServiceError(str(exc)) from exc

        return {
            "provider": "vnpay",
            "url": url,
            "simulation": False,
            "amount_minor": payment.amount_minor,
            "currency": "VND",
        }

    elif payment_method == "paypal":
        payment.currency = getattr(settings, "PAYPAL_CURRENCY", "USD").upper()
        payment.amount_minor = paypal.vnd_to_usd_minor(settings, order.total_amount)
        payment.save(
            update_fields=[
                "provider",
                "attempt",
                "txn_ref",
                "currency",
                "amount_minor",
                "updated_at",
            ]
        )

        try:
            gateway_order = paypal.create_order(
                code=order.order_code,
                txn_ref=payment.txn_ref,
                amount_minor=payment.amount_minor,
                currency=payment.currency,
                base_url=request.build_absolute_uri("/"),
            )
        except PaymentGatewayError as exc:
            raise PaymentServiceError(str(exc)) from exc

        url = paypal.approve_url(gateway_order)

        return {
            "provider": "paypal",
            "url": url,
            "simulation": False,
            "amount_minor": payment.amount_minor,
            "currency": payment.currency,
        }

    elif payment_method in ("cod", "bank_transfer"):
        # These don't need external session - handled by order flow
        payment.status = "pending"
        payment.save(update_fields=["status", "updated_at"])
        return {
            "provider": payment_method,
            "url": request.build_absolute_uri(f"/orders/{order.order_code}/"),
            "simulation": True,
            "amount_minor": int(order.total_amount * 100),
            "currency": "VND",
        }

    else:
        raise PaymentServiceError(
            f"Phương thức thanh toán không hỗ trợ: {payment_method}"
        )
