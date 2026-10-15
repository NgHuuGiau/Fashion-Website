"""Celery tasks for orders app."""

import logging
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.management import call_command
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def send_cart_reminders(self):
    """Gửi email nhắc giỏ hàng bị bỏ (chạy hàng giờ)."""
    try:
        call_command("send_cart_reminders", no_input=True)
        return {"status": "completed"}
    except Exception as exc:
        logger.error(f"send_cart_reminders failed: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def daily_reconciliation(self):
    """Đối soát hàng ngày: kiểm tra tính nhất quán dữ liệu."""
    from orders.models import Order

    try:
        logger.info("Starting daily reconciliation...")

        issues = []
        today = timezone.now().date()

        # 1. Kiểm tra đơn hàng delivered chưa có points
        delivered_orders = Order.objects.filter(
            status="delivered",
            updated_at__date=today,
        ).select_related("user", "user__userprofile")

        for order in delivered_orders:
            if hasattr(order.user, "userprofile"):
                expected_points = int(order.total_amount // 10)
                if order.points_earned != expected_points:
                    issues.append(
                        f"Order {order.id}: points_earned={order.points_earned}, expected={expected_points}"
                    )

        # 2. Kiểm tra stock consistency
        from products.models import ProductVariant
        from django.db.models import Sum

        for variant in ProductVariant.objects.filter(is_active=True).select_related(
            "product"
        ):
            total_stock = (
                ProductVariant.objects.filter(
                    product=variant.product, is_active=True
                ).aggregate(total=Sum("stock"))["total"]
                or 0
            )

            if variant.product.stock != total_stock:
                issues.append(
                    f"Product {variant.product.id} stock mismatch: "
                    f"product={variant.product.stock}, variants_sum={total_stock}"
                )

        # 3. Kiểm tra đơn hàng cancelled vẫn còn stock reserved
        cancelled_orders = Order.objects.filter(status="cancelled")
        for order in cancelled_orders:
            for item in order.items.all():
                if item.variant:
                    if item.variant.stock < item.quantity:
                        issues.append(
                            f"Order {order.id}: variant {item.variant_id} stock inconsistency"
                        )

        if issues:
            logger.warning(f"Reconciliation found {len(issues)} issues: {issues}")
            # Gửi email cảnh báo cho admin
            from django.core.mail import send_mail

            send_mail(
                f"[Reconciliation] Found {len(issues)} issues",
                "\n".join(issues),
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL] if hasattr(settings, "ADMIN_EMAIL") else [],
                fail_silently=True,
            )
        else:
            logger.info("Daily reconciliation completed - no issues found")

        return {"issues_count": len(issues), "issues": issues[:10]}

    except Exception as exc:
        logger.error(f"daily_reconciliation failed: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def notify_low_stock(self):
    """Mail ngay cho shop khi co SP sap het/het hang (chay moi sang)."""
    from products.models import Product

    try:
        if not settings.EMAIL_HOST or not settings.SUPPORT_EMAIL:
            return {"status": "skipped_no_mail_config"}
        low = list(
            Product.objects.filter(available=True, stock__lte=10)
            .order_by("stock", "name")
            .values_list("id", "name", "stock")[:20]
        )
        out = list(
            Product.objects.filter(available=True, stock=0)
            .order_by("name")
            .values_list("id", "name")[:20]
        )
        if not low and not out:
            return {"status": "ok_empty"}
        from django.core.mail import send_mail

        lines = [f"HET HANG #{pid} {name}" for pid, name in out]
        lines += [f"SAP HET #{pid} {name} (ton {stock})" for pid, name, stock in low]
        send_mail(
            "[HUUGIAU] Canh bao ton kho",
            "\n".join(lines),
            settings.DEFAULT_FROM_EMAIL,
            [settings.SUPPORT_EMAIL],
            fail_silently=True,
        )
        return {"status": "sent", "lines": len(lines)}
    except Exception as exc:
        logger.error(f"notify_low_stock failed: {exc}")
        raise self.retry(exc=exc)


@shared_task
def health_check():
    """Health check task for monitoring."""
    from django.db import connection
    from django.core.cache import cache

    checks = {}
    healthy = True

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {e}"
        healthy = False

    try:
        cache.set("healthcheck", "ok", 10)
        if cache.get("healthcheck") == "ok":
            checks["cache"] = "ok"
        else:
            checks["cache"] = "error: get failed"
            healthy = False
    except Exception as e:
        checks["cache"] = f"error: {e}"
        healthy = False

    return {
        "healthy": healthy,
        "checks": checks,
        "timestamp": timezone.now().isoformat(),
    }


@shared_task
def cleanup_sessions():
    """Clean up old sessions (older than 30 days)."""
    from django.contrib.sessions.models import Session

    cutoff = timezone.now() - timedelta(days=30)
    deleted_count, _ = Session.objects.filter(expire_date__lt=cutoff).delete()
    logger.info(f"Cleaned up {deleted_count} expired sessions")
    return {"deleted_count": deleted_count}
