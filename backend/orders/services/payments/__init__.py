"""
Payment services package for Fashion-Website
"""

from .base import GatewayOutcome, PaymentGatewayError
from .paypal import paypal_service, PayPalService
from .vnpay import (
    verify_callback,
    callback_params,
    normalize_order_info,
)
from .vnpay_payment import (
    build_payment_url,
    outcome_from_callback,
)
from .vnpay_api import (
    query_transaction,
    refund,
)

# Re-export gateway modules for convenience
from . import paypal
from . import vnpay
from . import vnpay_payment
from . import vnpay_api

# Re-export service functions from parent directory
from ..payment_session import create_payment_session
from ..payment_callback import handle_vnpay_callback, handle_paypal_callback
from ..payment_refund import request_refund, _run_gateway_refund
from ..payment_refund_confirm import confirm_refund, reject_refund

__all__ = [
    # Base
    "GatewayOutcome",
    "PaymentGatewayError",
    # PayPal
    "paypal_service",
    "PayPalService",
    # VNPay
    "build_payment_url",
    "outcome_from_callback",
    "verify_callback",
    "callback_params",
    "query_transaction",
    "refund",
    "normalize_order_info",
    # Service functions
    "create_payment_session",
    "handle_vnpay_callback",
    "handle_paypal_callback",
    "request_refund",
    "_run_gateway_refund",
    "confirm_refund",
    "reject_refund",
    # Submodules
    "paypal",
    "vnpay",
    "vnpay_payment",
    "vnpay_api",
]
