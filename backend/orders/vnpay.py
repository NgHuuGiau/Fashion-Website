"""Tích hợp cổng thanh toán VNPay (chuẩn v2, HMAC-SHA512).

Cấu hình qua .env: VNPAY_URL, VNPAY_TMN_CODE, VNPAY_HASH_SECRET.
Sandbox mặc định; chỉ hoạt động khi VNPAY_TMN_CODE + VNPAY_HASH_SECRET được điền.
"""

import hashlib
import hmac
import logging
from urllib.parse import urlencode

from django.conf import settings

logger = logging.getLogger(__name__)

VNPAY_VERSION = "2.1.0"
VNPAY_COMMAND = "pay"
VNPAY_ORDER_TYPE = "other"
VNPAY_CURRENCY = "VND"


def is_configured():
    return bool(
        settings.VNPAY_TMN_CODE and settings.VNPAY_HASH_SECRET and settings.VNPAY_URL
    )


def _secure_hash(params: dict) -> str:
    """Tạo chữ ký khóa bí mật theo chuẩn VNPay: nối value theo thứ tự key."""
    data = "&".join(f"{key}={params[key]}" for key in sorted(params))
    return hmac.new(
        settings.VNPAY_HASH_SECRET.encode("utf-8"),
        data.encode("utf-8"),
        hashlib.sha512,
    ).hexdigest()


def build_payment_url(order, ip_addr, return_url) -> str:
    """Tạo URL chuyển hướng tới cổng thanh toán VNPay."""
    if not is_configured():
        return ""
    created = order.created_at.strftime("%Y%m%d%H%M%S")
    params = {
        "vnp_Version": VNPAY_VERSION,
        "vnp_Command": VNPAY_COMMAND,
        "vnp_TmnCode": settings.VNPAY_TMN_CODE,
        "vnp_Amount": str(int(order.total_amount) * 100),
        "vnp_OrderType": VNPAY_ORDER_TYPE,
        "vnp_OrderInfo": f"Thanh toan don hang {order.id}",
        "vnp_CreateDate": created,
        "vnp_CurrCode": VNPAY_CURRENCY,
        "vnp_IpAddr": ip_addr,
        "vnp_ReturnUrl": return_url,
        "vnp_TxnRef": str(order.id),
        "vnp_Locale": "vn",
    }
    params["vnp_SecureHash"] = _secure_hash(params)
    return f"{settings.VNPAY_URL}?{urlencode(params)}"


def verify_return(params: dict) -> bool:
    """Xác minh chữ ký do VNPay gửi về (loại bỏ vnp_SecureHash trước khi verify)."""
    if not is_configured():
        return False
    received = params.get("vnp_SecureHash", "")
    if not received:
        return False
    data = {
        key: value
        for key, value in params.items()
        if key not in ("vnp_SecureHash", "vnp_SecureHashType")
    }
    expected = _secure_hash(data)
    return hmac.compare_digest(received, expected)
