from decimal import Decimal

from django.conf import settings
from django.db import models, transaction
from django.db.models import Sum, F
from django.utils import timezone

from datetime import timedelta as _timedelta


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
    stackable = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Được cộng dồn",
        help_text="Tắt = mã độc quyền, không cộng với giảm giá hạng và điểm.",
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
        null=True,
        blank=True,  # khách vãng lai dùng mã khuyến mãi
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
    vnpay_transaction_id = models.CharField(
        max_length=64, unique=True, null=True, blank=True
    )
    refunded_amount = models.DecimalField(
        max_digits=12, decimal_places=0, default=Decimal("0")
    )
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
    delivered_at = models.DateTimeField(null=True, blank=True, db_index=True)

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
        return f"Order #{self.id} - {self.user.username if self.user else '(guest)'}"

    def save(self, *args, **kwargs):
        update_fields = kwargs.get("update_fields")
        should_track_status = update_fields is None or "status" in update_fields
        previous_status = None
        if self.pk:
            previous_status = (
                type(self)
                .objects.using(kwargs.get("using") or self._state.db)
                .filter(pk=self.pk)
                .values_list("status", flat=True)
                .first()
            )
        super().save(*args, **kwargs)
        if not should_track_status or previous_status == self.status:
            return

        OrderStatusHistory.objects.using(self._state.db).create(
            order_id=self.pk,
            from_status=previous_status or "",
            to_status=self.status,
            actor_id=getattr(self, "_status_changed_by_id", None),
            source=getattr(self, "_status_change_source", "application"),
            transaction_id=(
                getattr(self, "_status_change_transaction_id", "")
                or self.vnpay_transaction_id
                or ""
            )[:64],
            note=getattr(self, "_status_change_note", "")[:255],
        )
        for attribute in (
            "_status_changed_by_id",
            "_status_change_source",
            "_status_change_transaction_id",
            "_status_change_note",
        ):
            if hasattr(self, attribute):
                delattr(self, attribute)

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
        if self.return_requests.exclude(status="rejected").exists():
            return False
        delivered_at = self.delivered_at or self.updated_at
        return delivered_at >= timezone.now() - _timedelta(days=7)

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
        ("received", "Đã nhận và kiểm tra hàng"),
        ("rejected", "Từ chối"),
        ("refunded", "Đã hoàn tiền"),
        ("exchanged", "Đã đổi hàng"),
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
    stock_restored_at = models.DateTimeField(null=True, blank=True)
    refund_reference = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Đổi trả #{self.id} - {self.order}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def receive_and_restock(self):
        """Ghi nhận hàng đã nhận/kiểm tra rồi mới cộng lại đúng biến thể vào kho."""
        from products.models import Product, ProductVariant

        with transaction.atomic():
            request = type(self).objects.select_for_update().get(pk=self.pk)
            if request.stock_restored_at:
                self.status = request.status
                self.stock_restored_at = request.stock_restored_at
                return self
            if request.status != "approved":
                raise ValueError("Chỉ nhận hàng sau khi yêu cầu đã được duyệt.")

            for item_data in request.items:
                order_item_id = item_data.get("order_item_id")
                quantity = item_data.get("qty")
                if not isinstance(order_item_id, int) or not isinstance(quantity, int):
                    raise ValueError(
                        "Yêu cầu cũ thiếu mã dòng hàng; cần kiểm tra thủ công, không tự cộng kho."
                    )
                order_item = (
                    OrderItem.objects.select_for_update()
                    .filter(pk=order_item_id, order_id=request.order_id)
                    .first()
                )
                if not order_item or quantity < 1 or quantity > order_item.quantity:
                    raise ValueError("Dữ liệu sản phẩm trả lại không hợp lệ.")

                if order_item.variant_id:
                    ProductVariant.objects.filter(pk=order_item.variant_id).update(
                        stock=F("stock") + quantity
                    )
                    total_stock = (
                        order_item.product.variants.filter(is_active=True).aggregate(
                            total=Sum("stock")
                        )["total"]
                        or 0
                    )
                    Product.objects.filter(pk=order_item.product_id).update(
                        stock=total_stock, updated=timezone.now()
                    )
                else:
                    Product.objects.filter(pk=order_item.product_id).update(
                        stock=F("stock") + quantity, updated=timezone.now()
                    )

            request.status = "received"
            request.stock_restored_at = timezone.now()
            request.save(update_fields=["status", "stock_restored_at", "updated_at"])
            self.status = request.status
            self.stock_restored_at = request.stock_restored_at
            return self


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="status_history"
    )
    from_status = models.CharField(max_length=20, blank=True)
    to_status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="order_status_changes",
    )
    source = models.CharField(max_length=32, default="system")
    transaction_id = models.CharField(max_length=64, blank=True)
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]
        indexes = [models.Index(fields=["order", "created_at"])]
        verbose_name = "Lịch sử trạng thái đơn hàng"
        verbose_name_plural = "Lịch sử trạng thái đơn hàng"


def record_order_status_change(
    order,
    from_status,
    *,
    actor=None,
    source="system",
    transaction_id="",
    note="",
):
    if from_status == order.status:
        return None
    return OrderStatusHistory.objects.create(
        order=order,
        from_status=from_status or "",
        to_status=order.status,
        actor=actor,
        source=source,
        transaction_id=transaction_id[:64],
        note=note[:255],
    )


class RefundRecord(models.Model):
    STATUS_CHOICES = [
        ("pending", "Đang xác nhận"),
        ("succeeded", "Đã hoàn qua cổng"),
        ("failed", "Cổng từ chối"),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="refunds")
    request_id = models.CharField(max_length=32, unique=True)
    transaction_id = models.CharField(max_length=64)
    amount = models.DecimalField(max_digits=12, decimal_places=0)
    reason = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="pending")
    gateway_code = models.CharField(max_length=20, blank=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="refund_records",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["order", "status"])]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        "products.Product", on_delete=models.PROTECT, related_name="order_items"
    )
    variant = models.ForeignKey(
        "products.ProductVariant", on_delete=models.PROTECT, null=True, blank=True
    )
    selected_color = models.CharField(max_length=50, blank=True)
    selected_size = models.CharField(max_length=20, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=0)
    # Snapshot ten SP luc dat hang; doi ten SP sau nay khong sua lich su don.
    product_name = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        return f"{self.quantity} x {self.display_name}"

    @property
    def display_name(self):
        if self.product_name:
            return self.product_name
        try:
            return self.product.name
        except Exception:
            return ""

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
            self.expires_at = timezone.now() + _timedelta(days=365)
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


class CartReminder(models.Model):
    """Giỏ hàng bỏ quên: chốt lại lần cuối khách chạm vào giỏ (theo session)."""

    session_key = models.CharField(max_length=40, unique=True, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="cart_reminders",
    )
    email = models.EmailField(blank=True)
    cart_snapshot = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    reminded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Nhắc giỏ hàng bỏ quên"
        verbose_name_plural = "Nhắc giỏ hàng bỏ quên"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"CartReminder {self.session_key} -> {self.email or '(chưa có email)'}"
