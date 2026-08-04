import csv

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpRequest, HttpResponse

from ..models import Order


@login_required
def admin_export_orders(request: HttpRequest) -> HttpResponse:
    if not request.user.is_staff:
        raise Http404

    status = request.GET.get("status", "")
    orders = Order.objects.all().prefetch_related("items__product", "items__variant").order_by("-created_at")
    if status and status in dict(Order.STATUS_CHOICES):
        orders = orders.filter(status=status)

    response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
    response["Content-Disposition"] = "attachment; filename=don-hang.csv"
    writer = csv.writer(response)
    writer.writerow(["Mã ĐH", "Khách hàng", "Email", "SĐT", "Địa chỉ", "PT thanh toán", "Ngân hàng", "Đã thanh toán", "Trạng thái", "Tiền hàng", "Phí ship", "Giảm giá", "Tổng cộng", "Ghi chú", "Ngày tạo"])
    for o in orders:
        writer.writerow([
            o.id, o.customer_name, o.customer_email, o.phone, o.shipping_address,
            o.get_payment_method_display(), o.bank_code, "Có" if o.is_paid else "Không",
            o.get_status_display(), o.subtotal_amount, o.shipping_fee, o.discount_amount,
            o.total_amount, o.note, o.created_at.strftime("%d/%m/%Y %H:%M"),
        ])
    return response
