"""Kiểm thử bảo mật chữ ký/IPN của 4 cổng thanh toán (momo/shopeepay/zalopay/vnpay).

Chỉ chạy trên hàm thuần, không cần DB. Trọng tâm: callback bị sửa hoặc sai
chữ ký phải bị từ chối, và mọi cổng phải chặn tiền tệ khác VND.
"""

import json
from decimal import Decimal
from types import SimpleNamespace
from unittest import mock

from django.test import SimpleTestCase, override_settings

from . import momo, shopeepay, vnpay, zalopay

MOMO_CFG = dict(
    MOMO_PARTNER_CODE="MOMO_PARTNER",
    MOMO_ACCESS_KEY="MOMO_ACCESS",
    MOMO_SECRET_KEY="MOMO_SECRET",
    MOMO_ENDPOINT="https://test-payment.momo.vn/v2/gateway/api/create",
)
SHOPEEPAY_CFG = dict(
    SHOPEEPAY_PARTNER_ID="12345",
    SHOPEEPAY_KEY="SP_KEY",
    SHOPEEPAY_SECRET="SP_SECRET",
    SHOPEEPAY_ENDPOINT="https://partner.shopeepay.vn",
)
ZALOPAY_CFG = dict(
    ZALOPAY_APP_ID="553",
    ZALOPAY_KEY1="ZP_KEY1",
    ZALOPAY_KEY2="ZP_KEY2",
    ZALOPAY_ENDPOINT="https://sb-openapi.zalopay.vn/v2/create",
)
VNPAY_CFG = dict(
    VNPAY_TMN_CODE="ABCD1234",
    VNPAY_HASH_SECRET="VNPAY_SECRET",
    VNPAY_URL="https://sandbox.vnpayment.vn/paymentv2/vpcpay.html",
    DEBUG=True,
)


def _order(total="100000", oid=1):
    return SimpleNamespace(id=oid, user_id=None, total_amount=Decimal(total))


@override_settings(**MOMO_CFG)
class MoMoSignatureTest(SimpleTestCase):
    FIELDS = (
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

    def _payload(self):
        data = {
            "amount": "100000",
            "extraData": "",
            "message": "Success",
            "orderId": "1_20260101000000",
            "orderInfo": "Thanh toan don hang 1",
            "orderType": "momo_wallet",
            "partnerCode": "MOMO_PARTNER",
            "payType": "qr",
            "requestId": "req-1",
            "responseTime": "1700000000000",
            "resultCode": "0",
            "transId": "999",
        }
        data["signature"] = momo._secure_hash(data, self.FIELDS)
        return data

    def test_valid_ipn_accepted(self):
        self.assertTrue(momo.verify_callback(self._payload()))

    def test_tampered_amount_rejected(self):
        data = self._payload()
        data["amount"] = "1"
        self.assertFalse(momo.verify_callback(data))

    def test_missing_field_rejected(self):
        data = self._payload()
        del data["transId"]
        self.assertFalse(momo.verify_callback(data))

    def test_unsigned_rejected(self):
        data = self._payload()
        data.pop("signature")
        self.assertFalse(momo.verify_callback(data))

    def test_amount_matches_enforces_currency(self):
        self.assertTrue(momo.amount_matches(_order(), {"amount": "100000"}))
        self.assertFalse(
            momo.amount_matches(_order(), {"amount": "100000", "currency": "USD"})
        )
        self.assertFalse(momo.amount_matches(_order(), {"amount": "1"}))


@override_settings(**SHOPEEPAY_CFG)
class ShopeePaySignatureTest(SimpleTestCase):
    def _payload(self):
        data = {
            "partner_order_id": "SP1_1",
            "order_id": "1",
            "amount": 100000,
            "currency": "VND",
            "status": "SUCCESS",
            "payment_method": "wallet",
            "transaction_time": 1700000000,
        }
        data["sign"] = shopeepay._secure_hash(data)
        return data

    def test_valid_callback_accepted(self):
        self.assertTrue(shopeepay.verify_callback(self._payload()))

    def test_tampered_amount_rejected(self):
        data = self._payload()
        data["amount"] = 1
        self.assertFalse(shopeepay.verify_callback(data))

    def test_unsigned_rejected(self):
        data = self._payload()
        data.pop("sign")
        self.assertFalse(shopeepay.verify_callback(data))

    def test_amount_matches_enforces_currency(self):
        self.assertTrue(shopeepay.amount_matches(_order(), {"amount": 100000}))
        self.assertFalse(
            shopeepay.amount_matches(_order(), {"amount": 100000, "currency": "USD"})
        )


@override_settings(**ZALOPAY_CFG)
class ZaloPaySignatureTest(SimpleTestCase):
    KEY2 = ZALOPAY_CFG["ZALOPAY_KEY2"]

    def _ipn(self):
        raw = json.dumps(
            {
                "app_trans_id": "260101_abc",
                "amount": 100000,
                "zp_trans_id": "999",
                "status": 1,
            }
        )
        return {"data": raw, "mac": zalopay._secure_hash(raw, self.KEY2)}

    def test_ipn_mac_accepted_and_payload_parsed(self):
        data = self._ipn()
        self.assertTrue(zalopay.verify_callback(data))
        self.assertEqual(zalopay.callback_payload(data)["app_trans_id"], "260101_abc")

    def test_ipn_tampered_rejected(self):
        data = self._ipn()
        data["mac"] = "deadbeef"
        self.assertFalse(zalopay.verify_callback(data))

    def test_redirect_checksum_accepted(self):
        data = {
            "appid": 553,
            "apptransid": "260101_abc",
            "pmcid": "37",
            "bankcode": "",
            "amount": 100000,
            "discountamount": 0,
            "status": 1,
        }
        fields = (
            "appid",
            "apptransid",
            "pmcid",
            "bankcode",
            "amount",
            "discountamount",
            "status",
        )
        data["checksum"] = zalopay._secure_hash(
            "|".join(str(data[field]) for field in fields), self.KEY2
        )
        self.assertTrue(zalopay.verify_callback(data))

    def test_embed_data_carries_order_id(self):
        with mock.patch("orders.zalopay.requests.post") as post:
            post.return_value.json.return_value = {
                "return_code": 1,
                "order_url": "u",
                "order_token": "t",
            }
            zalopay.build_payment_request(
                _order(oid=42), "127.0.0.1", "https://shop/return", "https://shop/ipn"
            )
            sent = post.call_args.kwargs["data"]
            self.assertEqual(json.loads(sent["embed_data"])["order_id"], 42)

    def test_amount_matches_enforces_currency(self):
        self.assertTrue(zalopay.amount_matches(_order(), {"amount": 100000}))
        self.assertFalse(
            zalopay.amount_matches(_order(), {"amount": 100000, "currency": "USD"})
        )


@override_settings(**VNPAY_CFG)
class VNPaySignatureTest(SimpleTestCase):
    def _payload(self):
        data = {
            "vnp_Amount": "10000000",
            "vnp_TxnRef": "1",
            "vnp_CurrCode": "VND",
            "vnp_ResponseCode": "00",
        }
        data["vnp_SecureHash"] = vnpay._secure_hash(data)
        return data

    def test_valid_return_accepted(self):
        self.assertTrue(vnpay.verify_return(self._payload()))

    def test_tampered_amount_rejected(self):
        data = self._payload()
        data["vnp_Amount"] = "1"
        self.assertFalse(vnpay.verify_return(data))

    def test_unsigned_rejected(self):
        data = self._payload()
        data.pop("vnp_SecureHash")
        self.assertFalse(vnpay.verify_return(data))

    def test_amount_matches_enforces_currency(self):
        params = {"vnp_Amount": "10000000", "vnp_CurrCode": "VND"}
        self.assertTrue(vnpay.amount_matches(_order(), params))
        self.assertFalse(
            vnpay.amount_matches(
                _order(), {"vnp_Amount": "10000000", "vnp_CurrCode": "USD"}
            )
        )
        self.assertFalse(vnpay.amount_matches(_order(), {"vnp_Amount": "999"}))


class UnconfiguredGatewayRejectsTest(SimpleTestCase):
    """Không cấu hình credentials thì callback phải bị từ chối, không crash."""

    @override_settings(
        MOMO_PARTNER_CODE="",
        MOMO_ACCESS_KEY="",
        MOMO_SECRET_KEY="",
        MOMO_ENDPOINT="",
        SHOPEEPAY_PARTNER_ID="",
        SHOPEEPAY_KEY="",
        SHOPEEPAY_SECRET="",
        SHOPEEPAY_ENDPOINT="",
        ZALOPAY_APP_ID="",
        ZALOPAY_KEY1="",
        ZALOPAY_KEY2="",
        ZALOPAY_ENDPOINT="",
        VNPAY_TMN_CODE="",
        VNPAY_HASH_SECRET="",
    )
    def test_all_gateways_reject_when_unconfigured(self):
        self.assertFalse(momo.verify_callback({"signature": "x"}))
        self.assertFalse(shopeepay.verify_callback({"sign": "x"}))
        self.assertFalse(zalopay.verify_callback({"data": "x", "mac": "y"}))
        self.assertFalse(vnpay.verify_return({"vnp_SecureHash": "x"}))
