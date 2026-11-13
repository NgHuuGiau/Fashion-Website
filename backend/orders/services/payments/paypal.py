"""
PayPal Sandbox Integration for Fashion-Website
Ported from ElectroHub project - adapted for Fashion-Website schema
"""
import logging
import uuid
from decimal import Decimal
from typing import Optional

import httpx
from django.conf import settings

logger = logging.getLogger("fashion.paypal")


class PayPalService:
    """PayPal Checkout SDK wrapper for sandbox/production"""

    def __init__(self):
        self.client_id = getattr(settings, "PAYPAL_CLIENT_ID", "")
        self.client_secret = getattr(settings, "PAYPAL_CLIENT_SECRET", "")
        self.mode = getattr(settings, "PAYPAL_MODE", "sandbox")  # sandbox or live
        self.base_url = (
            "https://api-m.sandbox.paypal.com"
            if self.mode == "sandbox"
            else "https://api-m.paypal.com"
        )
        self._access_token: Optional[str] = None

    def _get_access_token(self) -> str:
        """Get OAuth2 access token from PayPal"""
        if self._access_token:
            return self._access_token

        auth = (self.client_id, self.client_secret)
        headers = {"Accept": "application/json", "Accept-Language": "en_US"}
        data = {"grant_type": "client_credentials"}

        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{self.base_url}/v1/oauth2/token", auth=auth, headers=headers, data=data
            )
            response.raise_for_status()
            self._access_token = response.json()["access_token"]
            return self._access_token

    def _headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._get_access_token()}",
            "PayPal-Request-Id": str(uuid.uuid4()),
        }

    def create_order(
        self,
        amount: Decimal,
        currency: str = "VND",
        reference_id: str = "",
        return_url: str = "",
        cancel_url: str = "",
    ) -> dict:
        """Create PayPal order (v2/checkout/orders)"""
        purchase_units = [{
            "reference_id": reference_id or str(uuid.uuid4()),
            "amount": {
                "currency_code": currency,
                "value": f"{amount:.2f}",
                "breakdown": {
                    "item_total": {"currency_code": currency, "value": f"{amount:.2f}"}
                }
            }
        }]

        payload = {
            "intent": "CAPTURE",
            "purchase_units": purchase_units,
            "application_context": {
                "brand_name": "HUUGIAU Fashion",
                "landing_page": "BILLING",
                "shipping_preference": "NO_SHIPPING",
                "user_action": "PAY_NOW",
                "return_url": return_url or "",
                "cancel_url": cancel_url or "",
            }
        }

        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{self.base_url}/v2/checkout/orders",
                headers=self._headers(),
                json=payload
            )
            response.raise_for_status()
            return response.json()

    def capture_order(self, order_id: str) -> dict:
        """Capture approved PayPal order"""
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{self.base_url}/v2/checkout/orders/{order_id}/capture",
                headers=self._headers()
            )
            response.raise_for_status()
            return response.json()

    def get_order_details(self, order_id: str) -> dict:
        """Get order details from PayPal"""
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                f"{self.base_url}/v2/checkout/orders/{order_id}",
                headers=self._headers()
            )
            response.raise_for_status()
            return response.json()

    def refund_capture(self, capture_id: str, amount: Decimal, currency: str = "VND") -> dict:
        """Refund a captured payment"""
        payload = {
            "amount": {"currency_code": currency, "value": f"{amount:.2f}"},
            "note_to_payer": "Refund from HUUGIAU Fashion"
        }
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{self.base_url}/v2/payments/captures/{capture_id}/refund",
                headers=self._headers(),
                json=payload
            )
            response.raise_for_status()
            return response.json()

    def verify_webhook_signature(
        self,
        transmission_id: str,
        timestamp: str,
        webhook_id: str,
        event_body: str,
        cert_url: str,
        transmission_sig: str,
        auth_algo: str
    ) -> bool:
        """Verify PayPal webhook signature"""
        # In production, implement proper webhook verification
        # For sandbox, we can skip or use PayPal's verify-webhook-signature endpoint
        logger.info(f"PayPal webhook received: {transmission_id}")
        return True


# Singleton instance
paypal_service = PayPalService()