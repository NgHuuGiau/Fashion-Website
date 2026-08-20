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
    discount_type = models.CharField(
        max_length=20, choices=DISCOUNT_TYPE_CHOICES, default=TYPE_PERCENT
    )
    value = models.DecimalField(max_digits=10, decimal_places=0, default=Decimal("0"))
    min_order_amount = models.DecimalField(
        max_digits=12, decimal_places=0, default=Decimal("0")
    )
    max_discount_amount = models.DecimalField(
        max_digits=10, decimal_places=0, null=True, blank=True
    )
    is_active = models.BooleanField(default=True, db_index=True)
    starts_at = models.DateTimeField(null=True, blank=True, db_index=True)
    ends_at = models.DateTimeField(null=True, blank=True, db_index=True)
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    max_uses_per_user = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Giới hạn mỗi người"
    )
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
    coupon = models.ForeignKey(
        Coupon, related_name="redemptions", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="coupon_redemptions",
        on_delete=models.CASCADE,
    )
    order = models.ForeignKey(
        "orders.Order",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="coupon_redemptions",
    )
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

    DELIVERY_SLOT_CHOICES = [
        ("morning", "8:00 – 11:00"),
        ("afternoon", "13:00 – 17:00"),
        ("evening", "18:00 – 21:00"),
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

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    customer_name = models.CharField(max_length=150)
    customer_email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, db_index=True)
    shipping_address = models.TextField()
    note = models.TextField(blank=True)
    delivery_time_slot = models.CharField(
        max_length=20, blank=True, verbose_name="Khung giờ nhận hàng"
    )
    gift_wrap = models.BooleanField(default=False, verbose_name="Đóng gói quà tặng")
    gift_note = models.CharField(
        max_length=255, blank=True, verbose_name="Thiệp chúc kèm quà"
    )
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHOD_CHOICES, default="cod", db_index=True
    )
    bank_code = models.CharField(max_length=20, blank=True)
    is_paid = models.BooleanField(default=False, db_index=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True
    )
    carrier = models.CharField(
        max_length=20,
        choices=CARRIER_CHOICES,
        blank=True,
        verbose_name="Đơn vị vận chuyển",
    )
    tracking_code = models.CharField(
        max_length=40, blank=True, verbose_name="Mã vận đơn"
    )

    subtotal_amount = models.DecimalField(
        max_digits=12, decimal_places=0, default=Decimal("0")
    )
    shipping_fee = models.DecimalField(
        max_digits=12, decimal_places=0, default=Decimal("0")
    )
    discount_amount = models.DecimalField(
        max_digits=12, decimal_places=0, default=Decimal("0")
    )
    points_used = models.PositiveIntegerField(default=0, verbose_name="Điểm đã dùng")
    points_earned = models.PositiveIntegerField(
        default=0, verbose_name="Điểm tích được"
    )
    coupon = models.ForeignKey(
        "orders.Coupon",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="orders",
    )
    coupon_code = models.CharField(max_length=30, blank=True)
    total_amount = models.DecimalField(
        max_digits=12, decimal_places=0, default=Decimal("0")
    )

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

    def get_delivery_slot_display(self):
        return dict(self.DELIVERY_SLOT_CHOICES).get(self.delivery_time_slot, "")


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

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="return_requests"
    )
    return_type = models.CharField(
        max_length=20, choices=RETURN_TYPE_CHOICES, default="refund"
    )
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    items = models.JSONField(default=list)
    refund_amount = models.DecimalField(
        max_digits=12, decimal_places=0, default=Decimal("0")
    )
    note = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Đổi trả #{self.id} - {self.order}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        "products.Product", on_delete=models.CASCADE, related_name="order_items"
    )
    variant = models.ForeignKey(
        "products.ProductVariant", on_delete=models.SET_NULL, null=True, blank=True
    )
    selected_color = models.CharField(max_length=50, blank=True)
    selected_size = models.CharField(max_length=20, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=0)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def subtotal(self):
        return self.price * self.quantity


class GiftCard(models.Model):
    """Thẻ quà tặng - mua tặng người khác, có mã duy nhất, hạn sử dụng 1 năm"""

    code = models.CharField(
        max_length=16, unique=True, db_index=True, verbose_name="Mã thẻ"
    )
    initial_balance = models.DecimalField(
        max_digits=10, decimal_places=0, verbose_name="Giá trị ban đầu"
    )
    current_balance = models.DecimalField(
        max_digits=10, decimal_places=0, default=0, verbose_name="Số dư hiện tại"
    )
    currency = models.CharField(
        max_length=3, default="VND", verbose_name="Đơn vị tiền tệ"
    )

    purchaser = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="gift_cards_purchased",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Người mua",
    )
    purchaser_email = models.EmailField(blank=True, verbose_name="Email người mua")
    recipient_email = models.EmailField(blank=True, verbose_name="Email người nhận")
    recipient_name = models.CharField(
        max_length=150, blank=True, verbose_name="Tên người nhận"
    )
    message = models.TextField(blank=True, verbose_name="Lời nhắn")

    STATUS_CHOICES = [
        ("active", "Đang hoạt động"),
        ("redeemed", "Đã dùng hết"),
        ("expired", "Hết hạn"),
        ("cancelled", "Đã hủy"),
    ]
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="active", db_index=True
    )

    purchased_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(verbose_name="Hạn sử dụng")
    redeemed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Thẻ quà tặng"
        verbose_name_plural = "Thẻ quà tặng"
        ordering = ["-purchased_at"]

    def __str__(self):
        return f"Gift Card {self.code} - {self.initial_balance:,.0f}đ"

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_unique_code()
        if not self.current_balance:
            self.current_balance = self.initial_balance
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(days=365)
        super().save(*args, **kwargs)

    @staticmethod
    def generate_unique_code():
        """Tạo mã 12 ký tự: GC + 10 random"""
        import random
        import string

        while True:
            code = "GC" + "".join(
                random.choices(string.ascii_uppercase + string.digits, k=10)
            )
            if not GiftCard.objects.filter(code=code).exists():
                return code

    def is_valid(self):
        """Kiểm tra thẻ còn hợp lệ"""
        if self.status != "active":
            return False
        if self.current_balance <= 0:
            return False
        if self.expires_at < timezone.now():
            return False
        return True

    def redeem(self, amount, order=None):
        """Trừ số dư khi dùng"""
        if not self.is_valid():
            return False, "Thẻ không hợp lệ hoặc đã hết hạn"
        if amount > self.current_balance:
            return False, "Số dư không đủ"
        self.current_balance -= amount
        if self.current_balance == 0:
            self.status = "redeemed"
            self.redeemed_at = timezone.now()
        self.save(update_fields=["current_balance", "status", "redeemed_at"])
        GiftCardUsage.objects.create(
            gift_card=self,
            order=order,
            amount=amount,
            balance_after=self.current_balance,
        )
        return True, "Thành công"

    @property
    def is_expired(self):
        return self.expires_at < timezone.now()


class GiftCardUsage(models.Model):
    """Lịch sử sử dụng thẻ quà tặng"""

    gift_card = models.ForeignKey(
        GiftCard,
        related_name="usages",
        on_delete=models.CASCADE,
        verbose_name="Thẻ quà tặng",
    )
    order = models.ForeignKey(
        "orders.Order",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="gift_card_usages",
        verbose_name="Đơn hàng",
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=0, verbose_name="Số tiền đã dùng"
    )
    balance_after = models.DecimalField(
        max_digits=10, decimal_places=0, verbose_name="Số dư còn lại"
    )
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Lịch sử sử dụng thẻ"
        verbose_name_plural = "Lịch sử sử dụng thẻ"
        ordering = ["-used_at"]

    def __str__(self):
        return f"{self.gift_card.code} - {self.amount:,.0f}đ"
