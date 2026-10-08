"""J&T Express API Client - minimal, cung interface nhu GHN/GHTK."""
import logging
import time
from dataclasses import dataclass
from typing import Optional

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class JNTConfig:
    client_id: str
    client_secret: str
    base_url: str = "https://api.jtexpress.vn/v2"
    timeout: int = 30
    max_retries: int = 3

    @classmethod
    def from_settings(cls) -> "JNTConfig":
        return cls(
            client_id=getattr(settings, "JNT_CLIENT_ID", ""),
            client_secret=getattr(settings, "JNT_CLIENT_SECRET", ""),
            base_url=getattr(settings, "JNT_ENDPOINT", "https://api.jtexpress.vn/v2"),
        )

    def is_configured(self) -> bool:
        return bool(self.client_id and self.client_secret)


class JNTAPIError(Exception):
    def __init__(self, message: str, response: dict = None):
        self.message = message
        self.response = response or {}
        super().__init__(message)


class JNTClient:
    def __init__(self, config: JNTConfig = None):
        self.config = config or JNTConfig.from_settings()
        self.session = requests.Session()
        self._access_token = None
        self._token_expires = 0

    def _get_token(self) -> str:
        if self._access_token and time.time() < self._token_expires - 60:
            return self._access_token
        resp = self.session.post(
            f"{self.config.base_url}/auth/token",
            json={"client_id": self.config.client_id, "client_secret": self.config.client_secret},
            timeout=10,
        )
        data = resp.json()
        self._access_token = data.get("access_token", "")
        self._token_expires = time.time() + data.get("expires_in", 3600)
        return self._access_token

    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        token = self._get_token()
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        url = f"{self.config.base_url}{endpoint}"
        for attempt in range(self.config.max_retries):
            try:
                resp = self.session.request(method, url, headers=headers, timeout=self.config.timeout, **kwargs)
                data = resp.json() if resp.content else {}
                if resp.status_code == 200 and data.get("code") == 200:
                    return data.get("data", data)
                raise JNTAPIError(data.get("message", "Unknown error"), data)
            except requests.RequestException as e:
                if attempt == self.config.max_retries - 1:
                    raise JNTAPIError(f"Network error: {e}")
                time.sleep(2 ** attempt)
        raise JNTAPIError("Max retries exceeded")

    def create_order(self, order_data: dict) -> dict:
        res = self._request("POST", "/order/create", json=order_data)
        code = res.get("bill_code", "") or res.get("order_code", "")
        return {"order_code": code, "tracking_code": code, "total_fee": res.get("total_price", 0), "cod_amount": order_data.get("cod_amount", 0), "raw": res}

    def get_order_detail(self, bill_code: str) -> dict:
        return self._request("GET", "/order/detail", params={"bill_code": bill_code})

    def cancel_order(self, bill_code: str, cancel_reason: str = "") -> dict:
        return self._request("POST", "/order/cancel", json={"bill_code": bill_code, "reason": cancel_reason})


def get_jnt_client() -> Optional[JNTClient]:
    config = JNTConfig.from_settings()
    if not config.is_configured():
        logger.warning("J&T not configured: missing JNT_CLIENT_ID/SECRET")
        return None
    return JNTClient(config)


def build_jnt_order_payload(order, carrier_config: dict) -> dict:
    items = order.items.all()
    products = [{"name": i.product_name or i.product.name, "quantity": i.quantity, "weight": getattr(i.variant, "weight", 200)} for i in items]
    return {
        "bill_code": f"HG{order.id}",
        "sender_name": "HUUGIAU Atelier",
        "sender_phone": getattr(settings, "HOTLINE", ""),
        "sender_address": getattr(settings, "STORE_ADDRESS", ""),
        "receiver_name": order.customer_name,
        "receiver_phone": order.phone,
        "receiver_address": order.shipping_address,
        "cod_amount": int(order.total_amount) if order.payment_method == "cod" else 0,
        "service_type": "J&T Express",
        "items": products,
        "note": order.note or "",
    }