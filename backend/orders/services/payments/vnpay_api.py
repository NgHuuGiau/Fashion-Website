"""
VNPAY Part 3: Query transaction and Refund
"""
import hashlib
import hmac
import secrets
from datetime import datetime
from typing import Dict, Any

import httpx
from django.conf import settings

from .base import GatewayOutcome
from .vnpay import (
    VNPAY_VERSION, _now_gmt7, _format_time, normalize_order_info,
    verify_callback, callback_params
)
from .vnpay_payment import build_payment_url, outcome_from_callback

def _request_id(prefix: str) -> str:
    return f"{prefix}{_now_gmt7().strftime('%H%M%S')}{secrets.token_hex(4)}"


def _querydr_signature(payload: Dict[str, str]) -> str:
    return "|".join(
        payload[key]
        for key in (
            "vnp_RequestId", "vnp_Version", "vnp_Command", "vnp_TmnCode",
            "vnp_TxnRef", "vnp_TransactionDate", "vnp_CreateDate",
            "vnp_IpAddr", "vnp_OrderInfo",
        )
    )


def _refund_signature(payload: Dict[str, str]) -> str:
    return "|".join(
        payload[key]
        for key in (
            "vnp_RequestId", "vnp_Version", "vnp_Command", "vnp_TmnCode",
            "vnp_TransactionType", "vnp_TxnRef", "vnp_Amount",
            "vnp_TransactionNo", "vnp_TransactionDate", "vnp_CreateBy",
            "vnp_CreateDate", "vnp_IpAddr", "vnp_OrderInfo",
        )
    )


def _signed_payload(payload: Dict[str, str], data: str, secret: str) -> Dict[str, str]:
    payload["vnp_SecureHash"] = hmac.new(
        secret.encode("utf-8"), data.encode("utf-8"), hashlib.sha512
    ).hexdigest()
    return payload


def _post(vnpay_api_url: str, payload: Dict[str, str]) -> Dict[str, Any]:
    """POST to VNPay API."""
    with httpx.Client(timeout=30.0) as client:
        response = client.post(vnpay_api_url, json=payload)
        response.raise_for_status()
        return response.json()


def query_transaction(
    *,
    txn_ref: str,
    transaction_date: datetime,
    ip_addr: str = "127.0.0.1",
) -> Dict[str, Any]:
    """Query transaction status from VNPay."""
    vnpay_tmn_code = getattr(settings, "VNPAY_TMN_CODE", "")
    vnpay_hash_secret = getattr(settings, "VNPAY_HASH_SECRET", "")
    vnpay_api_url = getattr(settings, "VNPAY_API_URL", "https://sandbox.vnpayment.vn/merchant_webapi/api/transaction")

    now = _now_gmt7()
    payload = {
        "vnp_RequestId": _request_id("QR"),
        "vnp_Version": VNPAY_VERSION,
        "vnp_Command": "querydr",
        "vnp_TmnCode": vnpay_tmn_code,
        "vnp_TxnRef": txn_ref,
        "vnp_TransactionDate": _format_time(transaction_date),
        "vnp_CreateDate": _format_time(now),
        "vnp_IpAddr": ip_addr,
        "vnp_OrderInfo": "Doi soat giao dich Fashion-Website",
    }
    data = _querydr_signature(payload)
    return _post(vnpay_api_url, _signed_payload(payload, data, vnpay_hash_secret))


def refund(
    *,
    txn_ref: str,
    amount_minor: int,
    transaction_no: str,
    transaction_date: datetime,
    ip_addr: str = "127.0.0.1",
    created_by: str = "Fashion-Website",
) -> GatewayOutcome:
    """Request refund from VNPay."""
    vnpay_tmn_code = getattr(settings, "VNPAY_TMN_CODE", "")
    vnpay_hash_secret = getattr(settings, "VNPAY_HASH_SECRET", "")
    vnpay_api_url = getattr(settings, "VNPAY_API_URL", "https://sandbox.vnpayment.vn/merchant_webapi/api/transaction")

    now = _now_gmt7()
    payload = {
        "vnp_RequestId": _request_id("RF"),
        "vnp_Version": VNPAY_VERSION,
        "vnp_Command": "refund",
        "vnp_TmnCode": vnpay_tmn_code,
        "vnp_TransactionType": "02",  # 02 = full refund, 03 = partial
        "vnp_TxnRef": txn_ref,
        "vnp_Amount": str(int(amount_minor)),
        "vnp_TransactionNo": transaction_no,
        "vnp_TransactionDate": _format_time(transaction_date),
        "vnp_CreateBy": created_by,
        "vnp_CreateDate": _format_time(now),
        "vnp_IpAddr": ip_addr,
        "vnp_OrderInfo": normalize_order_info(f"Hoan tien don {txn_ref}"),
    }
    data = _refund_signature(payload)
    result = _post(vnpay_api_url, _signed_payload(payload, data, vnpay_hash_secret))

    code = str(result.get("vnp_ResponseCode", ""))
    succeeded = code == "00"

    return GatewayOutcome(
        status="refunded" if succeeded else "failed",
        provider_status=code or None,
        provider_txn_id=str(result.get("vnp_TransactionNo") or transaction_no),
        amount_minor=amount_minor,
        currency="VND",
        raw=result,
    )


__all__ = [
    "build_payment_url",
    "outcome_from_callback",
    "verify_callback",
    "callback_params",
    "query_transaction",
    "refund",
    "normalize_order_info",
]