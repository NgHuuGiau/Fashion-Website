"""GHTK (Giao Hang Tiet Kiem) API Client - minimal, cung interface nhu GHN."""
import logging
import time
from dataclasses import dataclass
from typing import Optional

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class GHTKConfig:
    token: str
    shop_id: str = ""
    base_url: str = "https://services.giaohangtietkiem.vn/services/shipment"
    timeout: int = 30
    max_retries: int = 3

    @classmethod
    def from_settings(cls) -> "GHTKConfig":
        return cls(
            token=getattr(settings, "GHTK_TOKEN", ""),
            shop_id=str(getattr(settings, "GHTK_SHOP_ID", "")),
            base_url=getattr(settings, "GHTK_ENDPOINT", "https://services.giaohangtietkiem.vn/services/shipment").rsplit("/order", 1)[0],
        )

    def is_configured(self) -> bool:
        return bool(self.token)


class GHTKAPIError(Exception):
    def __init__(self, message: str, response: dict = None):
        self.message = message
        self.response = response or {}
        super().__init__(message)


class GHTKClient:
    def __init__(self, config: GHTKConfig = None):
        self.config = config or GHTKConfig.from_settings()
        self.session = requests.Session()
        self.session.headers.update({"Token": self.config.token, "Content-Type": "application/json"})

    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        url = f"{self.config.base_url}{endpoint}"
        for attempt in range(self.config.max_retries):
            try:
                resp = self.session.request(method, url, timeout=self.config.timeout, **kwargs)
                data = resp.json() if resp.content else {}
                if resp.status_code == 200 and data.get("success"):
                    return data.get("order", data)
                raise GHTKAPIError(data.get("message", "Unknown error"), data)
            except requests.RequestException as e:
                if attempt == self.config.max_retries - 1:
                    raise GHTKAPIError(f"Network error: {e}")
                time.sleep(2 ** attempt)
        raise GHTKAPIError("Max retries exceeded")

    def create_order(self, order_data: dict) -> dict:
        res = self._request("POST", "/order", json={"order": order_data})
        # ponytail: chuan hoa ve dang GHN {order_code, tracking_code, total_fee, cod_amount}
        code = res.get("label", "") or res.get("tracking_id", "")
        return {"order_code": code, "tracking_code": code, "total_fee": res.get("fee", 0), "cod_amount": order_data.get("pick_money", 0), "raw": res}

    def get_order_detail(self, order_code: str) -> dict:
        return self._request("GET", f"/v2/{order_code}", params={})

    def cancel_order(self, order_code: str, cancel_reason: str = "") -> dict:
        return self._request("POST", f"/cancel/{order_code}", json={})


def get_ghtk_client() -> Optional[GHTKClient]:
    config = GHTKConfig.from_settings()
    if not config.is_configured():
        logger.warning("GHTK not configured: missing GHTK_TOKEN")
        return None
    return GHTKClient(config)


def build_ghtk_order_payload(order, carrier_config: dict) -> dict:
    items = order.items.all()
    products = [{"name": i.product_name or i.product.name, "quantity": i.quantity, "weight": 0.2} for i in items]
    return {
        "id": f"HG{order.id}",
        "pick_name": "HUUGIAU Atelier",
        "pick_address": getattr(settings, "STORE_ADDRESS", ""),
        "pick_tel": getattr(settings, "HOTLINE", ""),
        "name": order.customer_name,
        "address": order.shipping_address,
        "phone": order.phone,
        "note": order.note or "",
        "pick_money": int(order.total_amount) if order.payment_method == "cod" else 0,
        "value": int(order.total_amount),
        "transport": "road",
        "products": products,
    }
