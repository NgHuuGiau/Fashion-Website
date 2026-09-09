"""Celery tasks for core app."""

import logging
from datetime import timedelta

from celery import shared_task
from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.db import connection
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def health_check(self):
    """Health check task for monitoring."""
    checks = {}
    healthy = True

    # Database check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {e}"
        healthy = False

    # Cache check
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


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def cleanup_sessions(self):
    """Clean up old sessions (older than 30 days)."""

    cutoff = timezone.now() - timedelta(days=30)
    deleted_count, _ = Session.objects.filter(expire_date__lt=cutoff).delete()
    logger.info(f"Cleaned up {deleted_count} expired sessions")
    return {"deleted_count": deleted_count}


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def cleanup_old_logs(self):
    """Clean up old log entries (older than 90 days)."""
    # Implementation depends on logging setup
    logger.info("Log cleanup task executed")
    return {"status": "completed"}


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def cleanup_old_carts(self):
    """Clean up abandoned carts older than 30 days."""
    from orders.models import CartReminder

    cutoff = timezone.now() - timedelta(days=30)
    deleted_count, _ = CartReminder.objects.filter(created_at__lt=cutoff).delete()
    logger.info(f"Cleaned up {deleted_count} old cart reminders")
    return {"deleted_count": deleted_count}
