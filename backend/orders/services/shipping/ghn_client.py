"""GHN (Giao Hàng Nhanh) API Client"""

import logging
import time
from dataclasses import dataclass
from typing import Optional

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class GHNConfig:
    token: str
    shop_id: int
    base_url: str = "https://dev-online-gateway.ghn.vn/shiip/public-api"
    timeout: int = 30
    max_retries: int = 3

    @classmethod
    def from_settings(cls) -> "GHNConfig":
        return cls(
            token=settings.GHN_TOKEN,
            shop_id=settings.GHN_SHOP_ID,
            base_url=settings.GHN_BASE_URL,
        )

    def is_configured(self) -> bool:
        return bool(self.token and self.shop_id)


class GHNAPIError(Exception):
    def __init__(self, code: int, message: str, response: dict = None):
        self.code = code
        self.message = message
        self.response = response or {}
        super().__init__(f"GHN API Error {code}: {message}")


class GHNClient:
    """GHN API Client with retry logic and error handling"""

    def __init__(self, config: GHNConfig = None):
        self.config = config or GHNConfig.from_settings()
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Token": self.config.token,
                "ShopId": str(self.config.shop_id),
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
                if resp.status_code == 200 and data.get("code") == 200:
                    return data.get("data", {})
                raise GHNAPIError(
                    code=data.get("code", resp.status_code),
                    message=data.get("message", "Unknown error"),
                    response=data,
                )
            except requests.RequestException as e:
                if attempt == self.config.max_retries - 1:
                    raise GHNAPIError(-1, f"Network error after retries: {e}")
                time.sleep(2**attempt)
        raise GHNAPIError(-1, "Max retries exceeded")

    def get_provinces(self) -> list[dict]:
        return self._request("GET", "/master-data/province")

    def get_districts(self, province_id: int) -> list[dict]:
        return self._request(
            "GET", "/master-data/district", params={"province_id": province_id}
        )

    def get_wards(self, district_id: int) -> list[dict]:
        return self._request(
            "GET", "/master-data/ward", params={"district_id": district_id}
        )

    def calculate_fee(
        self,
        from_district_id: int,
        to_district_id: int,
        to_ward_code: str,
        weight: int,
        length: int = 10,
        width: int = 10,
        height: int = 10,
        service_type_id: int = 2,
        insurance_value: int = 0,
        coupon: str = None,
    ) -> dict:
        payload = {
            "from_district_id": from_district_id,
            "to_district_id": to_district_id,
            "to_ward_code": to_ward_code,
            "weight": weight,
            "length": length,
            "width": width,
            "height": height,
            "service_type_id": service_type_id,
            "insurance_value": insurance_value,
        }
        if coupon:
            payload["coupon"] = coupon
        return self._request("POST", "/v2/shipping-order/fee", json=payload)

    def create_order(self, order_data: dict) -> dict:
        return self._request("POST", "/v2/shipping-order/create", json=order_data)

    def get_order_detail(self, order_code: str) -> dict:
        return self._request(
            "GET", "/v2/shipping-order/detail", params={"order_code": order_code}
        )

    def print_order(self, order_codes: list[str]) -> dict:
        return self._request(
            "POST", "/v2/a5/gen-token", json={"order_codes": order_codes}
        )

    def cancel_order(
        self, order_code: str, cancel_reason: str = "Khách hủy đơn"
    ) -> list[dict]:
        return self._request(
            "POST",
            "/v2/switch-status/cancel",
            json={
                "order_codes": [order_code],
                "reason_code": "GHN-CANCEL-OTHER",
                "reason": cancel_reason,
            },
        )

    def get_tracking(self, order_code: str) -> dict:
        return self._request(
            "GET", "/v2/tracking/detail", params={"order_code": order_code}
        )


def get_ghn_client() -> Optional[GHNClient]:
    config = GHNConfig.from_settings()
    if not config.is_configured():
        logger.warning("GHN not configured: missing GHN_TOKEN or GHN_SHOP_ID")
        return None
    return GHNClient(config)


def build_ghn_order_payload(order) -> dict:
    items = order.items.all()
    total_weight = 0
    products = []

    for item in items:
        variant = item.variant
        weight = getattr(variant, "weight", 200) if variant else 200
        qty = item.quantity
        total_weight += weight * qty
        products.append(
            {
                "name": item.product_name or item.product.name,
                "quantity": qty,
                "weight": weight,
                "category": {"level1": "Thời trang"},
            }
        )

    total_weight = max(total_weight, 200)

    return {
        "payment_type_id": 1,
        "note": order.note or "Đơn hàng từ HUUGIAU Atelier",
        "required_note": "KHONGCHOXEMHANG",
        "client_order_code": f"HG-{order.id}",
        "to_name": order.customer_name,
        "to_phone": order.phone,
        "to_address": order.shipping_address,
        "to_ward_name": order.shipping_ward_name,
        "to_province_name": order.shipping_province_name,
        "is_new_to_address": True,
        "cod_amount": int(order.total_amount) if order.payment_method == "cod" else 0,
        "content": ", ".join([p["name"] for p in products]),
        "weight": total_weight,
        "length": 30,
        "width": 20,
        "height": 10,
        "service_type_id": 2,
        "insurance_value": min(int(order.total_amount), 5_000_000),
        "items": products,
    }
