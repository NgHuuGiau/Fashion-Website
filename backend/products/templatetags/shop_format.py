from datetime import timedelta
from decimal import Decimal, InvalidOperation

from django import template
from django.utils import timezone
from django.utils.safestring import mark_safe
import json

from products.constants import get_category_type_label
from core.text_utils import normalize_vn_text, repair_mojibake_text


register = template.Library()


@register.simple_tag(takes_context=True)
def json_script_nonce(context, value, element_id):
    """Render JSON script tag với CSP nonce từ request context."""
    request = context.get("request")
    nonce = getattr(request, "csp_nonce", "") if request else ""
    nonce_attr = f' nonce="{nonce}"' if nonce else ""
    data = json.dumps(value, ensure_ascii=False)
    # Escape for safe embedding in script tag
    data = data.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return mark_safe(
        f'<script type="application/json" id="{element_id}"{nonce_attr}>{data}</script>'
    )


@register.filter
def vnd(value):
    if value in (None, ""):
        return "0"

    try:
        amount = int(Decimal(str(value)))
    except (InvalidOperation, TypeError, ValueError):
        return value

    return f"{amount:,}".replace(",", ".")


@register.filter(is_safe=True)
def json_escape(value):
    """JSON string value an toàn trong JSON-LD: thoát control chars & <>&."""
    import json

    from django.utils.safestring import mark_safe

    s = value if value is not None else ""
    out = json.dumps(str(s), ensure_ascii=False)
    return mark_safe(
        out.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    )


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


@register.filter
def div(value, arg):
    try:
        return float(value) / float(arg)
    except (TypeError, ValueError, ZeroDivisionError):
        return 0
