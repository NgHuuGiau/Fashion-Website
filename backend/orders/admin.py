from django.contrib import admin

from .models import Coupon, CouponRedemption, Order, OrderItem



class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "variant", "selected_color", "selected_size", "quantity", "price")


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
        "subtotal_amount",
        "shipping_fee",
        "discount_amount",
        "total_amount",
        "created_at",
    )
    list_filter = ("status", "payment_method", "bank_code", "is_paid", "created_at")
    search_fields = ("id", "user__username", "customer_name", "phone", "coupon_code")
    inlines = [OrderItemInline]
    readonly_fields = ("created_at", "updated_at")


@admin.register(OrderItem)

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "variant", "selected_color", "selected_size", "quantity", "price")
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
