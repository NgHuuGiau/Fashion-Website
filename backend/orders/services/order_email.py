import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

EVENT_TEMPLATES = {
    "created": ("emails/order_confirmation.html", "Xác nhận đơn hàng"),
    "paid": ("emails/order_paid.html", "Thanh toán thành công"),
    "cancelled": ("emails/order_cancelled.html", "Đơn hàng đã hủy"),
    "delivered": ("emails/order_delivered.html", "Đơn hàng hoàn thành"),
}


def _order_context(order):
    items = []
    for item in order.items.select_related("product", "variant"):
        items.append(
            {
                "name": item.product.name,
                "meta": " / ".join(filter(None, [item.selected_color, item.selected_size])),
                "quantity": item.quantity,
                "price": item.price,
                "total": item.price * item.quantity,
            }
        )
    return {
        "order": order,
        "items": items,
        "subtotal": order.subtotal_amount,
        "shipping_fee": order.shipping_fee,
        "discount_amount": order.discount_amount,
        "total": order.total_amount,
        "payment_label": order.get_payment_method_display(),
    }


def send_order_email(order, event="created", fail_silently=True):
    """Gửi email cho khách theo sự kiện đơn hàng. Bỏ qua nếu chưa cấu hình SMTP."""
    if not settings.EMAIL_HOST:
        return False
    customer_email = order.customer_email or getattr(order.user, "email", "")
    if not customer_email:
        return False
    if event not in EVENT_TEMPLATES:
        return False

    template, subject = EVENT_TEMPLATES[event]
    try:
        context = _order_context(order)
        html = render_to_string(template, context)
        subject = f"{subject} #{order.id} — HUUGIAU Studio"
        msg = EmailMultiAlternatives(
            subject=subject,
            body=subject,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[customer_email],
        )
        msg.attach_alternative(html, "text/html")
        msg.send(fail_silently=fail_silently)
        return True
    except Exception as exc:  # noqa: BLE001 — email không được làm hỏng luồng đơn hàng
        logger.warning("Không gửi được email đơn %s: %s", order.id, exc)
        return False
