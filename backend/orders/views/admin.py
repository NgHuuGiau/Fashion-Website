import csv
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from users.permissions import is_staff_member

from ..constants import BANKS, SHOP_ACCOUNT_NAME, SHOP_BANK_ACCOUNT
from ..models import Order


@login_required
def print_invoice(request: HttpRequest, order_id) -> HttpResponse:
    if not is_staff_member(request.user):
        raise Http404
    order = get_object_or_404(
        Order.objects.prefetch_related("items__product", "items__variant"), id=order_id
    )
    bank_name = (BANKS.get(order.bank_code) or {}).get("name", "")
    context = {
        "order": order,
        "bank_name": bank_name,
        "shop_bank_account": SHOP_BANK_ACCOUNT,
        "shop_account_name": SHOP_ACCOUNT_NAME,
    }
    return render(request, "admin/invoice_print.html", context)


@login_required
def admin_export_orders(request: HttpRequest) -> HttpResponse:
    if not is_staff_member(request.user):
        raise Http404

    status = request.GET.get("status", "")
    orders = (
        Order.objects.all()
        .prefetch_related("items__product", "items__variant")
        .order_by("-created_at")
    )
    if status and status in dict(Order.STATUS_CHOICES):
        orders = orders.filter(status=status)

    response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
    response["Content-Disposition"] = "attachment; filename=don-hang.csv"
    writer = csv.writer(response)
    writer.writerow(
        [
            "Mã ĐH",
            "Khách hàng",
            "Email",
            "SĐT",
            "Địa chỉ",
            "PT thanh toán",
            "Ngân hàng",
            "Đã thanh toán",
            "Trạng thái",
            "Tiền hàng",
            "Phí ship",
            "Giảm giá",
            "Tổng cộng",
            "Ghi chú",
            "Ngày tạo",
        ]
    )
    for o in orders:
        writer.writerow(
            [
                o.id,
                o.customer_name,
                o.customer_email,
                o.phone,
                o.shipping_address,
                o.get_payment_method_display(),
                o.bank_code,
                "Có" if o.is_paid else "Không",
                o.get_status_display(),
                o.subtotal_amount,
                o.shipping_fee,
                o.discount_amount,
                o.total_amount,
                o.note,
                o.created_at.strftime("%d/%m/%Y %H:%M"),
            ]
        )
    return response


@login_required
def admin_export_revenue(request: HttpRequest) -> HttpResponse:
    if not is_staff_member(request.user):
        raise Http404

    today = timezone.localdate()
    month_agg = (
        Order.objects.filter(status="delivered")
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(revenue=Sum("total_amount"), orders_count=Count("id"))
        .order_by("-month")
    )
    revenue_by_month: dict = {}
    for item in month_agg:
        if item["month"] is None:
            continue
        revenue_by_month[item["month"].strftime("%Y-%m")] = {
            "revenue": int(item["revenue"] or 0),
            "orders_count": int(item["orders_count"] or 0),
        }

    response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
    response["Content-Disposition"] = "attachment; filename=bao-cao-doanh-thu.csv"
    writer = csv.writer(response)
    writer.writerow(["Tháng", "Doanh thu (VND)", "Số đơn hoàn thành"])
    for offset in range(11, -1, -1):
        cursor = (today.replace(day=1) - timedelta(days=offset * 31)).replace(day=1)
        key = cursor.strftime("%Y-%m")
        row = revenue_by_month.get(key, {"revenue": 0, "orders_count": 0})
        writer.writerow(
            [f"{cursor.month}/{cursor.year}", row["revenue"], row["orders_count"]]
        )
    return response
