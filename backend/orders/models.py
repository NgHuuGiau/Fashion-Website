from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone



# ----------------------------
# | KHỐI LỚP (CLASS): COUPON |
# ----------------------------
class Coupon(models.Model):
    TYPE_PERCENT = "percent"
    TYPE_FIXED = "fixed"
    TYPE_FREESHIP = "freeship"

    DISCOUNT_TYPE_CHOICES = [
        (TYPE_PERCENT, "Giảm theo phần trăm"),
        (TYPE_FIXED, "Giảm số tiền cố định"),
        (TYPE_FREESHIP, "Miễn phí vận chuyển"),
    ]

    code = models.CharField(max_length=30, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default=TYPE_PERCENT)
    value = models.DecimalField(max_digits=10, decimal_places=0, default=Decimal("0"))
    min_order_amount = models.DecimalField(max_digits=12, decimal_places=0, default=Decimal("0"))
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    # --------------------------
    # | KHỐI LỚP (CLASS): META |
    # --------------------------
    class Meta:
        ordering = ["code"]

    def __str__(self):
        return self.code


    # ---------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): IS_USABLE_NOW |
    # ---------------------------------------
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



# ---------------------------
# | KHỐI LỚP (CLASS): ORDER |
# ---------------------------
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
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    customer_name = models.CharField(max_length=150)
    customer_email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20)
    shipping_address = models.TextField()
    note = models.TextField(blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default="cod")
    bank_code = models.CharField(max_length=20, blank=True)
    is_paid = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    subtotal_amount = models.DecimalField(max_digits=12, decimal_places=0, default=Decimal("0"))
    shipping_fee = models.DecimalField(max_digits=12, decimal_places=0, default=Decimal("0"))
    discount_amount = models.DecimalField(max_digits=12, decimal_places=0, default=Decimal("0"))
    coupon = models.ForeignKey("orders.Coupon", null=True, blank=True, on_delete=models.SET_NULL, related_name="orders")
    coupon_code = models.CharField(max_length=30, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=0, default=Decimal("0"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    # --------------------------
    # | KHỐI LỚP (CLASS): META |
    # --------------------------
    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"



# -------------------------------
# | KHỐI LỚP (CLASS): ORDERITEM |
# -------------------------------
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


    # ----------------------------------
    # | HÀM XỬ LÝ (FUNCTION): SUBTOTAL |
    # ----------------------------------
    def subtotal(self):
        return self.price * self.quantity
