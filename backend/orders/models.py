from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone



class Coupon(models.Model):
    TYPE_PERCENT = "percent"
    TYPE_FIXED = "fixed"
    TYPE_FREESHIP = "freeship"

    DISCOUNT_TYPE_CHOICES = [
        (TYPE_PERCENT, "Giảm theo phần trăm"),
        (TYPE_FIXED, "Giảm số tiền cố định"),
        (TYPE_FREESHIP, "Miễn phí vận chuyển"),
    ]

    code = models.CharField(max_length=30, unique=True, db_index=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default=TYPE_PERCENT)
    value = models.DecimalField(max_digits=10, decimal_places=0, default=Decimal("0"))
    min_order_amount = models.DecimalField(max_digits=12, decimal_places=0, default=Decimal("0"))
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    starts_at = models.DateTimeField(null=True, blank=True, db_index=True)
    ends_at = models.DateTimeField(null=True, blank=True, db_index=True)
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    max_uses_per_user = models.PositiveIntegerField(null=True, blank=True, verbose_name="Giới hạn mỗi người")
    used_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ["code"]

    def __str__(self):
        return self.code


    def is_usable_now(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if self.starts_at and now < self.starts_at:
            return False
        if self.ends_at and now > self.ends_at:
            return False
        if self.usage_limit is not None and self.used_count >= self.usage_limit:
            return False
        return True


    def is_usable_by_user(self, user):
        if not user or not user.is_authenticated:
            return True
        if self.max_uses_per_user is None:
            return True
        used = self.redemptions.filter(user=user).count()
        return used < self.max_uses_per_user


class CouponRedemption(models.Model):
    coupon = models.ForeignKey(Coupon, related_name="redemptions", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="coupon_redemptions", on_delete=models.CASCADE)
    order = models.ForeignKey("orders.Order", null=True, blank=True, on_delete=models.SET_NULL, related_name="coupon_redemptions")
    used_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Lượt dùng mã giảm giá"
        verbose_name_plural = "Lượt dùng mã giảm giá"
        ordering = ["-used_at"]

    def __str__(self):
        return f"{self.coupon.code} - {self.user}"



class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Chờ xử lý"),
        ("processing", "Đang xử lý"),
        ("shipping", "Đang giao"),
        ("delivered", "Hoàn thành"),
        ("cancelled", "Đã hủy"),
    ]

    PAYMENT_METHOD_CHOICES = [
        ("cod", "Thanh toán khi nhận hàng"),
        ("bank", "Chuyển khoản ngân hàng"),
        ("vnpay", "Thanh toán VNPay"),
    ]

    CARRIER_CHOICES = [
        ("ghn", "GHN"),
        ("ghtk", "GHTK"),
        ("vnpost", "VNPost"),
    ]
    CARRIER_LABELS = dict(CARRIER_CHOICES)
    TRACKING_BASE_URL = {
        "ghn": "https://donhang.ghn.vn/?order_code={code}",
        "ghtk": "https://i.giaohangtietkiem.vn/ma-don-hang?code={code}",
        "vnpost": "https://www.vnpost.vn/vi-vn/tra-cuu/tra-cuu-hang",
    }

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    customer_name = models.CharField(max_length=150)
    customer_email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, db_index=True)
    shipping_address = models.TextField()
    note = models.TextField(blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default="cod", db_index=True)
    bank_code = models.CharField(max_length=20, blank=True)
    is_paid = models.BooleanField(default=False, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True)
    carrier = models.CharField(max_length=20, choices=CARRIER_CHOICES, blank=True, verbose_name="Đơn vị vận chuyển")
    tracking_code = models.CharField(max_length=40, blank=True, verbose_name="Mã vận đơn")

    subtotal_amount = models.DecimalField(max_digits=12, decimal_places=0, default=Decimal("0"))
    shipping_fee = models.DecimalField(max_digits=12, decimal_places=0, default=Decimal("0"))
    discount_amount = models.DecimalField(max_digits=12, decimal_places=0, default=Decimal("0"))
    points_used = models.PositiveIntegerField(default=0, verbose_name="Điểm đã dùng")
    points_earned = models.PositiveIntegerField(default=0, verbose_name="Điểm tích được")
    coupon = models.ForeignKey("orders.Coupon", null=True, blank=True, on_delete=models.SET_NULL, related_name="orders")
    coupon_code = models.CharField(max_length=30, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=0, default=Decimal("0"))

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["payment_method", "is_paid", "status"]),
            models.Index(fields=["phone"]),
        ]

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

    @property
    def carrier_label(self):
        return self.CARRIER_LABELS.get(self.carrier, "")

    @property
    def tracking_url(self):
        if not self.tracking_code:
            return ""
        template = self.TRACKING_BASE_URL.get(self.carrier, "")
        return template.format(code=self.tracking_code) if template else ""

    @property
    def can_request_return(self):
        if self.status != "delivered":
            return False
        if self.return_requests.filter(status__in=["pending", "approved"]).exists():
            return False
        return True


class ReturnRequest(models.Model):
    RETURN_TYPE_CHOICES = [
        ("refund", "Hoàn tiền"),
        ("exchange", "Đổi hàng / đổi size"),
    ]
    REASON_CHOICES = [
        ("wrong_size", "Sai size, không vừa"),
        ("not_like", "Không ưng kiểu dáng"),
        ("defective", "Lỗi sản phẩm"),
        ("wrong_item", "Giao nhầm sản phẩm"),
        ("other", "Lý do khác"),
    ]
    STATUS_CHOICES = [
        ("pending", "Chờ duyệt"),
        ("approved", "Đã duyệt"),
        ("rejected", "Từ chối"),
        ("refunded", "Đã hoàn tiền"),
    ]
    STATUS_LABELS = dict(STATUS_CHOICES)
    REASON_LABELS = dict(REASON_CHOICES)
    RETURN_TYPE_LABELS = dict(RETURN_TYPE_CHOICES)

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="return_requests")
    return_type = models.CharField(max_length=20, choices=RETURN_TYPE_CHOICES, default="refund")
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    items = models.JSONField(default=list)
    refund_amount = models.DecimalField(max_digits=12, decimal_places=0, default=Decimal("0"))
    note = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Đổi trả #{self.id} - {self.order}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name="order_items")
    variant = models.ForeignKey("products.ProductVariant", on_delete=models.SET_NULL, null=True, blank=True)
    selected_color = models.CharField(max_length=50, blank=True)
    selected_size = models.CharField(max_length=20, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=0)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


    def subtotal(self):
        return self.price * self.quantity
