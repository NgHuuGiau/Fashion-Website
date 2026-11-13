"""
VNPAY Part 2: Payment URL building and callback parsing
"""
import hashlib
import hmac
from datetime import timedelta
from typing import Dict, Optional

from django.conf import settings

from .base import GatewayOutcome, PaymentGatewayError
from .vnpay import (
    VNPAY_VERSION, _now_gmt7, _format_time, normalize_order_info,
    hash_data
)


def build_payment_url(
    *,
    txn_ref: str,
    amount_vnd: int,
    order_info: str,
    ip_addr: str,
    return_url: Optional[str] = None,
) -> str:
    """Build VNPay payment URL."""
    if amount_vnd <= 0:
        raise PaymentGatewayError("Số tiền thanh toán không hợp lệ")

    vnpay_pay_url = getattr(settings, "VNPAY_URL", "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html")
    vnpay_tmn_code = getattr(settings, "VNPAY_TMN_CODE", "")
    vnpay_hash_secret = getattr(settings, "VNPAY_HASH_SECRET", "")
    vnpay_return_url = getattr(settings, "VNPAY_RETURN_URL", return_url or "")
    vnpay_expire_minutes = getattr(settings, "VNPAY_EXPIRE_MINUTES", 15)

    created = _now_gmt7()
    params = {
        "vnp_Version": VNPAY_VERSION,
        "vnp_Command": "pay",
        "vnp_TmnCode": vnpay_tmn_code,
        "vnp_Amount": str(int(amount_vnd) * 100),
        "vnp_CurrCode": "VND",
        "vnp_TxnRef": txn_ref,
        "vnp_OrderInfo": normalize_order_info(order_info),
        "vnp_OrderType": "other",
        "vnp_Locale": "vn",
        "vnp_IpAddr": ip_addr or "127.0.0.1",
        "vnp_CreateDate": _format_time(created),
        "vnp_ExpireDate": _format_time(created + timedelta(minutes=vnpay_expire_minutes)),
        "vnp_ReturnUrl": vnpay_return_url,
    }

    secret = vnpay_hash_secret
    data = hash_data(params)
    signature = hmac.new(
        secret.encode("utf-8"), data.encode("utf-8"), hashlib.sha512
    ).hexdigest()

    return f"{vnpay_pay_url}?{data}&vnp_SecureHash={signature}"


def outcome_from_callback(params: Dict[str, str]) -> GatewayOutcome:
    """Parse VNPay callback into GatewayOutcome."""
    response_code = params.get("vnp_ResponseCode", "")
    transaction_status = params.get("vnp_TransactionStatus", "")
    paid = response_code == "00" and transaction_status == "00"

    amount_minor = None
    if "vnp_Amount" in params:
        try:
            amount_minor = int(params["vnp_Amount"]) // 100
        except (ValueError, TypeError):
            pass

    return GatewayOutcome(
        status="paid" if paid else "failed",
        provider_status=response_code or None,
        provider_txn_id=params.get("vnp_TransactionNo") or None,
        amount_minor=amount_minor,
        currency="VND",
        raw=params,
    )