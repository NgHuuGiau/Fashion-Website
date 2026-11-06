"""Run order side effects only after the database transaction succeeds."""

from django.db import transaction

from .order_email import send_order_email
from .shipping.service import create_shipping_order


def notify_order_after_commit(order, event, *, ship=False):
    transaction.on_commit(lambda: send_order_email(order, event=event), robust=True)
    if ship:
        transaction.on_commit(lambda: create_shipping_order(order), robust=True)
