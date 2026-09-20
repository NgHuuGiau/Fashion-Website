"""Service pricing checkout tach tu views/cart.py (P-refactor).

Chi chua logic thuan tuy + query DB don gian, khong phu thuoc request,
de view mong va de test truc tiep.
"""

from decimal import Decimal

from core.text_utils import normalize_vn_text

from ..constants import (
    FREESHIP_THRESHOLD,
    HCMC_KEYWORDS,
    MAX_STACKED_DISCOUNT_PCT,
    NORTHERN_KEYWORDS,
    SHIPPING_FEE_ZONES,
    STANDARD_SHIPPING_FEE,
)
from ..models import Coupon


def shipping_zone(address):
    text = normalize_vn_text(address or "").lower()
    if any(k in text for k in HCMC_KEYWORDS):
        return "near"
    if any(k in text for k in NORTHERN_KEYWORDS):
        return "north"
    return "standard"


def calculate_shipping_fee(subtotal, address=""):
    if subtotal >= FREESHIP_THRESHOLD:
        return Decimal("0")
    return SHIPPING_FEE_ZONES.get(shipping_zone(address), STANDARD_SHIPPING_FEE)


def calculate_coupon_discount(coupon, subtotal, shipping_fee):
    if not coupon:
        return Decimal("0")

    discount = Decimal("0")
    if coupon.discount_type == Coupon.TYPE_PERCENT:
        discount = (subtotal * coupon.value) / Decimal("100")
    elif coupon.discount_type == Coupon.TYPE_FIXED:
        discount = coupon.value
    elif coupon.discount_type == Coupon.TYPE_FREESHIP:
        discount = shipping_fee

    if coupon.max_discount_amount is not None:
        discount = min(discount, coupon.max_discount_amount)

    max_allowed_discount = subtotal + shipping_fee
    return max(Decimal("0"), min(discount, max_allowed_discount))


def validate_coupon(coupon_code, subtotal, user=None):
    if not coupon_code:
        return None, ""

    coupon = Coupon.objects.filter(code=coupon_code).first()
    if not coupon:
        return None, "Mã giảm giá không tồn tại."

    if not coupon.is_usable_now():
        return None, "Mã giảm giá đã hết hạn hoặc không còn hiệu lực."

    if subtotal < coupon.min_order_amount:
        return None, f"Đơn tối thiểu để dùng mã là {int(coupon.min_order_amount)} VND."

    if not coupon.is_usable_by_user(user):
        return None, "Bạn đã dùng hết lượt của mã giảm giá này."

    return coupon, ""


def apply_stacking_policy(
    *,
    coupon,
    subtotal,
    shipping_fee,
    discount_amount,
    tier_discount_amount,
    points_to_use,
    points_discount,
):
    """Ap dung policy cong don P3.1.

    Ma doc quyen -> bo giam hang + diem. Nguoc lai tran hang + diem
    vuot MAX_STACKED_DISCOUNT_PCT (uu tien cat diem truoc).
    Tra (tier, points_to_use, points_discount, total).
    """
    if coupon is not None and not coupon.stackable:
        total = max(Decimal("0"), subtotal + shipping_fee - discount_amount)
        return Decimal("0"), 0, Decimal("0"), total

    stacked_cap = subtotal * MAX_STACKED_DISCOUNT_PCT / Decimal("100")
    excess = (tier_discount_amount + points_discount) - stacked_cap
    if excess > 0:
        cut_points = min(points_discount, excess)
        points_discount -= cut_points
        points_to_use = min(points_to_use, int(points_discount / Decimal("100")))
        excess -= cut_points
        if excess > 0:
            tier_discount_amount = max(Decimal("0"), tier_discount_amount - excess)
    total = max(
        Decimal("0"),
        subtotal
        + shipping_fee
        - discount_amount
        - tier_discount_amount
        - points_discount,
    )
    return tier_discount_amount, points_to_use, points_discount, total
