"""ViettelPost API Client - minimal, cung interface nhu GHN/GHTK."""
import logging
import time
from dataclasses import dataclass
from typing import Optional

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class ViettelPostConfig:
    token: str
    shop_id: str = ""
    base_url: str = "https://partner.viettelpost.vn/v2/order"
    timeout: int = 30
    max_retries: int = 3

    @classmethod
    def from_settings(cls) -> "ViettelPostConfig":
        return cls(
            token=getattr(settings, "VIETTELPOST_TOKEN", ""),
            shop_id=str(getattr(settings, "VIETTELPOST_SHOP_ID", "")),
            base_url=getattr(settings, "VIETTELPOST_ENDPOINT", "https://partner.viettelpost.vn/v2/order/createOrder").rsplit("/createOrder", 1)[0],
        )

    def is_configured(self) -> bool:
        return bool(self.token)


class ViettelPostAPIError(Exception):
    def __init__(self, message: str, response: dict = None):
        self.message = message
        self.response = response or {}
        super().__init__(message)


class ViettelPostClient:
    def __init__(self, config: ViettelPostConfig = None):
        self.config = config or ViettelPostConfig.from_settings()
        self.session = requests.Session()
        self.session.headers.update({"Token": self.config.token, "Content-Type": "application/json"})

    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        url = f"{self.config.base_url}{endpoint}"
        for attempt in range(self.config.max_retries):
            try:
                resp = self.session.request(method, url, timeout=self.config.timeout, **kwargs)
                data = resp.json() if resp.content else {}
                if resp.status_code == 200 and data.get("status") == 200:
                    return data.get("data", {})
                raise ViettelPostAPIError(data.get("message", "Unknown error"), data)
            except requests.RequestException as e:
                if attempt == self.config.max_retries - 1:
                    raise ViettelPostAPIError(f"Network error: {e}")
                time.sleep(2 ** attempt)
        raise ViettelPostAPIError("Max retries exceeded")

    def create_order(self, order_data: dict) -> dict:
        res = self._request("POST", "/createOrder", json=order_data)
        code = res.get("ORDER_NUMBER", "")
        return {"order_code": code, "tracking_code": code, "total_fee": res.get("MONEY_TOTAL", 0), "cod_amount": order_data.get("COD_AMOUNT", 0), "raw": res}

    def get_order_detail(self, order_code: str) -> dict:
        return self._request("POST", "/getOrderDetail", json={"ORDER_NUMBER": order_code})

    def cancel_order(self, order_code: str, cancel_reason: str = "") -> dict:
        return self._request("POST", "/cancelOrder", json={"ORDER_NUMBER": order_code})


def get_viettelpost_client() -> Optional[ViettelPostClient]:
    config = ViettelPostConfig.from_settings()
    if not config.is_configured():
        logger.warning("ViettelPost not configured: missing VIETTELPOST_TOKEN")
        return None
    return ViettelPostClient(config)


def build_viettelpost_order_payload(order, carrier_config: dict) -> dict:
    items = order.items.all()
    products = [{"PRODUCT_NAME": i.product_name or i.product.name, "PRODUCT_QUANTITY": i.quantity} for i in items]
    return {
        "ORDER_NUMBER": f"HG{order.id}",
        "SENDER_FULLNAME": "HUUGIAU Atelier",
        "SENDER_ADDRESS": getattr(settings, "STORE_ADDRESS", ""),
        "SENDER_PHONE": getattr(settings, "HOTLINE", ""),
        "RECEIVER_FULLNAME": order.customer_name,
        "RECEIVER_ADDRESS": order.shipping_address,
        "RECEIVER_PHONE": order.phone,
        "PRODUCT_TYPE": "HH",
        "ORDER_PAYMENT": 3 if order.payment_method == "cod" else 1,
        "COD_AMOUNT": int(order.total_amount) if order.payment_method == "cod" else 0,
        "MONEY_COLLECTION": int(order.total_amount) if order.payment_method == "cod" else 0,
        "NOTE": order.note or "",
        "LIST_ITEM": products,
    }
