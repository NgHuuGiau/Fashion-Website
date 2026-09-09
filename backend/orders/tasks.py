"""Celery tasks for orders app."""

import logging
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.db import transaction
from django.db.models import F, Sum
from django.utils import timezone

from .models import CartReminder
from .services.order_email import send_order_email

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def send_cart_reminders(self):
    """Gửi email nhắc giỏ hàng bị bỏ (chạy hàng giờ)."""
    try:
        threshold = timezone.now() - timedelta(hours=1)
        reminders = CartReminder.objects.filter(
            sent_at__isnull=True,
            created_at__lte=threshold,
        ).select_related("user")[:100]

        sent_count = 0
        for reminder in reminders:
            try:
                if reminder.user:
                    send_order_email(
                        reminder.user,
                        event="cart_reminder",
                        context={
                            "items": reminder.items,
                            "total": reminder.total_amount,
                        },
                    )
                else:
                    # Guest cart reminder - need email from session
                    pass

                reminder.sent_at = timezone.now()
                reminder.save(update_fields=["sent_at"])
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send cart reminder {reminder.id}: {e}")

        logger.info(f"Sent {sent_count} cart reminder emails")
        return {"sent_count": sent_count}
    except Exception as exc:
        logger.error(f"send_cart_reminders failed: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_vnpay_ipn(self, params):
    """Xử lý VNPay IPN (server-to-server)."""
    from orders.models import Order
    from orders.vnpay import verify_return

    try:
        if not verify_return(params):
            logger.warning("VNPay IPN: Invalid signature")
            return {"RspCode": "97", "Message": "Invalid signature"}

        order_id = params.get("vnp_TxnRef")
        response_code = params.get("vnp_ResponseCode")
        transaction_status = params.get("vnp_TransactionStatus")

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            logger.warning(f"VNPay IPN: Order {order_id} not found")
            return {"RspCode": "01", "Message": "Order not found"}

        if order.payment_method != "vnpay":
            logger.warning(f"VNPay IPN: Order {order_id} not a VNPay order")
            return {"RspCode": "97", "Message": "Invalid payment method"}

        if order.is_paid:
            logger.info(f"VNPay IPN: Order {order_id} already paid")
            return {"RspCode": "02", "Message": "Order already confirmed"}

        if response_code == "00" and transaction_status == "00":
            with transaction.atomic():
                if order.status == "cancelled":
                    # Restore stock if previously cancelled
                    restore_order_stock(order)

                order.is_paid = True
                order.status = "processing"
                order.save(update_fields=["is_paid", "status", "updated_at"])

                send_order_email(order.user, event="paid", order=order)

                logger.info(f"VNPay IPN: Order {order_id} marked as paid")
                return {"RspCode": "00", "Message": "Confirm Success"}
        else:
            # Payment failed
            restore_order_stock(order)
            order.status = "cancelled"
            order.save(update_fields=["status", "updated_at"])

            send_order_email(order.user, event="cancelled", order=order)

            logger.warning(f"VNPay IPN: Order {order_id} payment failed")
            return {"RspCode": "97", "Message": "Payment not successful"}

    except Exception as exc:
        logger.error(f"process_vnpay_ipn failed for {params.get('vnp_TxnRef')}: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_bank_ipn(self, params):
    """Xử lý bank transfer IPN (nếu có webhook từ ngân hàng)."""
    # TODO: Implement bank IPN processing
    logger.info(f"Bank IPN received: {params}")
    return {"status": "received"}


def restore_order_stock(order):
    """Trả lại hàng về kho khi đơn bị hủy."""
    if order.status == "cancelled":
        return

    with transaction.atomic():
        for item in order.items.select_related("product", "variant"):
            if item.variant:
                item.variant.stock = F("stock") + item.quantity
                item.variant.save(update_fields=["stock"])

                # Cập nhật tổng stock của product
                total_stock = (
                    item.product.variants.filter(is_active=True).aggregate(
                        total=Sum("stock")
                    )["total"]
                    or 0
                )
                item.product.stock = total_stock
                item.product.save(update_fields=["stock", "updated"])
            else:
                item.product.stock = F("stock") + item.quantity
                item.product.save(update_fields=["stock", "updated"])

        order.status = "cancelled"
        order.save(update_fields=["status", "updated_at"])


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
