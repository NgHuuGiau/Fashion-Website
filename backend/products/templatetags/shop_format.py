from datetime import timedelta
from decimal import Decimal, InvalidOperation

from django import template
from django.utils import timezone

from products.constants import get_category_type_label
from core.text_utils import normalize_vn_text, repair_mojibake_text


register = template.Library()


@register.filter
def vnd(value):
    if value in (None, ""):
        return "0"

    try:
        amount = int(Decimal(str(value)))
    except (InvalidOperation, TypeError, ValueError):
        return value

    return f"{amount:,}".replace(",", ".")


@register.filter
def repair_text(value):
    return repair_mojibake_text(value)


@register.filter
def normalize_vn(value):
    return normalize_vn_text(value)


@register.filter
def product_type_label(category_slug):
    return get_category_type_label(category_slug)


@register.filter
def is_new(product):
    """Sản phẩm mới trong 14 ngày -> hiển thị badge MỚI."""
    created = getattr(product, "created", None)
    if not created:
        return False
    return timezone.now() - created <= timedelta(days=14)
