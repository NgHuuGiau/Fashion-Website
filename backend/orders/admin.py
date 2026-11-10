from django.contrib import admin
from django.core.exceptions import ValidationError
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.urls import path, reverse
from django.utils.html import format_html

from .models import (
    CartReminder,
    Coupon,
    CouponRedemption,
    Order,
    OrderItem,
    OrderStatusHistory,
    RefundRecord,
    ReturnRequest,
    ShippingOrder,
)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        "product",
        "variant",
        "selected_color",
        "selected_size",
        "quantity",
        "price",
    )


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    can_delete = False
    readonly_fields = tuple(field.name for field in OrderStatusHistory._meta.fields)

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "customer_name",
        "status",
        "payment_method",
        "bank_code",
        "coupon_code",
        "is_paid",
        "vnpay_transaction_id",
        "refunded_amount",
        "subtotal_amount",
        "shipping_fee",
        "discount_amount",
        "total_amount",
        "created_at",
    )
    list_filter = ("status", "payment_method", "bank_code", "is_paid", "created_at")
    search_fields = ("id", "user__username", "customer_name", "phone", "coupon_code")
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    readonly_fields = (
        "created_at",
        "updated_at",
        "status",
        "is_paid",
        "delivered_at",
        "vnpay_transaction_id",
        "refunded_amount",
    )

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        fields = list(self.readonly_fields)
        if obj and obj.payment_method == "bank" and not obj.is_paid:
            fields.append("reconciliation_checklist")
        return fields

    def reconciliation_checklist(self, obj):
        # ponytail: checklist tĩnh cho đối soát tay, tự động hoá khi có IPN ngân hàng
        return format_html(
            "<ol>"
            "<li>Mở app ngân hàng, tìm giao dịch tới STK shop đúng số tiền <b>{}</b>.</li>"
            "<li>Khách báo đã chuyển KHÔNG phải bằng chứng — chỉ tick khi tiền đã vào.</li>"
            "<li>Xong thì đánh dấu đã thanh toán ở form trạng thái đơn (dashboard).</li>"
            "</ol>",
            obj.total_amount,
        )

    reconciliation_checklist.short_description = "Checklist đối soát chuyển khoản"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "product",
        "variant",
        "selected_color",
        "selected_size",
        "quantity",
        "price",
    )
    list_filter = ("order__status",)
    search_fields = ("order__id", "product__name")


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "discount_type",
        "value",
        "min_order_amount",
        "max_discount_amount",
        "is_active",
        "usage_limit",
        "max_uses_per_user",
        "used_count",
        "starts_at",
        "ends_at",
    )
    list_filter = ("discount_type", "is_active")
    search_fields = ("code",)


@admin.register(CouponRedemption)
class CouponRedemptionAdmin(admin.ModelAdmin):
    list_display = ("coupon", "user", "order", "used_at")
    list_filter = ("used_at",)
    search_fields = ("coupon__code", "user__username", "order__id")


@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "return_type",
        "reason",
        "refund_amount",
        "status",
        "created_at",
    )
    list_filter = ("status", "return_type", "reason")
    search_fields = ("order__id", "order__customer_name", "order__phone")
    readonly_fields = ("stock_restored_at", "created_at", "updated_at")

    def save_model(self, request, obj, form, change):
        if change:
            old = ReturnRequest.objects.get(pk=obj.pk)
            if obj.status != old.status:
                transitions = {
                    "pending": {"approved", "rejected"},
                    "approved": {"received"},
                    "received": {"refunded", "exchanged"},
                }
                if obj.status not in transitions.get(old.status, set()):
                    raise ValidationError("Trạng thái đổi trả không hợp lệ.")
                if obj.status == "received":
                    try:
                        obj.receive_and_restock()
                    except ValueError as exc:
                        raise ValidationError(str(exc)) from exc
                    return
                if obj.status == "refunded":
                    if not obj.refund_reference.strip():
                        raise ValidationError(
                            "Cần mã giao dịch/tham chiếu hoàn tiền thực tế trước khi xác nhận."
                        )
                    if (
                        obj.order.payment_method == "vnpay"
                        and obj.order.refunded_amount < obj.refund_amount
                    ):
                        raise ValidationError(
                            "VNPay chưa xác nhận đủ số tiền hoàn cho đơn hàng này."
                        )
        super().save_model(request, obj, form, change)


@admin.register(RefundRecord)
class RefundRecordAdmin(admin.ModelAdmin):
    list_display = (
        "request_id",
        "order",
        "amount",
        "status",
        "transaction_id",
        "requested_by",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("request_id", "transaction_id", "order__id")
    readonly_fields = tuple(field.name for field in RefundRecord._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(CartReminder)
class CartReminderAdmin(admin.ModelAdmin):
    list_display = ("session_key", "user", "email", "updated_at", "reminded_at")
    search_fields = ("email", "session_key", "user__username")
    list_filter = ("reminded_at",)


@admin.register(ShippingOrder)
class ShippingOrderAdmin(admin.ModelAdmin):
    exclude = ("shipping_label_pdf",)
    list_display = (
        "id",
        "order",
        "carrier",
        "carrier_order_code",
        "tracking_code",
        "status",
        "actual_fee",
        "cod_amount",
        "created_at",
    )
    list_filter = ("carrier", "status", "created_at")
    search_fields = (
        "carrier_order_code",
        "tracking_code",
        "order__id",
        "order__customer_name",
        "order__phone",
    )
    readonly_fields = (
        "order",
        "carrier",
        "carrier_order_code",
        "tracking_code",
        "shipping_label_download",
        "actual_fee",
        "cod_amount",
        "status",
        "raw_response",
        "error_message",
        "created_at",
        "updated_at",
        "picked_up_at",
        "delivered_at",
    )
    actions = [
        "create_shipping_order_action",
        "print_shipping_label_action",
        "cancel_shipping_order_action",
        "sync_status_action",
    ]

    def get_urls(self):
        return [
            path(
                "<int:object_id>/label/",
                self.admin_site.admin_view(self.download_label),
                name="orders_shippingorder_label",
            ),
            *super().get_urls(),
        ]

    @admin.display(description="Tem vận đơn")
    def shipping_label_download(self, obj):
        if not obj or not obj.shipping_label_pdf:
            return "Chưa có tem"
        return format_html(
            '<a href="{}">Tải tem PDF</a>',
            reverse("admin:orders_shippingorder_label", args=[obj.pk]),
        )

    def download_label(self, request, object_id):
        obj = get_object_or_404(ShippingOrder, pk=object_id)
        if (
            not self.has_view_or_change_permission(request, obj)
            or not obj.shipping_label_pdf
        ):
            raise Http404
        try:
            return FileResponse(
                obj.shipping_label_pdf.open("rb"),
                as_attachment=True,
                filename=f"label_{obj.carrier_order_code}.pdf",
                content_type="application/pdf",
            )
        except FileNotFoundError as exc:
            raise Http404 from exc

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description="Tạo đơn vận chuyển (GHN)")
    def create_shipping_order_action(self, request, queryset):
        from .services.shipping.service import create_shipping_order

        success = 0
        for shipping_order in queryset:
            if shipping_order.status != "created" and shipping_order.status != "failed":
                self.message_user(
                    request,
                    f"#{shipping_order.id}: Chỉ tạo được cho đơn mới/failed",
                    level="warning",
                )
                continue
            order = shipping_order.order
            if not order.carrier:
                order.carrier = "ghn"
                order.save(update_fields=["carrier"])
            try:
                result = create_shipping_order(order)
                if result and result.status != "failed":
                    success += 1
                else:
                    self.message_user(
                        request,
                        f"#{order.id}: {result.error_message if result else 'Unknown error'}",
                        level="error",
                    )
            except Exception as e:
                self.message_user(request, f"#{order.id}: {e}", level="error")
        self.message_user(request, f"Đã tạo {success}/{len(queryset)} đơn vận chuyển.")

    @admin.action(description="In tem vận đơn (GHN)")
    def print_shipping_label_action(self, request, queryset):
        from .services.shipping.service import print_shipping_label

        success = 0
        for shipping_order in queryset:
            if not shipping_order.carrier_order_code:
                self.message_user(
                    request,
                    f"#{shipping_order.id}: Chưa có mã đơn carrier",
                    level="warning",
                )
                continue
            try:
                pdf_bytes = print_shipping_label(shipping_order)
                if pdf_bytes:
                    success += 1
                else:
                    self.message_user(
                        request,
                        f"#{shipping_order.id}: Không lấy được PDF",
                        level="error",
                    )
            except Exception as e:
                self.message_user(request, f"#{shipping_order.id}: {e}", level="error")
        self.message_user(request, f"Đã in {success}/{len(queryset)} tem.")

    @admin.action(description="Hủy đơn vận chuyển (GHN)")
    def cancel_shipping_order_action(self, request, queryset):
        from .services.shipping.service import cancel_shipping_order

        success = 0
        for shipping_order in queryset:
            if shipping_order.status in ["delivered", "cancelled"]:
                self.message_user(
                    request,
                    f"#{shipping_order.id}: Không thể hủy đơn đã giao/đã hủy",
                    level="warning",
                )
                continue
            if cancel_shipping_order(shipping_order):
                success += 1
            else:
                self.message_user(
                    request, f"#{shipping_order.id}: Hủy thất bại", level="error"
                )
        self.message_user(request, f"Đã hủy {success}/{len(queryset)} đơn.")

    @admin.action(description="Đồng bộ trạng thái từ carrier")
    def sync_status_action(self, request, queryset):
        from .services.shipping.service import sync_shipping_status

        success = 0
        for shipping_order in queryset:
            if sync_shipping_status(shipping_order):
                success += 1
            else:
                self.message_user(
                    request, f"#{shipping_order.id}: Sync thất bại", level="error"
                )
        self.message_user(request, f"Đã đồng bộ {success}/{len(queryset)} đơn.")
