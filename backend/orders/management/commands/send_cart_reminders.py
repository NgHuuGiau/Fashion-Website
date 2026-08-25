import logging

from django.core.management.base import BaseCommand
from django.utils import timezone

from orders.models import CartReminder
from orders.services.cart_email import send_cart_reminder

logger = logging.getLogger(__name__)

REMINDER_HOURS = 3


class Command(BaseCommand):
    help = "Gửi email nhắc giỏ hàng bỏ quên (>3h chưa checkout)."

    def handle(self, *args, **options):
        cutoff = timezone.now() - timezone.timedelta(hours=REMINDER_HOURS)
        rows = CartReminder.objects.filter(
            reminded_at__isnull=True, updated_at__lt=cutoff
        ).exclude(email="")
        sent = 0
        for row in rows:
            if send_cart_reminder(row, fail_silently=False):
                row.reminded_at = timezone.now()
                row.save(update_fields=["reminded_at"])
                sent += 1
        self.stdout.write(self.style.SUCCESS(f"Đã gửi {sent}/{rows.count()} email nhắc giỏ hàng."))
