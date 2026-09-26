"""API JSON (tach tu core/api.py monolith). Logic giu nguyen."""

from django.http import JsonResponse

from core.text_utils import repair_mojibake_text

from orders.constants import (
    shop_bank_code,
)


SORT_OPTIONS = {
    "newest": "-created",
    "price_asc": "price",
    "price_desc": "-price",
    "name_asc": "name",
}
PRODUCTS_PER_PAGE = 12


def api_json(data, status=200):
    return JsonResponse(data, status=status, safe=False)


def api_error(message, status=400):
    return api_json({"error": message}, status=status)


def int_param(request, name, default=None):
    raw = request.GET.get(name, "")
    try:
        return int(raw)
    except (TypeError, ValueError):
        return default


def _serialize_variant(variant):
    return {
        "id": variant.id,
        "color_name": repair_mojibake_text(variant.color_name),
        "color_code": variant.color_code,
        "size": variant.size,
        "stock": variant.stock,
        "is_active": variant.is_active,
    }


def _serialize_product_summary(product):
    return {
        "id": product.id,
        "slug": product.slug,
        "name": repair_mojibake_text(product.name),
        "price": int(product.price),
        "image": product.get_image(),
        "category": repair_mojibake_text(product.category.name),
        "category_slug": product.category.slug,
        "stock": product.stock,
        "available": product.available,
        "rating_avg": round(product.rating_avg, 1)
        if getattr(product, "rating_avg", None) is not None
        else 0,
        "rating_count": getattr(product, "rating_count", 0) or 0,
        "url": product.get_absolute_url(),
    }


def _serialize_review(review):
    return {
        "id": review.id,
        "user": review.user.username,
        "rating": review.rating,
        "comment": repair_mojibake_text(review.comment),
        "verified_purchase": review.verified_purchase,
        "created": review.created.isoformat(),
    }


def _serialize_order(order, include_items=False):
    data = {
        "id": order.id,
        "customer_name": repair_mojibake_text(order.customer_name),
        "customer_email": order.customer_email,
        "phone": order.phone,
        "shipping_address": order.shipping_address,
        "payment_method": order.payment_method,
        "payment_method_label": order.get_payment_method_display(),
        "bank_code": shop_bank_code() if order.payment_method == "bank" else "",
        "is_paid": order.is_paid,
        "status": order.status,
        "status_label": order.get_status_display(),
        "subtotal_amount": int(order.subtotal_amount),
        "shipping_fee": int(order.shipping_fee),
        "discount_amount": int(order.discount_amount),
        "coupon_code": order.coupon_code,
        "total_amount": int(order.total_amount),
        "note": order.note,
        "created_at": order.created_at.isoformat(),
    }
    if include_items:
        data["items"] = [
            {
                "id": item.id,
                "product_id": item.product_id,
                "product_name": repair_mojibake_text(item.display_name),
                "color": item.selected_color,
                "size": item.selected_size,
                "quantity": item.quantity,
                "price": int(item.price),
                "subtotal": int(item.price * item.quantity),
            }
            for item in order.items.select_related("product")
        ]
    return data
