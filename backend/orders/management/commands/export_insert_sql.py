"""
Management command: export_insert_sql
Export toàn bộ dữ liệu hiện tại ra file 02_INSERT_DATA.sql (format SSMS).
"""

import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Export toàn bộ dữ liệu DB ra file 02_INSERT_DATA.sql (format SSMS)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            default="database/sql/02_INSERT_DATA.sql",
            help="Đường dẫn file output (relative to BASE_DIR)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Chỉ mô phỏng export, không ghi file.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Cho phép chạy khi DEBUG=False (mặc định từ chối để tránh export nhầm production).",
        )
        parser.add_argument(
            "--no-input",
            action="store_true",
            help="Không hỏi xác nhận, chạy tự động (dùng cho CI/CD).",
        )

    def handle(self, *args, **options):
        dry_run = options.get("dry_run", False)
        force = options.get("force", False)
        no_input = options.get("no_input", False)

        if not settings.DEBUG and not force:  # noqa: F823
            raise CommandError(
                "Từ chối export khi DEBUG=False. Chạy lại với --force nếu bạn chắc chắn."
            )

        if not dry_run and not no_input:
            self.stdout.write(
                self.style.WARNING(
                    "CẢNH BÁO: Lệnh này sẽ export toàn bộ dữ liệu production. "
                    "Chạy lại với --no-input để bỏ qua xác nhận, hoặc --dry-run để mô phỏng."
                )
            )
            confirm = input("Bạn có chắc chắn muốn tiếp tục? (y/N): ").strip().lower()
            if confirm != "y":
                self.stdout.write(self.style.ERROR("Đã hủy."))
                return

        output_path = options["output"]
        if not os.path.isabs(output_path):
            from django.conf import settings

            output_path = os.path.join(settings.BASE_DIR, output_path)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        if dry_run:
            self.stdout.write(f"[DRY-RUN] Sẽ xuất dữ liệu ra: {output_path}")
            return

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(self._header())
            f.write(self._export_users())
            f.write(self._export_categories())
            f.write(self._export_products())
            f.write(self._export_variants())
            f.write(self._export_coupons())
            f.write(self._export_orders())
            f.write(self._export_order_items())
            f.write(self._export_wishlist())
            f.write(self._export_faqs())
            f.write(self._export_activities())
            f.write(
                "\n-- ============================================================\n"
            )
            f.write("-- END OF DATA\n")
            f.write("-- ============================================================\n")

        self.stdout.write(self.style.SUCCESS(f"Đã xuất ra: {output_path}"))
