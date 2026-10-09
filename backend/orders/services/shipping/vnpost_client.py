"""VNPost API Client - minimal, cung interface nhu GHN/GHTK."""

import logging
import time
from dataclasses import dataclass
from typing import Optional

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class VNPostConfig:
    token: str
    shop_id: str = ""
    base_url: str = "https://partner.vnpost.vn/api/v2"
    timeout: int = 30
    max_retries: int = 3

    @classmethod
    def from_settings(cls) -> "VNPostConfig":
        return cls(
            token=getattr(settings, "VNPOST_TOKEN", ""),
            shop_id=str(getattr(settings, "VNPOST_SHOP_ID", "")),
            base_url=getattr(
                settings, "VNPOST_ENDPOINT", "https://partner.vnpost.vn/api/v2"
            ).rsplit("/createOrder", 1)[0],
        )

    def is_configured(self) -> bool:
        return bool(self.token)


class VNPostAPIError(Exception):
    def __init__(self, message: str, response: dict = None):
        self.message = message
        self.response = response or {}
        super().__init__(message)


class VNPostClient:
    def __init__(self, config: VNPostConfig = None):
        self.config = config or VNPostConfig.from_settings()
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.config.token}",
                "Content-Type": "application/json",
            }
        )

    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        url = f"{self.config.base_url}{endpoint}"
        for attempt in range(self.config.max_retries):
            try:
                resp = self.session.request(
                    method, url, timeout=self.config.timeout, **kwargs
                )
                data = resp.json() if resp.content else {}
                if resp.status_code == 200 and data.get("success"):
                    return data.get("data", data)
                raise VNPostAPIError(data.get("message", "Unknown error"), data)
            except requests.RequestException as e:
                if attempt == self.config.max_retries - 1:
                    raise VNPostAPIError(f"Network error: {e}")
                time.sleep(2**attempt)
        raise VNPostAPIError("Max retries exceeded")

    def create_order(self, order_data: dict) -> dict:
        res = self._request("POST", "/order/create", json={"order": order_data})
        code = (
            res.get("order_code", "")
            or res.get("tracking_code", "")
            or res.get("code", "")
        )
        return {
            "order_code": code,
            "tracking_code": code,
            "total_fee": res.get("fee", 0),
            "cod_amount": order_data.get("cod_amount", 0),
            "raw": res,
        }

    def get_order_detail(self, order_code: str) -> dict:
        return self._request("GET", "/order/detail", params={"order_code": order_code})

    def cancel_order(self, order_code: str, cancel_reason: str = "") -> dict:
        return self._request(
            "POST",
            "/order/cancel",
            json={"order_code": order_code, "reason": cancel_reason},
        )


def get_vnpost_client() -> Optional[VNPostClient]:
    config = VNPostConfig.from_settings()
    if not config.is_configured():
        logger.warning("VNPost not configured: missing VNPOST_TOKEN")
        return None
    return VNPostClient(config)


def build_vnpost_order_payload(order, carrier_config: dict) -> dict:
    items = order.items.all()
    products = [
        {
            "name": i.product_name or i.product.name,
            "quantity": i.quantity,
            "weight": getattr(i.variant, "weight", 200) / 1000,
        }
        for i in items
    ]
    return {
        "order_code": f"HG{order.id}",
        "sender_name": "HUUGIAU Atelier",
        "sender_phone": getattr(settings, "HOTLINE", ""),
        "sender_address": getattr(settings, "STORE_ADDRESS", ""),
        "receiver_name": order.customer_name,
        "receiver_phone": order.phone,
        "receiver_address": order.shipping_address,
        "cod_amount": int(order.total_amount) if order.payment_method == "cod" else 0,
        "service_type": "EMS" if order.payment_method == "cod" else "FAST",
        "items": products,
        "note": order.note or "",
    }
