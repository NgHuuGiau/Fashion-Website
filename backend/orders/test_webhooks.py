import json
from unittest.mock import Mock, patch

from django.test import TestCase, override_settings
from django.urls import reverse

from .forms import CheckoutForm
from .models import Order, ShippingOrder
from .services.shipping.ghn_client import GHNAPIError, GHNClient, GHNConfig
from .services.shipping.service import (
    cancel_shipping_order,
    create_shipping_order,
    print_shipping_label,
)


class GHNWebhookAuthenticationTest(TestCase):
    def setUp(self):
        self.url = reverse("orders:ghn_webhook")

    def post_webhook(self, *, token=None, payload=None):
        headers = {"HTTP_TOKEN": token} if token is not None else {}
        return self.client.post(
            self.url,
            data=json.dumps(
                payload
                or {
                    "OrderCode": "GHN-123",
                    "Type": "switch_status",
                    "Status": "delivered",
                    "CODAmount": 0,
                    "TotalFee": 0,
                }
            ),
            content_type="application/json",
            **headers,
        )

    @override_settings(GHN_WEBHOOK_TOKEN="")
    def test_webhook_fails_closed_when_token_is_not_configured(self):
        response = self.post_webhook(token="anything")

        self.assertEqual(response.status_code, 503)

    @override_settings(GHN_WEBHOOK_TOKEN="correct-secret")
    def test_webhook_rejects_missing_or_invalid_token(self):
        for token in (None, "wrong-secret"):
            with self.subTest(token=token):
                response = self.post_webhook(token=token)
                self.assertEqual(response.status_code, 401)

    @override_settings(GHN_WEBHOOK_TOKEN="correct-secret")
    def test_custom_header_authenticates_and_invalid_json_returns_400(self):
        response = self.client.post(
            self.url,
            data="{invalid",
            content_type="application/json",
            HTTP_X_GHN_TOKEN="correct-secret",
        )
        self.assertEqual(response.status_code, 400)

    @override_settings(GHN_WEBHOOK_TOKEN="correct-secret")
    def test_valid_webhook_updates_shipping_and_order_status(self):
        order = Order.objects.create(
            customer_name="Test buyer",
            phone="0900000000",
            shipping_address="Ho Chi Minh City",
            payment_method="cod",
            total_amount=100000,
        )
        shipping_order = ShippingOrder.objects.create(
            order=order,
            carrier="ghn",
            carrier_order_code="GHN-123",
        )

        response = self.post_webhook(token="correct-secret")

        self.assertEqual(response.status_code, 200)
        shipping_order.refresh_from_db()
        order.refresh_from_db()
        self.assertEqual(shipping_order.status, "delivered")
        self.assertEqual(order.status, "delivered")
        self.assertEqual(shipping_order.raw_response["Type"], "switch_status")

        self.post_webhook(token="correct-secret")
        self.assertEqual(order.status_history.filter(to_status="delivered").count(), 1)

    @override_settings(GHN_WEBHOOK_TOKEN="correct-secret")
    def test_fee_and_cod_events_do_not_clobber_status_or_each_other(self):
        order = Order.objects.create(
            customer_name="Buyer",
            phone="0900000000",
            shipping_address="Hồ Chí Minh",
            total_amount=100000,
        )
        shipping = ShippingOrder.objects.create(
            order=order,
            carrier="ghn",
            carrier_order_code="GHN-123",
            actual_fee=25000,
            cod_amount=100000,
        )
        response = self.post_webhook(
            token="correct-secret",
            payload={
                "OrderCode": "GHN-123",
                "Type": "update_fee",
                "TotalFee": 30000,
                "CODAmount": 0,
                "Status": "",
            },
        )
        self.assertEqual(response.status_code, 200)
        shipping.refresh_from_db()
        self.assertEqual(shipping.actual_fee, 30000)
        self.assertEqual(shipping.cod_amount, 100000)
        self.assertEqual(shipping.status, "created")

        self.post_webhook(
            token="correct-secret",
            payload={
                "OrderCode": "GHN-123",
                "Type": "update_cod",
                "CODAmount": 90000,
                "TotalFee": 0,
            },
        )
        shipping.refresh_from_db()
        self.assertEqual(shipping.actual_fee, 30000)
        self.assertEqual(shipping.cod_amount, 90000)

    @override_settings(GHN_WEBHOOK_TOKEN="correct-secret")
    def test_unknown_order_is_retryable_and_bad_payload_is_rejected(self):
        self.assertEqual(self.post_webhook(token="correct-secret").status_code, 503)
        self.assertEqual(
            self.post_webhook(
                token="correct-secret", payload={"Status": "picked"}
            ).status_code,
            400,
        )


class GHNShippingIntegrationTest(TestCase):
    @override_settings(GHN_TOKEN="test-token", GHN_SHOP_ID=123)
    def test_checkout_requires_ghn_region_when_enabled(self):
        form = CheckoutForm(
            data={
                "customer_name": "Buyer",
                "phone": "0900000000",
                "shipping_address": "1 Đường A",
                "payment_method": "cod",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("shipping_ward_name", form.errors)
        self.assertIn("shipping_province_name", form.errors)

    @override_settings(
        GHN_TOKEN="test-token",
        GHN_SHOP_ID=123,
        GHN_BASE_URL="https://dev-online-gateway.ghn.vn/shiip/public-api",
    )
    def test_ghn_endpoints_and_payload(self):
        client = GHNClient(GHNConfig.from_settings())
        client._request = Mock(return_value={"order_code": "GHN-123"})
        client.create_order({"client_order_code": "HG-1"})
        self.assertEqual(client._request.call_args.args[1], "/v2/shipping-order/create")
        client.get_order_detail("GHN-123")
        self.assertEqual(client._request.call_args.args[1], "/v2/shipping-order/detail")
        client.print_order(["GHN-123"])
        self.assertEqual(client._request.call_args.args[1], "/v2/a5/gen-token")
        client.cancel_order("GHN-123")
        self.assertEqual(client._request.call_args.args[1], "/v2/switch-status/cancel")
        self.assertEqual(
            client._request.call_args.kwargs["json"]["order_codes"], ["GHN-123"]
        )

    @override_settings(GHN_TOKEN="test-token", GHN_SHOP_ID=123)
    @patch("orders.services.shipping.service.get_ghn_client")
    def test_failed_create_persists_and_can_retry_without_duplicate(self, get_client):
        client = get_client.return_value
        client.create_order.side_effect = [
            GHNAPIError(500, "Temporary error"),
            {"order_code": "GHN-123", "total_fee": 25000},
        ]
        order = Order.objects.create(
            customer_name="Buyer",
            phone="0900000000",
            shipping_address="1 Đường A, Phường Sài Gòn, Hồ Chí Minh",
            shipping_ward_name="Phường Sài Gòn",
            shipping_province_name="Hồ Chí Minh",
            payment_method="cod",
            total_amount=100000,
        )
        failed = create_shipping_order(order)
        self.assertEqual(failed.status, "failed")
        self.assertEqual(failed.carrier_order_code, f"pending-{order.id}")
        shipped = create_shipping_order(order)
        self.assertEqual(shipped.status, "pending_pickup")
        self.assertEqual(shipped.carrier_order_code, "GHN-123")
        self.assertEqual(ShippingOrder.objects.filter(order=order).count(), 1)
        payload = client.create_order.call_args.args[0]
        self.assertEqual(payload["client_order_code"], f"HG-{order.id}")
        self.assertEqual(payload["payment_type_id"], 1)
        self.assertEqual(payload["to_ward_name"], "Phường Sài Gòn")
        self.assertTrue(payload["is_new_to_address"])

    @override_settings(GHN_TOKEN="test-token", GHN_SHOP_ID=123)
    @patch("orders.services.shipping.service.get_ghn_client")
    def test_missing_region_does_not_call_ghn(self, get_client):
        order = Order.objects.create(
            customer_name="Buyer", phone="0900000000", shipping_address="HCM"
        )
        shipping = create_shipping_order(order)
        self.assertEqual(shipping.status, "failed")
        self.assertIn("phường/xã", shipping.error_message)
        get_client.return_value.create_order.assert_not_called()

    @override_settings(GHN_TOKEN="test-token", GHN_SHOP_ID=123)
    @patch("orders.services.shipping.service.get_ghn_client")
    def test_cancel_requires_carrier_success(self, get_client):
        order = Order.objects.create(
            customer_name="Buyer",
            phone="0900000000",
            shipping_address="HCM",
            status="shipping",
        )
        shipping = ShippingOrder.objects.create(
            order=order,
            carrier="ghn",
            carrier_order_code="GHN-123",
            status="pending_pickup",
        )
        get_client.return_value.cancel_order.return_value = [
            {"order_code": "GHN-123", "result": False}
        ]
        self.assertFalse(cancel_shipping_order(shipping))
        shipping.refresh_from_db()
        self.assertEqual(shipping.status, "pending_pickup")

    @override_settings(GHN_TOKEN="test-token", GHN_SHOP_ID=123)
    @patch("django.db.models.fields.files.FieldFile.save")
    @patch("orders.services.shipping.service.get_ghn_client")
    def test_print_label_downloads_pdf_from_token(self, get_client, save_file):
        order = Order.objects.create(
            customer_name="Buyer", phone="0900000000", shipping_address="HCM"
        )
        shipping = ShippingOrder.objects.create(
            order=order, carrier="ghn", carrier_order_code="GHN-123"
        )
        client = get_client.return_value
        client.config.base_url = "https://dev-online-gateway.ghn.vn/shiip/public-api"
        client.print_order.return_value = {"token": "print-token"}
        client.session.get.return_value.content = b"%PDF-1.7\n"
        self.assertEqual(print_shipping_label(shipping), b"%PDF-1.7\n")
        self.assertEqual(
            client.session.get.call_args.args[0],
            "https://dev-online-gateway.ghn.vn/a5/public-api/printA5",
        )
        save_file.assert_called_once()
