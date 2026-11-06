"""GHN Webhook Handler"""

import hmac
import json
import logging

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from orders.models import ShippingOrder

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def ghn_webhook(request: HttpRequest) -> HttpResponse:
    expected_token = settings.GHN_WEBHOOK_TOKEN
    received_token = request.headers.get("Token", "") or request.headers.get(
        "X-GHN-Token", ""
    )
    if not expected_token:
        logger.error("GHN webhook rejected: GHN_WEBHOOK_TOKEN is not configured")
        return JsonResponse(
            {"code": 503, "message": "Webhook is not configured"}, status=503
        )
    if not hmac.compare_digest(received_token, expected_token):
        logger.warning(
            "GHN webhook invalid token from %s", request.META.get("REMOTE_ADDR")
        )
        return JsonResponse({"code": 401, "message": "Invalid token"}, status=401)

    try:
        if request.content_type == "application/json":
            payload = json.loads(request.body)
        else:
            payload = request.POST.dict()
        if not isinstance(payload, dict):
            return JsonResponse({"code": 400, "message": "Invalid payload"}, status=400)

        order_code = payload.get("OrderCode") or payload.get("order_code")
        if not isinstance(order_code, str) or not order_code.strip():
            logger.warning("GHN webhook missing OrderCode")
            return JsonResponse(
                {"code": 400, "message": "Missing OrderCode"}, status=400
            )

        try:
            shipping_order = ShippingOrder.objects.select_related("order").get(
                carrier="ghn", carrier_order_code=order_code
            )
        except ShippingOrder.DoesNotExist:
            logger.warning("GHN webhook: ShippingOrder not found for %s", order_code)
            return JsonResponse({"code": 503, "message": "Order not ready"}, status=503)

        carrier_data = {**payload, "order_code": order_code}
        event_type = payload.get("Type")
        if event_type in (None, "switch_status", "create"):
            carrier_data["status"] = payload.get("Status", payload.get("status", ""))
        if event_type in (None, "update_fee") and (
            "TotalFee" in payload or "total_fee" in payload
        ):
            carrier_data["total_fee"] = payload.get(
                "TotalFee", payload.get("total_fee")
            )
        if event_type in (None, "update_cod") and (
            "CODAmount" in payload or "cod_amount" in payload
        ):
            carrier_data["cod_amount"] = payload.get(
                "CODAmount", payload.get("cod_amount")
            )
        shipping_order.update_from_carrier(carrier_data)

        logger.info(
            "GHN webhook processed: %s -> %s", order_code, shipping_order.status
        )
        return JsonResponse({"code": 200, "message": "Success"})

    except json.JSONDecodeError:
        logger.exception("GHN webhook invalid JSON")
        return JsonResponse({"code": 400, "message": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.exception("GHN webhook error: %s", e)
        return JsonResponse({"code": 500, "message": "Internal error"}, status=500)
