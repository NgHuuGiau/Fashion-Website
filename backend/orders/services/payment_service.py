"""
Payment orchestration service - Part 1: Core functions and session creation
Ported from ElectroHub - adapted for Django
"""
import re
from datetime import datetime, timezone, timedelta


from orders.models import Payment
from orders.services.payments.base import PaymentGatewayError

GMT7 = timezone(timedelta(hours=7))


class PaymentServiceError(Exception):
    pass


__all__ = [
    "PaymentGatewayError",
    "PaymentServiceError",
    "InvalidSignature",
    "PaymentNotFound",
    "AmountMismatch",
    "SESSIONABLE",
    "SETTLED",
    "_txn_ref",
    "_now_utc",
    "get_client_ip",
    "get_vnpay_return_url",
    "get_paypal_return_url",
    "get_paypal_cancel_url",
    "_vnpay_transaction_date",
]


class InvalidSignature(PaymentServiceError):
    pass


class PaymentNotFound(PaymentServiceError):
    pass


class AmountMismatch(PaymentServiceError):
    pass


SESSIONABLE = {"pending", "failed"}
SETTLED = {"paid", "refund_pending", "refunded"}


def _txn_ref(order_code: str, attempt: int) -> str:
    """Generate VNPay transaction reference."""
    stem = re.sub(r"[^0-9A-Za-z]", "", order_code).upper() or "FW"
    return f"{stem}{attempt:02d}"


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def get_client_ip(request) -> str:
    """Extract client IP from request."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "127.0.0.1")


def get_vnpay_return_url(request) -> str:
    """Build VNPay return URL from request."""
    return request.build_absolute_uri("/orders/payment/vnpay/return/")


def get_paypal_return_url(request) -> str:
    """Build PayPal return URL from request."""
    return request.build_absolute_uri("/orders/payment/paypal/return/")


def get_paypal_cancel_url(request) -> str:
    """Build PayPal cancel URL from request."""
    return request.build_absolute_uri("/orders/payment/paypal/cancel/")


def _vnpay_transaction_date(payment: Payment) -> datetime:
    """Extract transaction date from payment creation."""
    return payment.created_at.astimezone(GMT7) if payment.created_at else _now_utc().astimezone(GMT7)