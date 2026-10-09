"""GHN Webhook Handler"""

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
    try:
        if request.content_type == "application/json":
            payload = json.loads(request.body)
        else:
            payload = request.POST.dict()

        order_code = payload.get("order_code", "")
        if not order_code:
            logger.warning("GHN webhook missing order_code: %s", payload)
            return JsonResponse({"code": 400, "message": "Missing order_code"})

        try:
            shipping_order = ShippingOrder.objects.select_related("order").get(
                carrier="ghn", carrier_order_code=order_code
            )
        except ShippingOrder.DoesNotExist:
            logger.warning("GHN webhook: ShippingOrder not found for %s", order_code)
            return JsonResponse({"code": 404, "message": "Order not found"})

        expected_token = getattr(settings, "GHN_WEBHOOK_TOKEN", "")
        if expected_token:
            received_token = request.headers.get("Token", "") or request.headers.get(
                "X-GHN-Token", ""
            )
            if received_token != expected_token:
                logger.warning(
                    "GHN webhook invalid token from %s", request.META.get("REMOTE_ADDR")
                )
                return JsonResponse({"code": 401, "message": "Invalid token"})

        shipping_order.update_from_carrier(payload)

        logger.info(
            "GHN webhook processed: %s -> %s", order_code, shipping_order.status
        )
        return JsonResponse({"code": 200, "message": "Success"})

    except json.JSONDecodeError:
        logger.exception("GHN webhook invalid JSON")
        return JsonResponse({"code": 400, "message": "Invalid JSON"})
    except Exception as e:
        logger.exception("GHN webhook error: %s", e)
        return JsonResponse({"code": 500, "message": "Internal error"})
