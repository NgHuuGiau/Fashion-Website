from django.conf import settings
from django.core.management.base import CommandError


def refuse_demo_seed_in_production():
    if not settings.DEBUG:
        raise CommandError(
            "Từ chối lệnh dữ liệu demo khi DEBUG=False; không ghi dữ liệu mẫu vào production."
        )
