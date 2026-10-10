"""Tích hợp cổng thanh toán MoMo (API v2, HMAC-SHA256).

Cấu hình qua .env: MOMO_PARTNER_CODE, MOMO_ACCESS_KEY, MOMO_SECRET_KEY, MOMO_ENDPOINT.
Sandbox mặc định; chỉ hoạt động khi đầy đủ credentials.
"""

import hashlib
import hmac
import logging
import uuid
from datetime import datetime

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

MOMO_VERSION = "2.0"
MOMO_PAYMENT_METHOD = "captureWallet"
MOMO_LOCALE = "vn"
MOMO_CURRENCY = "VND"


def is_configured():
    """Kiểm tra xem MoMo đã được cấu hình chưa."""
    return bool(
        settings.MOMO_PARTNER_CODE
        and settings.MOMO_ACCESS_KEY
        and settings.MOMO_SECRET_KEY
        and settings.MOMO_ENDPOINT
    )


def _secure_hash(params: dict, fields: tuple[str, ...]) -> str:
    """Tạo chữ ký HMAC-SHA256 theo chuẩn MoMo."""
    raw_data = "&".join(
        [f"accessKey={settings.MOMO_ACCESS_KEY}"]
        + [f"{field}={params.get(field, '')}" for field in fields]
    )
    return hmac.new(
        settings.MOMO_SECRET_KEY.encode("utf-8"),
        raw_data.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def build_payment_request(order, ip_addr, return_url, notify_url) -> dict:
    """
    Tạo request payload cho MoMo CreateOrder API.

    Returns:
        dict: {"payUrl": "...", "orderId": "...", "requestId": "...", "signature": "..."}
    """
    if not is_configured():
        return {"payUrl": "", "error": "MoMo chưa được cấu hình"}

    request_id = str(uuid.uuid4())
    order_id = f"{order.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    params = {
        "partnerCode": settings.MOMO_PARTNER_CODE,
        "partnerName": "HUUGIAU Studio",
        "storeId": settings.MOMO_PARTNER_CODE,
        "requestId": request_id,
        "orderId": order_id,
        "amount": str(int(order.total_amount)),
        "orderInfo": f"Thanh toan don hang {order.id}",
        "orderType": "momo_wallet",
        "redirectUrl": return_url,
        "ipnUrl": notify_url,
        "lang": MOMO_LOCALE,
        "extraData": "",
        "requestType": "captureWallet",
    }

    params["signature"] = _secure_hash(
        params,
        (
            "amount",
            "extraData",
            "ipnUrl",
            "orderId",
            "orderInfo",
            "partnerCode",
            "redirectUrl",
            "requestId",
            "requestType",
        ),
    )

    try:
        response = requests.post(
            settings.MOMO_ENDPOINT,
            json=params,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        response_data = response.json()

        if response_data.get("resultCode") == 0:
            return {
                "payUrl": response_data.get("payUrl", ""),
                "orderId": order_id,
                "requestId": request_id,
                "signature": response_data.get("signature", ""),
                "deeplink": response_data.get("deeplink", ""),
                "qrCodeUrl": response_data.get("qrCodeUrl", ""),
            }
        else:
            logger.error("MoMo create order failed: %s", response_data)
            return {
                "payUrl": "",
                "error": response_data.get("message", "Unknown error"),
            }

    except requests.RequestException:
        logger.exception("MoMo request failed for order %s", order.id)
        return {"payUrl": "", "error": "Kết nối MoMo thất bại"}
    except Exception:
        logger.exception("MoMo response parse failed for order %s", order.id)
        return {"payUrl": "", "error": "Phân tích phản hồi MoMo thất bại"}


def verify_callback(data: dict) -> bool:
    """Xác minh chữ ký callback/IPN từ MoMo."""
    if not is_configured():
        return False

    received_signature = data.get("signature", "")
    if not received_signature:
        return False

    # Loại bỏ signature khỏi data trước khi verify
    fields = (
        "amount",
        "extraData",
        "message",
        "orderId",
        "orderInfo",
        "orderType",
        "partnerCode",
        "payType",
        "requestId",
        "responseTime",
        "resultCode",
        "transId",
    )
    if any(field not in data for field in fields):
        return False
    expected = _secure_hash(data, fields)

    return hmac.compare_digest(received_signature, expected)


def amount_matches(order, data: dict) -> bool:
    """Đối chiếu số tiền callback với đơn hàng."""
    try:
        return int(data.get("amount", 0)) == int(order.total_amount)
    except (TypeError, ValueError):
        return False


def is_success_callback(data: dict) -> bool:
    """Kiểm tra callback có phải thanh toán thành công không."""
    return str(data.get("resultCode")) == "0"


def get_transaction_info(data: dict) -> dict:
    """Trích xuất thông tin giao dịch từ callback."""
    return {
        "transaction_id": data.get("transId"),
        "order_id": data.get("orderId"),
        "request_id": data.get("requestId"),
        "amount": int(data.get("amount", 0)),
        "message": data.get("message", ""),
        "pay_type": data.get("payType"),
        "response_time": data.get("responseTime"),
    }


def refund_transaction(order, amount: int, trans_id: str) -> dict:
    """
    Gọi API hoàn tiền MoMo.
    """
    if not is_configured():
        return {"success": False, "message": "MoMo chưa được cấu hình"}

    request_id = str(uuid.uuid4())
    order_id = f"refund_{order.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    params = {
        "partnerCode": settings.MOMO_PARTNER_CODE,
        "requestId": request_id,
        "orderId": order_id,
        "amount": str(amount),
        "orderInfo": f"Hoan tien don hang {order.id}",
        "transId": trans_id,
        "description": "",
        "lang": MOMO_LOCALE,
    }

    params["signature"] = _secure_hash(
        params,
        ("amount", "description", "orderId", "partnerCode", "requestId", "transId"),
    )

    try:
        response = requests.post(
            settings.MOMO_ENDPOINT.replace(
                "/v2/gateway/api/create", "/v2/gateway/api/refund"
            ),
            json=params,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        response_data = response.json()

        if response_data.get("resultCode") == 0:
            return {"success": True, "data": response_data}
        else:
            return {
                "success": False,
                "message": response_data.get("message", "Refund failed"),
                "data": response_data,
            }
    except requests.RequestException:
        logger.exception("MoMo refund request failed for order %s", order.id)
        return {"success": False, "ambiguous": True, "message": "Kết nối MoMo thất bại"}
    except Exception:
        logger.exception("MoMo refund response parse failed for order %s", order.id)
        return {
            "success": False,
            "ambiguous": True,
            "message": "Phân tích phản hồi MoMo thất bại",
        }


def query_transaction(order, trans_id: str) -> dict:
    """
    Truy vấn trạng thái giao dịch MoMo.
    """
    if not is_configured():
        return {"success": False, "message": "MoMo chưa được cấu hình"}

    request_id = str(uuid.uuid4())
    order_id = order.gateway_transaction_id or trans_id

    params = {
        "partnerCode": settings.MOMO_PARTNER_CODE,
        "requestId": request_id,
        "orderId": order_id,
        "lang": MOMO_LOCALE,
    }

    params["signature"] = _secure_hash(params, ("orderId", "partnerCode", "requestId"))

    try:
        response = requests.post(
            settings.MOMO_ENDPOINT.replace(
                "/v2/gateway/api/create", "/v2/gateway/api/query"
            ),
            json=params,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        response_data = response.json()

        if response_data.get("resultCode") == 0:
            return {"success": True, "data": response_data}
        else:
            return {
                "success": False,
                "message": response_data.get("message", "Query failed"),
            }
    except Exception:
        logger.exception("MoMo query failed for order %s", order.id)
        return {
            "success": False,
            "ambiguous": True,
            "message": "Truy vấn MoMo thất bại",
        }
