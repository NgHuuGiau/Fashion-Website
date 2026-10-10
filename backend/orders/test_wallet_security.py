import hashlib
import hmac
import json
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse

from . import momo, zalopay
from .models import Order


@override_settings(
    MOMO_PARTNER_CODE="partner",
    MOMO_ACCESS_KEY="access",
    MOMO_SECRET_KEY="secret",
    MOMO_ENDPOINT="https://example.test/create",
    ZALOPAY_APP_ID="123",
    ZALOPAY_KEY1="key-one",
    ZALOPAY_KEY2="key-two",
    ZALOPAY_ENDPOINT="https://example.test/create",
)
class WalletCallbackTest(TestCase):
    def make_order(self, method, merchant_id):
        return Order.objects.create(
            customer_name="Buyer",
            phone="0900000000",
            shipping_address="HCM",
            payment_method=method,
            total_amount=100000,
            gateway_transaction_id=merchant_id,
        )

    def test_momo_ipn_uses_exact_merchant_id_and_is_idempotent(self):
        order = self.make_order("momo", "7_20261009")
        other = self.make_order("momo", "7_20261010")
        params = {
            "amount": 100000,
            "extraData": "",
            "message": "Success",
            "orderId": "7_20261009",
            "orderInfo": "Thanh toan don hang 7",
            "orderType": "momo_wallet",
            "partnerCode": "partner",
            "payType": "webApp",
            "requestId": "request-7",
            "responseTime": 123456,
            "resultCode": 0,
            "transId": 9988,
        }
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
        params["signature"] = momo._secure_hash(params, fields)

        with (
            patch("orders.services.order_email.send_order_email"),
            patch("orders.services.shipping.service.create_shipping_order"),
        ):
            response = self.client.post(
                reverse("orders:momo_ipn"),
                data=json.dumps(params),
                content_type="application/json",
            )
            again = self.client.post(
                reverse("orders:momo_ipn"),
                data=json.dumps(params),
                content_type="application/json",
            )

        order.refresh_from_db()
        other.refresh_from_db()
        self.assertEqual(response.json()["return_code"], 0)
        self.assertEqual(again.json()["message"], "already confirmed")
        self.assertTrue(order.is_paid)
        self.assertFalse(other.is_paid)
        self.assertEqual(order.gateway_transaction_id, "7_20261009")

    def test_momo_signature_uses_access_key_and_documented_fields(self):
        params = {"amount": 100000, "orderId": "7_20261009"}
        expected = hmac.new(
            b"secret",
            b"accessKey=access&amount=100000&orderId=7_20261009",
            hashlib.sha256,
        ).hexdigest()
        self.assertEqual(momo._secure_hash(params, ("amount", "orderId")), expected)

    def test_zalopay_ipn_unwraps_signed_data(self):
        order = self.make_order("zalopay", "261009_abcdef12")
        payload = json.dumps(
            {
                "app_trans_id": "261009_abcdef12",
                "amount": 100000,
                "zp_trans_id": 123456,
            },
            separators=(",", ":"),
        )
        envelope = {
            "data": payload,
            "mac": hmac.new(b"key-two", payload.encode(), hashlib.sha256).hexdigest(),
            "type": 1,
        }

        with (
            patch("orders.services.order_email.send_order_email"),
            patch("orders.services.shipping.service.create_shipping_order"),
        ):
            response = self.client.post(
                reverse("orders:zalopay_ipn"),
                data=json.dumps(envelope),
                content_type="application/json",
            )

        order.refresh_from_db()
        self.assertEqual(response.json()["return_code"], 1)
        self.assertTrue(order.is_paid)
        self.assertEqual(order.gateway_transaction_id, "261009_abcdef12")

    def test_zalopay_create_uses_documented_mac(self):
        order = self.make_order("zalopay", "")
        with patch("orders.zalopay.requests.post") as post:
            post.return_value.json.return_value = {
                "return_code": 1,
                "order_url": "https://example.test/pay",
            }
            result = zalopay.build_payment_request(
                order, "127.0.0.1", "https://shop.test/return", "https://shop.test/ipn"
            )
        params = post.call_args.kwargs["data"]
        raw = "|".join(
            str(params[field])
            for field in (
                "app_id",
                "app_trans_id",
                "app_user",
                "amount",
                "app_time",
                "embed_data",
                "item",
            )
        )
        expected = hmac.new(b"key-one", raw.encode(), hashlib.sha256).hexdigest()
        self.assertEqual(params["mac"], expected)
        self.assertEqual(result["app_trans_id"], params["app_trans_id"])

    def test_zalopay_ipn_rejects_tampered_payload(self):
        order = self.make_order("zalopay", "261009_abcdef12")
        payload = json.dumps(
            {"app_trans_id": "261009_abcdef12", "amount": 100000, "zp_trans_id": 123}
        )
        envelope = {
            "data": payload.replace("100000", "100001"),
            "mac": hmac.new(b"key-two", payload.encode(), hashlib.sha256).hexdigest(),
        }
        response = self.client.post(
            reverse("orders:zalopay_ipn"),
            data=json.dumps(envelope),
            content_type="application/json",
        )
        order.refresh_from_db()
        self.assertEqual(response.json()["return_code"], -1)
        self.assertFalse(order.is_paid)

    def test_zalopay_redirect_signature_and_amount(self):
        self.make_order("zalopay", "261009_abcdef12")
        params = {
            "appid": "123",
            "apptransid": "261009_abcdef12",
            "pmcid": "38",
            "bankcode": "",
            "amount": "100000",
            "discountamount": "0",
            "status": "1",
        }
        raw = "|".join(params.values())
        params["checksum"] = hmac.new(
            b"key-two", raw.encode(), hashlib.sha256
        ).hexdigest()
        with (
            patch("orders.services.order_email.send_order_email"),
            patch("orders.services.shipping.service.create_shipping_order"),
            patch("orders.views.wallets.log_activity"),
            patch(
                "orders.zalopay.query_transaction",
                return_value={
                    "success": True,
                    "data": {"amount": 100000, "zp_trans_id": 777},
                },
            ),
        ):
            response = self.client.get(reverse("orders:zalopay_return"), params)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Order.objects.get(gateway_transaction_id="261009_abcdef12").is_paid
        )
        self.assertEqual(
            Order.objects.get(gateway_transaction_id="261009_abcdef12")
            .status_history.latest("id")
            .transaction_id,
            "777",
        )

    def test_zalopay_redirect_waits_if_query_cannot_confirm(self):
        order = self.make_order("zalopay", "261009_abcdef12")
        params = {
            "appid": "123",
            "apptransid": "261009_abcdef12",
            "pmcid": "38",
            "bankcode": "",
            "amount": "100000",
            "discountamount": "0",
            "status": "1",
        }
        params["checksum"] = hmac.new(
            b"key-two", "|".join(params.values()).encode(), hashlib.sha256
        ).hexdigest()
        for query in (
            {"success": False},
            {"success": True, "data": {"amount": 1, "zp_trans_id": 777}},
        ):
            with (
                self.subTest(query=query),
                patch("orders.zalopay.query_transaction", return_value=query),
            ):
                response = self.client.get(reverse("orders:zalopay_return"), params)
                order.refresh_from_db()
                self.assertEqual(response.status_code, 302)
                self.assertFalse(order.is_paid)
