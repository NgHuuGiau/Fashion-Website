"""Tích hợp cổng thanh toán ZaloPay (API v2, HMAC-SHA256).

Cấu hình qua .env: ZALOPAY_APP_ID, ZALOPAY_KEY1, ZALOPAY_KEY2, ZALOPAY_ENDPOINT.
Sandbox mặc định; chỉ hoạt động khi đầy đủ credentials.
"""

import hashlib
import hmac
import json
import logging
import time
import uuid
from datetime import datetime

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

ZALOPAY_VERSION = "2.0"
ZALOPAY_LOCALE = "vn"
ZALOPAY_CURRENCY = "VND"


def is_configured():
    """Kiểm tra xem ZaloPay đã được cấu hình chưa."""
    return bool(
        settings.ZALOPAY_APP_ID
        and settings.ZALOPAY_KEY1
        and settings.ZALOPAY_KEY2
        and settings.ZALOPAY_ENDPOINT
    )


def _secure_hash(params: dict, key: str) -> str:
    """Tạo chữ ký HMAC-SHA256 theo chuẩn ZaloPay."""
    # ZaloPay yêu cầu các tham tố được sắp xếp theo alphabet
    raw_data = "&".join(f"{key}={params[key]}" for key in sorted(params))
    return hmac.new(
        key.encode("utf-8"),
        raw_data.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def build_payment_request(order, ip_addr, return_url, notify_url) -> dict:
    """
    Tạo request payload cho ZaloPay CreateOrder API.

    Returns:
        dict: {"order_url": "...", "order_token": "...", "app_trans_id": "...", ...}
    """
    if not is_configured():
        return {"order_url": "", "error": "ZaloPay chưa được cấu hình"}

    # ZaloPay yêu cầu app_trans_id format: YYMMDD_xxxx
    app_trans_id = f"{datetime.now().strftime('%y%m%d')}_{uuid.uuid4().hex[:8]}"

    params = {
        "app_id": int(settings.ZALOPAY_APP_ID),
        "app_user": f"user_{order.user_id if order.user_id else 'guest'}",
        "app_trans_id": app_trans_id,
        "app_time": int(time.time() * 1000),
        "amount": int(order.total_amount),
        "description": f"Thanh toan don hang {order.id}",
        "embed_data": json.dumps({"redirect_url": return_url}),
        "item": json.dumps([]),
        "bank_code": "",
        "callback_url": notify_url,
    }

    params["mac"] = _secure_hash(params, settings.ZALOPAY_KEY1)

    try:
        response = requests.post(
            settings.ZALOPAY_ENDPOINT,
            data=params,
            timeout=30,
        )
        response_data = response.json()

        if response_data.get("return_code") == 1:
            return {
                "order_url": response_data.get("order_url", ""),
                "order_token": response_data.get("order_token", ""),
                "app_trans_id": app_trans_id,
                "zp_trans_token": response_data.get("zp_trans_token", ""),
            }
        else:
            logger.error("ZaloPay create order failed: %s", response_data)
            return {"order_url": "", "error": response_data.get("return_message", "Unknown error")}

    except requests.RequestException:
        logger.exception("ZaloPay request failed for order %s", order.id)
        return {"order_url": "", "error": "Kết nối ZaloPay thất bại"}
    except Exception:
        logger.exception("ZaloPay response parse failed for order %s", order.id)
        return {"order_url": "", "error": "Phân tích phản hồi ZaloPay thất bại"}


def verify_callback(data: dict) -> bool:
    """Xác minh chữ ký callback/IPN từ ZaloPay (dùng key2)."""
    if not is_configured():
        return False

    received_mac = data.get("mac", "")
    if not received_mac:
        return False

    # Loại bỏ mac khỏi data trước khi verify
    verify_data = {k: v for k, v in data.items() if k != "mac"}
    expected = _secure_hash(verify_data, settings.ZALOPAY_KEY2)

    return hmac.compare_digest(received_mac, expected)


def amount_matches(order, data: dict) -> bool:
    """Đối chiếu số tiền callback với đơn hàng."""
    try:
        return int(data.get("amount", 0)) == int(order.total_amount)
    except (TypeError, ValueError):
        return False


def is_success_callback(data: dict) -> bool:
    """Kiểm tra callback có phải thanh toán thành công không."""
    return data.get("return_code") == 1


def get_transaction_info(data: dict) -> dict:
    """Trích xuất thông tin giao dịch từ callback."""
    return {
        "app_trans_id": data.get("app_trans_id"),
        "zp_trans_id": data.get("zp_trans_id"),
        "amount": int(data.get("amount", 0)),
        "description": data.get("description", ""),
        "bank_code": data.get("bank_code"),
        "card_type": data.get("card_type"),
        "payment_method": data.get("payment_method"),
        "merchant_user_id": data.get("merchant_user_id"),
    }


def query_transaction(order, app_trans_id: str) -> dict:
    """
    Truy vấn trạng thái giao dịch ZaloPay.
    """
    if not is_configured():
        return {"success": False, "message": "ZaloPay chưa được cấu hình"}

    params = {
        "app_id": int(settings.ZALOPAY_APP_ID),
        "app_trans_id": app_trans_id,
    }

    params["mac"] = _secure_hash(params, settings.ZALOPAY_KEY1)

    try:
        response = requests.post(
            settings.ZALOPAY_ENDPOINT.replace("/create", "/query"),
            data=params,
            timeout=30,
        )
        response_data = response.json()

        if response_data.get("return_code") == 1:
            return {"success": True, "data": response_data}
        else:
            return {"success": False, "message": response_data.get("return_message", "Query failed")}
    except Exception:
        logger.exception("ZaloPay query failed for order %s", order.id)
        return {"success": False, "ambiguous": True, "message": "Truy vấn ZaloPay thất bại"}


def refund_transaction(order, amount: int, zp_trans_id: str) -> dict:
    """
    Gọi API hoàn tiền ZaloPay.
    """
    if not is_configured():
        return {"success": False, "message": "ZaloPay chưa được cấu hình"}

    params = {
        "app_id": int(settings.ZALOPAY_APP_ID),
        "zp_trans_id": zp_trans_id,
        "amount": amount,
        "description": f"Hoan tien don hang {order.id}",
        "timestamp": int(time.time() * 1000),
    }

    params["mac"] = _secure_hash(params, settings.ZALOPAY_KEY1)

    try:
        response = requests.post(
            settings.ZALOPAY_ENDPOINT.replace("/create", "/refund"),
            data=params,
            timeout=30,
        )
        response_data = response.json()

        if response_data.get("return_code") == 1:
            return {"success": True, "data": response_data}
        else:
            return {"success": False, "message": response_data.get("return_message", "Refund failed")}
    except Exception:
        logger.exception("ZaloPay refund failed for order %s", order.id)
        return {"success": False, "ambiguous": True, "message": "Hoàn tiền ZaloPay thất bại"}