"""Shipping Service - Integration layer for GHN/GHTK"""

import logging
from typing import Optional

from django.conf import settings
from django.db import transaction

from orders.models import Order, ShippingOrder
from .ghn_client import (
    GHNAPIError,
    build_ghn_order_payload,
    get_ghn_client,
)
from .ghtk_client import build_ghtk_order_payload, get_ghtk_client
from .viettelpost_client import build_viettelpost_order_payload, get_viettelpost_client
from .vnpost_client import build_vnpost_order_payload, get_vnpost_client
from .jnt_client import build_jnt_order_payload, get_jnt_client

logger = logging.getLogger(__name__)


# Default carrier config from settings
def get_carrier_config(carrier: str) -> dict:
    """Get carrier configuration from settings"""
    base = {
        "from_ward_code": getattr(settings, "GHN_FROM_WARD_CODE", ""),
        "from_district_id": getattr(settings, "GHN_FROM_DISTRICT_ID", 0),
        "from_province_id": getattr(settings, "GHN_FROM_PROVINCE_ID", 0),
        "service_id": getattr(settings, "GHN_SERVICE_ID", 53320),
    }
    if carrier == "ghtk":
        base.update(
            {
                "from_ward_code": getattr(settings, "GHTK_FROM_WARD_CODE", ""),
                "from_district_id": getattr(settings, "GHTK_FROM_DISTRICT_ID", 0),
                "from_province_id": getattr(settings, "GHTK_FROM_PROVINCE_ID", 0),
            }
        )
    return base


def create_shipping_order(order: Order, carrier: str = None) -> Optional[ShippingOrder]:
    """
    Tạo đơn hàng vận chuyển tự động sau khi checkout thành công.
    Called from checkout flow after order is created and paid (for non-COD).
    """
    if not order.carrier:
        order.carrier = carrier or "ghn"
        order.save(update_fields=["carrier"])

    if order.carrier == "ghn":
        return _create_ghn_shipping_order(order)
    elif order.carrier in ("ghtk", "viettelpost", "jnt", "vnpost"):
        return _create_generic_shipping_order(order, order.carrier)
    return None


def _create_ghn_shipping_order(order: Order) -> Optional[ShippingOrder]:
    client = get_ghn_client()
    if not client:
        logger.warning(
            f"GHN not configured, skipping shipping order for Order #{order.id}"
        )
        return None

    shipping_order, _ = ShippingOrder.objects.get_or_create(
        order=order,
        defaults={
            "carrier": "ghn",
            "carrier_order_code": f"pending-{order.id}",
            "status": "created",
        },
    )
    if shipping_order.status not in ("created", "failed"):
        return shipping_order
    if not order.shipping_ward_name or not order.shipping_province_name:
        shipping_order.status = "failed"
        shipping_order.error_message = (
            "Thiếu phường/xã hoặc tỉnh/thành nhận hàng cho GHN."
        )
        shipping_order.save(update_fields=["status", "error_message", "updated_at"])
        return shipping_order
    try:
        response = client.create_order(build_ghn_order_payload(order))
        carrier_order_code = response.get("order_code", "")
        if not carrier_order_code:
            raise GHNAPIError(-1, "GHN không trả mã vận đơn", response)
        shipping_order.carrier_order_code = carrier_order_code
        shipping_order.tracking_code = carrier_order_code
        shipping_order.status = "pending_pickup"
        shipping_order.error_message = ""
        shipping_order.raw_response = response
        shipping_order.actual_fee = response.get("total_fee", 0)
        shipping_order.cod_amount = (
            int(order.total_amount) if order.payment_method == "cod" else 0
        )
        shipping_order.save()
        order.tracking_code = carrier_order_code
        order.status = "shipping"
        order.save(update_fields=["tracking_code", "status", "updated_at"])
        logger.info(
            "Created GHN shipping order %s for Order #%s", carrier_order_code, order.id
        )
        return shipping_order
    except GHNAPIError as e:
        logger.error("GHN API error for Order #%s: %s", order.id, e.message)
        shipping_order.error_message = e.message
        shipping_order.raw_response = e.response
        shipping_order.status = "failed"
        shipping_order.save(
            update_fields=["error_message", "raw_response", "status", "updated_at"]
        )
        return shipping_order
    except Exception as e:
        logger.exception(
            "Unexpected error creating GHN order for Order #%s: %s", order.id, e
        )
        shipping_order.error_message = str(e)
        shipping_order.status = "failed"
        shipping_order.save(update_fields=["error_message", "status", "updated_at"])
        return shipping_order


def _get_carrier_client(carrier: str):
    # ponytail: 1 cho chung, them carrier moi chi them 2 dong o day
    if carrier == "ghtk":
        return get_ghtk_client(), build_ghtk_order_payload
    if carrier == "viettelpost":
        return get_viettelpost_client(), build_viettelpost_order_payload
    if carrier == "vnpost":
        return get_vnpost_client(), build_vnpost_order_payload
    if carrier == "jnt":
        return get_jnt_client(), build_jnt_order_payload
    return None, None


def _create_ghtk_shipping_order(order: Order) -> Optional[ShippingOrder]:
    return _create_generic_shipping_order(order, "ghtk")


def _create_generic_shipping_order(
    order: Order, carrier: str
) -> Optional[ShippingOrder]:
    client, builder = _get_carrier_client(carrier)
    if not client:
        logger.warning(
            f"{carrier} not configured, skipping shipping order for Order #{order.id}"
        )
        return None
    try:
        with transaction.atomic():
            shipping_order = ShippingOrder.objects.create(
                order=order, carrier=carrier, carrier_order_code="", status="created"
            )
            payload = builder(order, get_carrier_config(carrier))
            response = client.create_order(payload)
            code = response.get("order_code", "") or response.get("tracking_code", "")
            shipping_order.carrier_order_code = code
            shipping_order.tracking_code = response.get("tracking_code", "") or code
            shipping_order.status = "pending_pickup"
            shipping_order.raw_response = response.get("raw", response)
            shipping_order.actual_fee = response.get("total_fee", 0) or 0
            shipping_order.cod_amount = response.get("cod_amount", 0) or 0
            shipping_order.save(
                update_fields=[
                    "carrier_order_code",
                    "tracking_code",
                    "status",
                    "raw_response",
                    "actual_fee",
                    "cod_amount",
                    "updated_at",
                ]
            )
            order.tracking_code = shipping_order.tracking_code
            order.status = "shipping"
            order.save(update_fields=["tracking_code", "status", "updated_at"])
            return shipping_order
    except Exception as e:
        logger.exception(f"Error creating {carrier} order for Order #{order.id}: {e}")
        try:
            shipping_order.error_message = str(e)[:500]
            shipping_order.status = "failed"
            shipping_order.save(update_fields=["error_message", "status", "updated_at"])
            return shipping_order
        except Exception:
            return None


def print_shipping_label(shipping_order: ShippingOrder) -> Optional[bytes]:
    """In tem vận đơn - trả về PDF bytes"""
    if shipping_order.carrier == "ghn":
        return _print_ghn_label(shipping_order)
    return None


def _print_ghn_label(shipping_order: ShippingOrder) -> Optional[bytes]:
    client = get_ghn_client()
    if not client:
        return None

    try:
        token = client.print_order([shipping_order.carrier_order_code]).get("token")
        if not token:
            return None
        from urllib.parse import urlsplit

        from django.core.files.base import ContentFile

        parsed = urlsplit(client.config.base_url)
        url = f"{parsed.scheme}://{parsed.netloc}/a5/public-api/printA5"
        response = client.session.get(url, params={"token": token}, timeout=30)
        response.raise_for_status()
        pdf_bytes = response.content
        if not pdf_bytes.startswith(b"%PDF-"):
            logger.error(
                "GHN print endpoint did not return PDF for %s",
                shipping_order.carrier_order_code,
            )
            return None
        filename = f"label_{shipping_order.carrier_order_code}.pdf"
        shipping_order.shipping_label_pdf.save(
            filename, ContentFile(pdf_bytes), save=True
        )
        return pdf_bytes
    except Exception as e:
        logger.error(
            f"Error printing GHN label for {shipping_order.carrier_order_code}: {e}"
        )
        return None


def cancel_shipping_order(
    shipping_order: ShippingOrder, reason: str = "Khách hủy đơn"
) -> bool:
    """Hủy đơn vận chuyển"""
    if shipping_order.carrier == "ghn":
        return _cancel_ghn_order(shipping_order, reason)
    client, _ = _get_carrier_client(shipping_order.carrier)
    if not client:
        return False
    try:
        client.cancel_order(shipping_order.carrier_order_code, reason)
        shipping_order.status = "cancelled"
        shipping_order.save(update_fields=["status", "updated_at"])
        return True
    except Exception as e:
        logger.error(f"Error cancelling {shipping_order.carrier} order: {e}")
        return False


def _cancel_ghn_order(shipping_order: ShippingOrder, reason: str) -> bool:
    client = get_ghn_client()
    if not client:
        return False

    try:
        results = client.cancel_order(shipping_order.carrier_order_code, reason)
        if not results or not results[0].get("result"):
            logger.warning(
                "GHN refused cancellation for %s: %s",
                shipping_order.carrier_order_code,
                results,
            )
            return False
        shipping_order.status = "cancelled"
        shipping_order.save(update_fields=["status", "updated_at"])

        # Restore parent order status if needed
        if shipping_order.order.status == "shipping":
            shipping_order.order.status = "processing"
            shipping_order.order.save(update_fields=["status", "updated_at"])
        return True
    except Exception as e:
        logger.error(
            f"Error cancelling GHN order {shipping_order.carrier_order_code}: {e}"
        )
        return False


def sync_shipping_status(shipping_order: ShippingOrder) -> bool:
    """Sync trạng thái từ carrier (manual sync hoặc cron job)"""
    if shipping_order.carrier == "ghn":
        return _sync_ghn_status(shipping_order)
    client, _ = _get_carrier_client(shipping_order.carrier)
    if not client:
        return False
    try:
        response = client.get_order_detail(shipping_order.carrier_order_code)
        shipping_order.update_from_carrier(response)
        return True
    except Exception as e:
        logger.error(f"Error syncing {shipping_order.carrier} status: {e}")
        return False


def _sync_ghn_status(shipping_order: ShippingOrder) -> bool:
    client = get_ghn_client()
    if not client:
        return False

    try:
        response = client.get_order_detail(shipping_order.carrier_order_code)
        shipping_order.update_from_carrier(response)
        return True
    except Exception as e:
        logger.error(
            f"Error syncing GHN status for {shipping_order.carrier_order_code}: {e}"
        )
        return False


def calculate_shipping_fee(
    from_district_id: int,
    to_district_id: int,
    to_ward_code: str,
    weight: int,
    length: int = 30,
    width: int = 20,
    height: int = 10,
) -> Optional[dict]:
    """Tính phí ship từ GHN"""
    client = get_ghn_client()
    if not client:
        return None

    try:
        return client.calculate_fee(
            from_district_id=from_district_id,
            to_district_id=to_district_id,
            to_ward_code=to_ward_code,
            weight=weight,
            length=length,
            width=width,
            height=height,
        )
    except Exception as e:
        logger.error(f"Error calculating GHN fee: {e}")
        return None
