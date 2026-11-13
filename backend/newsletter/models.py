"""
Newsletter/Email Marketing models for Fashion-Website
Ported from ElectroHub - adapted for Fashion-Website
"""

import hashlib
import hmac
from django.db import models
from django.conf import settings
from django.utils import timezone


class NewsletterSubscriber(models.Model):
    """Email subscriber for marketing campaigns"""

    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(default=timezone.now)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    source = models.CharField(
        max_length=50, default="website"
    )  # website, checkout, admin

    class Meta:
        db_table = "newsletter_subscriber"
        ordering = ["-subscribed_at"]

    def __str__(self):
        return self.email


class EmailCampaign(models.Model):
    """Email marketing campaign"""

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("sending", "Sending"),
        ("sent", "Sent"),
        ("failed", "Failed"),
    ]

    name = models.CharField(max_length=200)
    subject = models.CharField(max_length=200)
    body = models.TextField()
    template_id = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    recipient_count = models.PositiveIntegerField(default=0)
    sent_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_campaigns",
    )
    created_at = models.DateTimeField(default=timezone.now)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "newsletter_campaign"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class EmailTemplate(models.Model):
    """Predefined email templates"""

    TEMPLATE_CHOICES = [
        ("welcome", "Welcome Email"),
        ("flash_sale", "Flash Sale"),
        ("new_arrival", "New Arrival"),
        ("voucher_gift", "Voucher Gift"),
        ("store_notice", "Store Notice"),
    ]

    template_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=200)
    body = models.TextField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "newsletter_template"

    def __str__(self):
        return self.name


def generate_unsubscribe_token(email: str) -> str:
    """Generate HMAC token for unsubscribe link"""
    secret = settings.SECRET_KEY.encode()
    signature = hmac.new(secret, email.encode(), hashlib.sha256).hexdigest()
    return f"{email}|{signature}"


def verify_unsubscribe_token(token: str) -> tuple[str, bool]:
    """Verify unsubscribe token"""
    try:
        email, signature = token.rsplit("|", 1)
        expected = generate_unsubscribe_token(email).rsplit("|", 1)[1]
        return email, hmac.compare_digest(signature, expected)
    except (ValueError, IndexError):
        return "", False
