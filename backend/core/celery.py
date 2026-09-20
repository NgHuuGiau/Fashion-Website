"""Celery configuration for HUUGIAU Fashion Website."""

import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("fashion_website")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat Schedule for periodic tasks
app.conf.beat_schedule = {
    # Send cart reminders every hour
    "send-cart-reminders-hourly": {
        "task": "orders.tasks.send_cart_reminders",
        "schedule": crontab(minute=0, hour="*"),
    },
    # Reconciliation job daily at 2 AM
    "daily-reconciliation": {
        "task": "orders.tasks.daily_reconciliation",
        "schedule": crontab(hour=2, minute=0),
    },
    # Canh bao ton kho moi sang 8h
    "notify-low-stock-daily": {
        "task": "orders.tasks.notify_low_stock",
        "schedule": crontab(hour=8, minute=0),
    },
    # Expire points daily at 3 AM
    "expire-points-daily": {
        "task": "users.tasks.expire_points",
        "schedule": crontab(hour=3, minute=0),
    },
    # Clean up old sessions daily at 4 AM
    "cleanup-sessions": {
        "task": "core.tasks.cleanup_sessions",
        "schedule": crontab(hour=4, minute=0),
    },
    "cleanup-old-logs": {
        "task": "core.tasks.cleanup_old_logs",
        "schedule": crontab(hour=4, minute=30),
    },
    # Health check every 5 minutes
    "health-check": {
        "task": "core.tasks.health_check",
        "schedule": crontab(minute="*/5"),
    },
}

app.conf.timezone = "Asia/Ho_Chi_Minh"
app.conf.task_serializer = "json"
app.conf.accept_content = ["json"]
app.conf.result_serializer = "json"
app.conf.result_expires = 3600
app.conf.task_acks_late = True
app.conf.worker_prefetch_multiplier = 1
app.conf.task_routes = {
    "orders.tasks.send_cart_reminders": {"queue": "reminders"},
    "orders.tasks.process_vnpay_ipn": {"queue": "payments"},
    "orders.tasks.process_bank_ipn": {"queue": "payments"},
    "orders.tasks.daily_reconciliation": {"queue": "reconciliation"},
    "orders.tasks.notify_low_stock": {"queue": "maintenance"},
    "users.tasks.expire_points": {"queue": "maintenance"},
    "core.tasks.cleanup_sessions": {"queue": "maintenance"},
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
