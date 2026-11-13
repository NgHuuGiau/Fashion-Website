"""
Payment and Refund models for Fashion-Website
Ported from ElectroHub - adapted for Django ORM
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class Payment(models.Model):
    """Payment record for an order"""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("refund_pending", "Refund Pending"),
        ("refunded", "Refunded"),
    ]

    PROVIDER_CHOICES = [
        ("mock", "Mock (Simulation)"),
        ("vnpay", "VNPAY"),
        ("paypal", "PayPal"),
        ("cod", "Cash on Delivery"),
        ("bank_transfer", "Bank Transfer"),
    ]

    id = models.BigAutoField(primary_key=True)
    order = models.OneToOneField(
        "orders.Order", on_delete=models.CASCADE, related_name="payment"
    )
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, default="mock")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    amount_minor = models.BigIntegerField(
        default=0
    )  # Amount in minor units (VND * 100, USD cents)
    currency = models.CharField(max_length=3, default="VND")
    txn_ref = models.CharField(
        max_length=64, blank=True, default=""
    )  # Provider transaction reference
    provider_txn_id = models.CharField(
        max_length=128, blank=True, default=""
    )  # Provider's transaction ID
    provider_status = models.CharField(max_length=32, blank=True, default="")
    attempt = models.PositiveIntegerField(default=1)
    raw_payload = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orders_payment"
        indexes = [
            models.Index(fields=["provider", "status"]),
            models.Index(fields=["txn_ref"]),
        ]

    def __str__(self):
        return f"Payment #{self.id} - {self.provider} - {self.status}"


class Refund(models.Model):
    """Refund request for a payment"""

    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("processing", "Processing"),
        ("succeeded", "Succeeded"),
        ("failed", "Failed"),
        ("rejected", "Rejected"),
    ]

    id = models.BigAutoField(primary_key=True)
    payment = models.ForeignKey(
        Payment, on_delete=models.CASCADE, related_name="refunds"
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="requested_refunds",
    )
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="confirmed_refunds",
    )
    amount_minor = models.BigIntegerField()
    currency = models.CharField(max_length=3, default="VND")
    reason = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="scheduled"
    )
    due_at = models.DateTimeField()  # When refund can be processed (for holding period)
    provider_refund_id = models.CharField(max_length=128, blank=True, default="")
    raw_payload = models.JSONField(null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orders_refund"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["payment", "status"]),
            models.Index(fields=["due_at"]),
        ]

    def __str__(self):
        return (
            f"Refund #{self.id} - {self.status} - {self.amount_minor} {self.currency}"
        )
