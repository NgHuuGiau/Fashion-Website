import json
import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def send_cart_reminder(reminder, fail_silently=True):
    if not settings.EMAIL_HOST or not reminder.email:
        return False
    try:
        items = json.loads(reminder.cart_snapshot) if reminder.cart_snapshot else []
    except (json.JSONDecodeError, TypeError):
        items = []
    context = {"items": items}
    try:
        html = render_to_string("emails/cart_reminder.html", context)
        subject = "Bạn chưa hoàn tất đơn hàng — HUUGIAU Studio"
        msg = EmailMultiAlternatives(
            subject=subject,
            body=subject,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[reminder.email],
        )
        msg.attach_alternative(html, "text/html")
        msg.send(fail_silently=fail_silently)
        return True
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "Không gửi được email nhắc giỏ hàng %s: %s", reminder.session_key, exc
        )
        return False
