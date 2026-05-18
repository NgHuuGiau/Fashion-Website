from decimal import Decimal, InvalidOperation

from django import template

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
