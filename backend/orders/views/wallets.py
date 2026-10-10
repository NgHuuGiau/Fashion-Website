"""Wallet payments - MoMo / ZaloPay / ShopeePay chung 1 flow nhu VNPay.

ponytail: 3 vi khac nhau nhung flow giong het nhau:
  checkout -> redirect sang cong -> return/ipn -> mark paid + tao ship.
Gom chung de khoi lap 3x code return/ipn.
"""

import logging

from django.contrib import messages
from django.db import transaction
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from users.activity import log_activity

from .cart import restore_order_stock
from .payment import get_visitable_order
from ..models import Order

logger = logging.getLogger(__name__)

WALLET_METHODS = ("momo", "zalopay", "shopeepay")
WALLET_LABELS = {"momo": "MoMo", "zalopay": "ZaloPay", "shopeepay": "ShopeePay"}


def _gateway(method):
    if method == "momo":
        from .. import momo as g
    elif method == "zalopay":
        from .. import zalopay as g
    elif method == "shopeepay":
        from .. import shopeepay as g
    else:
        return None
    return g


def wallet_payment(request: HttpRequest, method: str, order_id) -> HttpResponse:
    if method not in WALLET_METHODS:
        messages.error(request, "Phuong thuc thanh toan khong ho tro.")
        return redirect("products:product_list")
    order = get_visitable_order(request, order_id)
    if order.payment_method != method:
        return redirect("orders:order_success", order_id=order.id)
    if order.is_paid:
        return redirect("orders:order_success", order_id=order.id)
    if order.status == "cancelled":
        return redirect("orders:order_failed", order_id=order.id)

    g = _gateway(method)
    if not g or not g.is_configured():
        messages.error(
            request,
            f"Vi {WALLET_LABELS[method]} chua duoc cau hinh. Vui long chon COD/chuyen khoan.",
        )
        return redirect("orders:order_success", order_id=order.id)

    return_url = request.build_absolute_uri(reverse(f"orders:{method}_return"))
    notify_url = request.build_absolute_uri(reverse(f"orders:{method}_ipn"))
    ip_addr = request.META.get("REMOTE_ADDR", "127.0.0.1")
    res = g.build_payment_request(order, ip_addr, return_url, notify_url)
    url = res.get("payUrl") or res.get("order_url") or res.get("checkout_url")
    if not url:
        messages.error(
            request,
            f"Khong tao duoc phien {WALLET_LABELS[method]}: {res.get('error', 'loi khong xac dinh')}",
        )
        return redirect("orders:order_review", order_id=order.id)
    # ponytail: luu trans id tam de doi soat return/ipn, khong can them cot
    tid = res.get("orderId") or res.get("app_trans_id") or res.get("order_id") or ""
    if tid:
        Order.objects.filter(pk=order.pk).update(gateway_transaction_id=str(tid)[:128])
    return redirect(url)


def _mark_paid(order, transaction_id: str, source: str):
    if order.is_paid:
        return False
    order.is_paid = True
    fields = ["is_paid", "updated_at"]
    if order.status == "cancelled":
        logger.error("Late %s payment for cancelled order %s", source, order.id)
    else:
        order.status = "processing"
        fields.append("status")
        from ..services.order_email import send_order_email
        from ..services.shipping.service import create_shipping_order

        send_order_email(order, event="paid")
        create_shipping_order(order)
    order._status_change_source = source
    order._status_change_transaction_id = (transaction_id or "")[:64]
    order._status_change_note = f"{source} xac nhan thanh toan."
    order.save(update_fields=fields)
    return True


@transaction.atomic
def wallet_return(request: HttpRequest, method: str) -> HttpResponse:
    if method not in WALLET_METHODS:
        return redirect("products:product_list")
    g = _gateway(method)
    params = request.GET.dict() if request.method == "GET" else request.POST.dict()
    raw_oid = (
        params.get("orderId")
        or params.get("order_id")
        or params.get("app_trans_id")
        or params.get("apptransid")
        or params.get("partner_order_id")
        or ""
    )
    order = (
        Order.objects.select_for_update()
        .filter(payment_method=method, gateway_transaction_id=str(raw_oid))
        .first()
        if raw_oid
        else None
    )
    if not order:
        messages.error(request, "Khong tim thay don hang.")
        return redirect("orders:my_orders")
    if not g.verify_callback(params):
        messages.error(request, "Chu ky thanh toan khong hop le.")
        return redirect("products:product_list")
    if not g.amount_matches(order, params):
        messages.error(request, "So tien thanh toan khong khop.")
        return redirect("orders:my_orders")
    info = g.get_transaction_info(params)
    tid = str(
        info.get("transaction_id")
        or info.get("zp_trans_id")
        or info.get("order_id")
        or ""
    )
    if order.is_paid:
        messages.info(request, "Don hang da duoc thanh toan truoc do.")
        return redirect("orders:order_success", order_id=order.id)
    if method == "zalopay" and g.is_success_callback(params):
        query = g.query_transaction(order, str(raw_oid))
        query_data = query.get("data") or {}
        if (
            not query.get("success")
            or not g.amount_matches(order, query_data)
            or not query_data.get("zp_trans_id")
        ):
            messages.info(
                request,
                "ZaloPay đang xác nhận giao dịch. Vui lòng kiểm tra lại đơn hàng.",
            )
            return redirect("orders:order_success", order_id=order.id)
        tid = str(query_data["zp_trans_id"])
    if g.is_success_callback(params):
        _mark_paid(order, tid, f"{method}_return")
        log_activity(
            request,
            event_type="payment_confirm",
            metadata={"order_id": order.id, "payment_method": method},
        )
        messages.success(request, f"Thanh toan {WALLET_LABELS[method]} thanh cong.")
        return redirect("orders:order_success", order_id=order.id)
    if order.status != "cancelled":
        restore_order_stock(order)
        order.status = "cancelled"
        order.save(update_fields=["status", "updated_at"])
    return redirect("orders:order_failed", order_id=order.id)


@csrf_exempt
@transaction.atomic
def wallet_ipn(request: HttpRequest, method: str) -> HttpResponse:
    if method not in WALLET_METHODS:
        return JsonResponse({"return_code": -1, "message": "unsupported"})
    g = _gateway(method)
    try:
        import json

        data = (
            json.loads(request.body.decode() or "{}")
            if request.body
            else request.POST.dict()
        )
    except Exception:
        data = request.POST.dict()
    if not isinstance(data, dict):
        return JsonResponse({"return_code": -1, "message": "invalid payload"})
    if not g.verify_callback(data):
        return JsonResponse({"return_code": -1, "message": "invalid signature"})
    if method == "zalopay":
        data = g.callback_payload(data)
    raw_oid = (
        data.get("orderId")
        or data.get("order_id")
        or data.get("app_trans_id")
        or data.get("partner_order_id")
        or ""
    )
    order = (
        Order.objects.select_for_update()
        .filter(payment_method=method, gateway_transaction_id=str(raw_oid))
        .first()
        if raw_oid
        else None
    )
    if not order:
        return JsonResponse({"return_code": 0, "message": "order not found"})
    if not g.amount_matches(order, data):
        return JsonResponse({"return_code": -1, "message": "mismatch"})
    if order.is_paid:
        return JsonResponse(
            {
                "return_code": 1 if method == "zalopay" else 0,
                "message": "already confirmed",
            }
        )
    info = g.get_transaction_info(data)
    tid = str(
        info.get("transaction_id")
        or info.get("zp_trans_id")
        or info.get("order_id")
        or ""
    )
    if not g.is_success_callback(data):
        if order.status != "cancelled":
            restore_order_stock(order)
            order.status = "cancelled"
            order.save(update_fields=["status", "updated_at"])
        return JsonResponse({"return_code": 0, "message": "payment failed"})
    _mark_paid(order, tid, f"{method}_ipn")
    return JsonResponse(
        {"return_code": 1 if method == "zalopay" else 0, "message": "confirm success"}
    )
