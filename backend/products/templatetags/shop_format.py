from decimal import Decimal, InvalidOperation
import unicodedata

from django import template


register = template.Library()


def _repair_mojibake_text(value):
    text = str(value or "")
    try:
        return text.encode("latin1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text


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
    return _repair_mojibake_text(value)


@register.filter
def normalize_vn(value):
    repaired = _repair_mojibake_text(value).casefold()
    normalized = unicodedata.normalize("NFD", repaired)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
