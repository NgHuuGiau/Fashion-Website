"""Celery tasks for orders app."""

import logging
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.management import call_command
from django.db import transaction
from django.db.models import F, Sum
from django.utils import timezone

from .services.order_email import send_order_email

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


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_vnpay_ipn(self, params):
    """Xử lý VNPay IPN (server-to-server)."""
    from orders.models import Order
    from orders.vnpay import amount_matches, verify_return

    try:
        if not verify_return(params):
            logger.warning("VNPay IPN: Invalid signature")
            return {"RspCode": "97", "Message": "Invalid signature"}

        order_id = params.get("vnp_TxnRef")
        response_code = params.get("vnp_ResponseCode")
        transaction_status = params.get("vnp_TransactionStatus")

        with transaction.atomic():
            order = Order.objects.select_for_update().filter(id=order_id).first()
            if order is None:
                logger.warning("VNPay IPN: order not found id=%s", order_id)
                return {"RspCode": "01", "Message": "Order not found"}
            if order.payment_method != "vnpay" or not amount_matches(order, params):
                return {"RspCode": "97", "Message": "Invalid payment or amount"}
            if order.is_paid:
                return {"RspCode": "02", "Message": "Order already confirmed"}

            transaction_id = params.get("vnp_TransactionNo", "").strip()
            if response_code == "00" and transaction_status == "00" and transaction_id:
                order.is_paid = True
                order.vnpay_transaction_id = transaction_id
                fields = ["is_paid", "vnpay_transaction_id", "updated_at"]
                if order.status == "cancelled":
                    logger.error(
                        "Late VNPay task callback for cancelled order %s; reconcile manually",
                        order.id,
                    )
                else:
                    order.status = "processing"
                    fields.append("status")
                    order._status_change_source = "vnpay_ipn_task"
                    order._status_change_transaction_id = transaction_id
                    order._status_change_note = "Celery xác nhận VNPay thành công."
                    send_order_email(order, event="paid")
                order.save(update_fields=fields)
                return {"RspCode": "00", "Message": "Confirm Success"}

            if order.status != "cancelled":
                restore_order_stock(order)
                order.status = "cancelled"
                order._status_change_source = "vnpay_ipn_task"
                order._status_change_transaction_id = transaction_id
                order._status_change_note = (
                    f"Celery nhận IPN thất bại, mã phản hồi {response_code}."
                )
                order.save(update_fields=["status", "updated_at"])
                send_order_email(order, event="cancelled")
            return {"RspCode": "97", "Message": "Payment not successful"}

    except Exception as exc:
        logger.exception(
            "process_vnpay_ipn failed for order %s", params.get("vnp_TxnRef")
        )
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
        order._status_change_source = "stock_restore_task"
        order._status_change_note = "Tác vụ hệ thống hoàn tồn kho khi hủy đơn."
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
