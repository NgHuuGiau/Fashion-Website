"""Tích hợp cổng thanh toán ShopeePay (API v2, HMAC-SHA256).

Cấu hình qua .env: SHOPEEPAY_PARTNER_ID, SHOPEEPAY_KEY, SHOPEEPAY_SECRET, SHOPEEPAY_ENDPOINT.
Sandbox mặc định; chỉ hoạt động khi đầy đủ credentials.
"""

import hashlib
import hmac
import logging
import time
from datetime import datetime

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

SHOPEEPAY_VERSION = "2.0"
SHOPEEPAY_LOCALE = "vn"
SHOPEEPAY_CURRENCY = "VND"


def is_configured():
    """Kiểm tra xem ShopeePay đã được cấu hình chưa."""
    return bool(
        settings.SHOPEEPAY_PARTNER_ID
        and settings.SHOPEEPAY_KEY
        and settings.SHOPEEPAY_SECRET
        and settings.SHOPEEPAY_ENDPOINT
    )


def _secure_hash(params: dict) -> str:
    """Tạo chữ ký HMAC-SHA256 theo chuẩn ShopeePay."""
    # ShopeePay yêu cầu các tham tố được sắp xếp theo alphabet
    raw_data = "&".join(f"{key}={params[key]}" for key in sorted(params))
    return hmac.new(
        settings.SHOPEEPAY_SECRET.encode("utf-8"),
        raw_data.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def build_payment_request(order, ip_addr, return_url, notify_url) -> dict:
    """
    Tạo request payload cho ShopeePay CreateOrder API.

    Returns:
        dict: {"checkout_url": "...", "order_id": "...", "token": "...", ...}
    """
    if not is_configured():
        return {"checkout_url": "", "error": "ShopeePay chưa được cấu hình"}

    order_id = f"SP{order.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    partner_id = int(settings.SHOPEEPAY_PARTNER_ID)

    params = {
        "partner_id": partner_id,
        "order_id": order_id,
        "amount": int(order.total_amount),
        "currency": SHOPEEPAY_CURRENCY,
        "description": f"Thanh toan don hang {order.id}",
        "return_url": return_url,
        "notify_url": notify_url,
        "timestamp": int(time.time()),
    }

    params["sign"] = _secure_hash(params)

    try:
        response = requests.post(
            f"{settings.SHOPEEPAY_ENDPOINT}/api/v2/payment/order/create",
            json=params,
            headers={
                "Content-Type": "application/json",
                "Partner-Key": settings.SHOPEEPAY_KEY,
            },
            timeout=30,
        )
        response_data = response.json()

        if response_data.get("error_code") == 0:
            data = response_data.get("data", {})
            return {
                "checkout_url": data.get("checkout_url", ""),
                "order_id": order_id,
                "token": data.get("token", ""),
                "expire_time": data.get("expire_time", 0),
            }
        else:
            logger.error("ShopeePay create order failed: %s", response_data)
            return {
                "checkout_url": "",
                "error": response_data.get("error_message", "Unknown error"),
            }

    except requests.RequestException:
        logger.exception("ShopeePay request failed for order %s", order.id)
        return {"checkout_url": "", "error": "Kết nối ShopeePay thất bại"}
    except Exception:
        logger.exception("ShopeePay response parse failed for order %s", order.id)
        return {"checkout_url": "", "error": "Phân tích phản hồi ShopeePay thất bại"}


def verify_callback(data: dict) -> bool:
    """Xác minh chữ ký callback/IPN từ ShopeePay."""
    if not is_configured():
        return False

    received_sign = data.get("sign", "")
    if not received_sign:
        return False

    # Loại bỏ sign khỏi data trước khi verify
    verify_data = {k: v for k, v in data.items() if k != "sign"}
    expected = _secure_hash(verify_data)

    return hmac.compare_digest(received_sign, expected)


def amount_matches(order, data: dict) -> bool:
    """Đối chiếu số tiền callback với đơn hàng."""
    try:
        return int(data.get("amount", 0)) == int(order.total_amount)
    except (TypeError, ValueError):
        return False


def is_success_callback(data: dict) -> bool:
    """Kiểm tra callback có phải thanh toán thành công không."""
    return data.get("status") == "SUCCESS"


def get_transaction_info(data: dict) -> dict:
    """Trích xuất thông tin giao dịch từ callback."""
    return {
        "partner_order_id": data.get("partner_order_id"),
        "order_id": data.get("order_id"),
        "amount": int(data.get("amount", 0)),
        "currency": data.get("currency", "VND"),
        "status": data.get("status", ""),
        "payment_method": data.get("payment_method", ""),
        "transaction_time": data.get("transaction_time", 0),
    }


def query_transaction(order, partner_order_id: str) -> dict:
    """
    Truy vấn trạng thái giao dịch ShopeePay.
    """
    if not is_configured():
        return {"success": False, "message": "ShopeePay chưa được cấu hình"}

    params = {
        "partner_id": int(settings.SHOPEEPAY_PARTNER_ID),
        "partner_order_id": partner_order_id,
        "timestamp": int(time.time()),
    }

    params["sign"] = _secure_hash(params)

    try:
        response = requests.post(
            f"{settings.SHOPEEPAY_ENDPOINT}/api/v2/payment/order/query",
            json=params,
            headers={
                "Content-Type": "application/json",
                "Partner-Key": settings.SHOPEEPAY_KEY,
            },
            timeout=30,
        )
        response_data = response.json()

        if response_data.get("error_code") == 0:
            return {"success": True, "data": response_data.get("data", {})}
        else:
            return {
                "success": False,
                "message": response_data.get("error_message", "Query failed"),
            }
    except Exception:
        logger.exception("ShopeePay query failed for order %s", order.id)
        return {
            "success": False,
            "ambiguous": True,
            "message": "Truy vấn ShopeePay thất bại",
        }


def refund_transaction(order, amount: int, order_id: str) -> dict:
    """
    Gọi API hoàn tiền ShopeePay.
    """
    if not is_configured():
        return {"success": False, "message": "ShopeePay chưa được cấu hình"}

    params = {
        "partner_id": int(settings.SHOPEEPAY_PARTNER_ID),
        "order_id": order_id,
        "amount": amount,
        "currency": SHOPEEPAY_CURRENCY,
        "description": f"Hoan tien don hang {order.id}",
        "timestamp": int(time.time()),
    }

    params["sign"] = _secure_hash(params)

    try:
        response = requests.post(
            f"{settings.SHOPEEPAY_ENDPOINT}/api/v2/payment/order/refund",
            json=params,
            headers={
                "Content-Type": "application/json",
                "Partner-Key": settings.SHOPEEPAY_KEY,
            },
            timeout=30,
        )
        response_data = response.json()

        if response_data.get("error_code") == 0:
            return {"success": True, "data": response_data.get("data", {})}
        else:
            return {
                "success": False,
                "message": response_data.get("error_message", "Refund failed"),
            }
    except Exception:
        logger.exception("ShopeePay refund failed for order %s", order.id)
        return {
            "success": False,
            "ambiguous": True,
            "message": "Hoàn tiền ShopeePay thất bại",
        }
