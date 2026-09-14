"""Tích hợp cổng thanh toán VNPay (chuẩn v2, HMAC-SHA512).

Cấu hình qua .env: VNPAY_URL, VNPAY_REFUND_URL, VNPAY_TMN_CODE, VNPAY_HASH_SECRET.
Sandbox mặc định; chỉ hoạt động khi VNPAY_TMN_CODE + VNPAY_HASH_SECRET được điền.
"""

import hashlib
import hmac
import logging
import requests
from datetime import datetime
from urllib.parse import urlencode

from django.conf import settings
from django.utils import timezone

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


def amount_matches(order, params: dict) -> bool:
    """Đối chiếu vnp_Amount (đơn vị xu = VND*100) với tổng tiền đơn hàng."""
    try:
        return int(params.get("vnp_Amount", 0)) == int(order.total_amount) * 100
    except (TypeError, ValueError):
        return False


def refund_transaction(order, amount: int, trans_id: str, user: str = "admin") -> dict:
    """
    Gọi API hoàn tiền VNPay.

    Args:
        order: Order object
        amount: Số tiền hoàn (VND)
        trans_id: Transaction ID từ VNPay (vnp_TransactionNo)
        user: Tên người thực hiện hoàn tiền

    Returns:
        dict: Kết quả từ VNPay API
    """
    if not is_configured():
        return {"success": False, "message": "VNPay chưa được cấu hình"}
    if not settings.VNPAY_REFUND_URL:
        return {"success": False, "message": "Chưa cấu hình endpoint hoàn tiền VNPay"}

    # VNPay Refund API parameters

    params = {
        "vnp_Version": VNPAY_VERSION,
        "vnp_Command": "refund",
        "vnp_TmnCode": settings.VNPAY_TMN_CODE,
        "vnp_RequestId": datetime.now().strftime("%Y%m%d%H%M%S"),
        "vnp_Amount": str(amount * 100),  # VNPay uses VND * 100
        "vnp_OrderInfo": f"Hoan tien don hang {order.id}",
        "vnp_CreateDate": timezone.now().strftime("%Y%m%d%H%M%S"),
        "vnp_CurrCode": VNPAY_CURRENCY,
        "vnp_IpAddr": "127.0.0.1",
        "vnp_TxnRef": str(order.id),
        "vnp_TransactionType": "02",  # 02: Partial refund
        "vnp_TransactionNo": trans_id,
        "vnp_Locale": "vn",
    }

    params["vnp_SecureHash"] = _secure_hash(params)

    try:
        response = requests.post(settings.VNPAY_REFUND_URL, data=params, timeout=30)
        response_data = response.json()

        # Verify response signature
        if "vnp_SecureHash" in response_data:
            received_hash = response_data.pop("vnp_SecureHash", "")
            expected_hash = _secure_hash(response_data)
            if not hmac.compare_digest(received_hash, expected_hash):
                return {"success": False, "message": "Invalid response signature"}

        return {
            "success": response_data.get("vnp_ResponseCode") == "00",
            "response_code": response_data.get("vnp_ResponseCode"),
            "message": response_data.get("vnp_Message"),
            "data": response_data,
        }
    except requests.RequestException as e:
        logger.error(f"VNPay refund request failed: {e}")
        return {"success": False, "message": f"Request failed: {str(e)}"}
    except Exception as e:
        logger.error(f"VNPay refund error: {e}")
        return {"success": False, "message": f"Error: {str(e)}"}
