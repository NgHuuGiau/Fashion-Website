import logging
import sys

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings

from orders.models import CartReminder
from orders.services.cart_email import send_cart_reminder

logger = logging.getLogger(__name__)

REMINDER_HOURS = 3


class Command(BaseCommand):
    help = "Gửi email nhắc giỏ hàng bỏ quên (>3h chưa checkout)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Chỉ mô phỏng, không thực sự gửi email.",
        )
        parser.add_argument(
            "--no-input",
            action="store_true",
            help="Không hỏi xác nhận, chạy tự động (dùng cho CI/CD).",
        )

    def handle(self, *args, **options):
        dry_run = options.get("dry_run", False)
        no_input = options.get("no_input", False)

        # Tự động bỏ qua xác nhận nếu chạy trong môi trường test
        is_interactive = (
            sys.stdin.isatty()
            and "test" not in sys.argv
            and not getattr(settings, "TESTING", False)
        )

        if not dry_run and not no_input and is_interactive:
            self.stdout.write(
                self.style.WARNING(
                    "CẢNH BÁO: Lệnh này sẽ gửi email thật. "
                    "Chạy lại với --no-input để bỏ qua xác nhận, hoặc --dry-run để mô phỏng."
                )
            )
            confirm = input("Bạn có chắc chắn muốn tiếp tục? (y/N): ").strip().lower()
            if confirm != "y":
                self.stdout.write(self.style.ERROR("Đã hủy."))
                return

        cutoff = timezone.now() - timezone.timedelta(hours=3)
        rows = CartReminder.objects.filter(
            reminded_at__isnull=True, updated_at__lt=cutoff
        ).exclude(email="")

        if dry_run:
            self.stdout.write(f"[DRY-RUN] Sẽ gửi {rows.count()} email nhắc giỏ hàng.")
            return

        sent = 0
        for row in rows:
            if send_cart_reminder(row, fail_silently=False):
                row.reminded_at = timezone.now()
                row.save(update_fields=["reminded_at"])
                sent += 1

        self.stdout.write(
            self.style.SUCCESS(f"Đã gửi {sent}/{rows.count()} email nhắc giỏ hàng.")
        )
