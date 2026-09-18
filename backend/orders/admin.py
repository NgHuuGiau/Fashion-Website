from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import (
    CartReminder,
    Coupon,
    CouponRedemption,
    Order,
    OrderItem,
    OrderStatusHistory,
    RefundRecord,
    ReturnRequest,
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
