"""
VNPAY sandbox/production adapter: URL signing, callback verification, query, refund
Ported from ElectroHub - adapted for Django/Fashion-Website
Part 1: Core utilities and payment URL building
"""
import hashlib
import hmac
import re
import unicodedata
from datetime import datetime, timedelta, timezone
from urllib.parse import quote_plus
from typing import Dict



VNPAY_VERSION = "2.1.0"
GMT7 = timezone(timedelta(hours=7))
_SAFE_TEXT = re.compile(r"[^A-Za-z0-9 ]+")


def _now_gmt7() -> datetime:
    return datetime.now(GMT7)


def _format_time(value: datetime) -> str:
    return value.astimezone(GMT7).strftime("%Y%m%d%H%M%S")


def normalize_order_info(value: str, limit: int = 255) -> str:
    """VNPAY rejects accented/special characters in vnp_OrderInfo."""
    ascii_text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    cleaned = re.sub(r"\s+", " ", _SAFE_TEXT.sub("", ascii_text)).strip()
    return (cleaned or "Thanh toan don hang Fashion-Website")[:limit]


def hash_data(params: Dict[str, str]) -> str:
    items = sorted((key, value) for key, value in params.items() if value not in (None, ""))
    return "&".join(f"{quote_plus(key)}={quote_plus(str(value))}" for key, value in items)


def sign_params(params: Dict[str, str], secret: str) -> str:
    return hmac.new(
        secret.encode("utf-8"), hash_data(params).encode("utf-8"), hashlib.sha512
    ).hexdigest()


def verify_callback(params: Dict[str, str], secret: str) -> bool:
    """Verify VNPay callback signature."""
    received = params.get("vnp_SecureHash", "")
    unsigned = {
        key: value
        for key, value in params.items()
        if key not in {"vnp_SecureHash", "vnp_SecureHashType"}
    }
    return bool(received) and hmac.compare_digest(received.lower(), sign_params(unsigned, secret))


def callback_params(params: Dict[str, str]) -> Dict[str, str]:
    """Extract only vnp_ params from callback."""
    return {key: value for key, value in params.items() if key.startswith("vnp_")}