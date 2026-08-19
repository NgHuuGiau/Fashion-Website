import hashlib
from datetime import timedelta
from decimal import Decimal
from urllib.parse import quote

from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.db.models import F, Sum
from django.db.models.functions import Greatest
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from core.text_utils import normalize_vn_text
from products.models import Product, ProductVariant
from users.activity import log_activity
from users.models import UserAddress, UserProfile

from ..cart import add_cart, clear_cart, iter_cart, remove_cart, safe_int
from ..constants import (
    BANKS,
    FREESHIP_THRESHOLD,
    HCMC_KEYWORDS,
    NORTHERN_KEYWORDS,
    PAYMENT_TIMEOUT_MINUTES,
    SHOP_ACCOUNT_NAME,
    SHOP_BANK_ACCOUNT,
    SHIPPING_FEE_ZONES,
    STANDARD_SHIPPING_FEE,
    TIER_DISCOUNTS,
)
from ..forms import CheckoutForm
from ..models import Coupon, CouponRedemption, Order, OrderItem


def build_vietqr_url(bank_code, amount, transfer_note):
    bank = BANKS.get(bank_code)
    if not bank:
        return ""
    return (
        f"https://img.vietqr.io/image/{bank['bin']}-{SHOP_BANK_ACCOUNT}-compact2.png"
        f"?amount={int(amount)}&addInfo={quote(transfer_note)}&accountName={quote(SHOP_ACCOUNT_NAME)}"
    )


def normalize_shipping_address(value):
    return normalize_vn_text(value)


def shipping_zone(address):
    text = normalize_shipping_address(address or "").lower()
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


def restore_order_stock(order):
    if order.status == "cancelled":
        return
    with transaction.atomic():
        for item in order.items.select_related("product", "variant"):
            if item.variant:
                ProductVariant.objects.filter(id=item.variant.id).update(stock=F("stock") + item.quantity)
                total_stock = item.product.variants.filter(is_active=True).aggregate(total=Sum("stock"))["total"] or 0
                item.product.stock = total_stock
                item.product.save(update_fields=["stock", "updated"])
            else:
                Product.objects.filter(id=item.product.id).update(
                    stock=F("stock") + item.quantity,
                    updated=timezone.now()
                )


def reserve_order_stock(order):
    with transaction.atomic():
        for item in order.items.select_related("product", "variant"):
            if item.variant:
                ProductVariant.objects.filter(id=item.variant.id).update(stock=Greatest(F("stock") - item.quantity, 0))
                total_stock = item.product.variants.filter(is_active=True).aggregate(total=Sum("stock"))["total"] or 0
                item.product.stock = total_stock
                item.product.save(update_fields=["stock", "updated"])
            else:
                Product.objects.filter(id=item.product.id).update(
                    stock=Greatest(F("stock") - item.quantity, 0),
                    updated=timezone.now()
                )


def apply_order_status_change(order, new_status, is_paid=False):
    """Cập nhật trạng thái đơn và đồng bộ tồn kho.

    - Chuyển sang trạng thái 'cancelled': trả lại hàng về kho.
    - Bỏ huỷ (từ 'cancelled' sang trạng thái khác): trừ lại hàng khỏi kho.
    """
    old_status = order.status
    with transaction.atomic():
        if old_status != "cancelled" and new_status == "cancelled":
            restore_order_stock(order)
        elif old_status == "cancelled" and new_status != "cancelled":
            reserve_order_stock(order)
        order.status = new_status
        order.is_paid = bool(is_paid)
        order.save(update_fields=["status", "is_paid", "updated_at"])
    if new_status == "shipping":
        from .order import mark_order_shipped

        mark_order_shipped(order)
    elif new_status == "delivered":
        from ..services.order_email import send_order_email
        from .order import _grant_order_points

        send_order_email(order, event="delivered")
        _grant_order_points(order)
    return order


def is_bank_order_expired(order):
    if order.payment_method not in ("bank", "vnpay"):
        return False
    if order.is_paid:
        return False
    if order.status != "processing":
        return False
    return timezone.now() > (order.created_at + timedelta(minutes=PAYMENT_TIMEOUT_MINUTES))


def expire_bank_order_if_needed(order):
    if not is_bank_order_expired(order):
        return False
    restore_order_stock(order)
    order.status = "cancelled"
    timeout_note = "[AUTO_TIMEOUT_15_MIN]"
    order.note = f"{order.note}\n{timeout_note}".strip() if order.note else timeout_note
    order.save(update_fields=["status", "note", "updated_at"])
    return True


def _payment_token(order_id):
    raw = f"bank:{order_id}:qr:{settings.SECRET_KEY}"
    return hashlib.sha256(raw.encode()).hexdigest()


@require_POST
def cart_add(request: HttpRequest, product_id) -> HttpResponse:
    is_ajax = request.headers.get("x-requested-with", "").lower() == "xmlhttprequest"

    def finish(message: str, is_error: bool = False, url: str | None = None) -> HttpResponse:
        if is_ajax:
            return JsonResponse({"ok": not is_error, "message": message})
        if is_error:
            messages.error(request, message)
        else:
            messages.success(request, message)
        return redirect(url or "orders:cart_detail")

    product = get_object_or_404(Product, id=product_id, available=True)
    variant_id = request.POST.get("variant_id")
    selected_variant = None
    requires_variant = product.requires_variants

    if variant_id:
        selected_variant = ProductVariant.objects.filter(id=variant_id, product=product, is_active=True).first()

    if requires_variant and not selected_variant:
        return finish("Vui lòng chọn màu và size trước khi thêm vào giỏ.", True, product.get_absolute_url())

    stock = selected_variant.stock if selected_variant else product.stock
    if stock <= 0:
        return finish("Sản phẩm đã hết hàng.", True, request.POST.get("next") or "products:product_list")

    quantity = safe_int(request.POST.get("quantity", 1), default=1, minimum=1)
    success, msg = add_cart(request, product.id, quantity=quantity, variant_id=selected_variant.id if selected_variant else None)
    if not success:
        return finish(msg, True, request.POST.get("next") or "products:product_list")
    log_activity(
        request,
        event_type="cart_add",
        metadata={
            "product_id": product.id,
            "variant_id": selected_variant.id if selected_variant else None,
            "quantity": quantity,
        },
    )
    return finish(msg)


def cart_summary(request: HttpRequest) -> JsonResponse:
    items, subtotal = iter_cart(request)
    payload = {
        "count": sum(item["quantity"] for item in items),
        "subtotal": str(subtotal),
        "items": [
            {
                "name": row["product"].name,
                "quantity": row["quantity"],
                "price": str(row["price"]),
                "line_total": str(row["subtotal"]),
                "variant_label": (
                    f"{row['variant'].color_name} / {row['variant'].size}" if row["variant"] else ""
                ),
                "image": row["product"].get_image(),
                "url": reverse(
                    "products:product_detail",
                    kwargs={"pk": row["product"].id, "slug": row["product"].slug},
                ),
            }
            for row in items[:10]
        ],
    }
    return JsonResponse(payload)


@require_POST
def cart_update(request: HttpRequest) -> HttpResponse:
    item_key = request.POST.get("item_key", "").strip()
    if not item_key:
        messages.error(request, "Không tìm thấy sản phẩm trong giỏ.")
        return redirect("orders:cart_detail")

    parts = item_key.split(":")
    if len(parts) != 2:
        messages.error(request, "Không tìm thấy sản phẩm trong giỏ.")
        return redirect("orders:cart_detail")

    try:
        product_id = int(parts[0])
    except ValueError:
        messages.error(request, "Không tìm thấy sản phẩm trong giỏ.")
        return redirect("orders:cart_detail")

    variant_id = int(parts[1]) if parts[1].isdigit() else None
    quantity = safe_int(request.POST.get("quantity", 1), default=1, minimum=1)
    success, msg = add_cart(
        request,
        product_id,
        quantity=quantity,
        override_quantity=True,
        variant_id=variant_id if variant_id and variant_id > 0 else None,
    )
    if success:
        messages.success(request, msg)
    else:
        messages.error(request, msg)
    return redirect("orders:cart_detail")


@require_POST
def cart_remove(request: HttpRequest) -> HttpResponse:
    item_key = request.POST.get("item_key", "").strip()
    remove_cart(request, item_key=item_key)
    messages.success(request, "Đã xóa sản phẩm khỏi giỏ hàng.")
    return redirect("orders:cart_detail")


@require_POST
def cart_clear_all(request: HttpRequest) -> HttpResponse:
    clear_cart(request)
    messages.success(request, "Đã xóa toàn bộ giỏ hàng.")
    return redirect("orders:cart_detail")


def cart_detail(request: HttpRequest) -> HttpResponse:
    items, subtotal = iter_cart(request)
    shipping_fee = calculate_shipping_fee(subtotal)
    total = subtotal + shipping_fee
    return render(
        request,
        "shop/cart.html",
        {
            "items": items,
            "subtotal": subtotal,
            "shipping_fee": shipping_fee,
            "total": total,
            "freeship_threshold": FREESHIP_THRESHOLD,
            "freeship_remaining": max(FREESHIP_THRESHOLD - subtotal, 0),
        },
    )


def checkout(request: HttpRequest) -> HttpResponse:
    items, subtotal = iter_cart(request)
    if not items:
        messages.warning(request, "Giỏ hàng đang trống.")
        return redirect("products:product_list")

    is_guest = not request.user.is_authenticated

    if is_guest:
        initial = {}
        default_address = None
        saved_addresses = []
        tier_name = ""
        tier_discount_pct_value = 0
        profile = None
    else:
        initial = {
            "customer_name": f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
            "customer_email": request.user.email,
        }
        default_address = UserAddress.objects.filter(user=request.user, is_default=True).first() or (
            UserAddress.objects.filter(user=request.user).first()
        )
        if default_address:
            initial["phone"] = default_address.phone
            initial["shipping_address"] = default_address.address
        saved_addresses = list(UserAddress.objects.filter(user=request.user))
        tier_name = UserProfile.objects.get_or_create(user=request.user)[0].tier_name()
        tier_discount_pct_value = TIER_DISCOUNTS.get(tier_name, 0)
        profile, _ = UserProfile.objects.get_or_create(user=request.user)

    shipping_fee = calculate_shipping_fee(subtotal, default_address.address if default_address else "")
    discount_amount = Decimal("0")
    tier_discount_amount = Decimal("0")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            payment_method = form.cleaned_data["payment_method"]
            bank_code = form.cleaned_data.get("bank_code", "") if payment_method == "bank" else ""
            coupon_code = form.cleaned_data.get("coupon_code", "")
            shipping_fee = calculate_shipping_fee(subtotal, form.cleaned_data["shipping_address"])
            tier_discount_amount = subtotal * Decimal(tier_discount_pct_value) / Decimal("100")

            coupon_user = None if is_guest else request.user
            selected_coupon, coupon_error = validate_coupon(coupon_code, subtotal, user=coupon_user)
            if coupon_error:
                form.add_error("coupon_code", coupon_error)
            else:
                discount_amount = calculate_coupon_discount(selected_coupon, subtotal, shipping_fee)
                total_amount = max(Decimal("0"), subtotal + shipping_fee - discount_amount - tier_discount_amount)

                points_to_use = 0
                points_discount = Decimal("0")
                if not is_guest and profile.points and (form.cleaned_data.get("points_to_use") or 0) > 0:
                    points_to_use = min(form.cleaned_data["points_to_use"], profile.points)
                    points_discount = min(
                        Decimal(points_to_use) * Decimal("100"),
                        max(Decimal("0"), subtotal - discount_amount),
                    )
                    total_amount = max(Decimal("0"), total_amount - points_discount)

                with transaction.atomic():
                    if selected_coupon:
                        selected_coupon = Coupon.objects.select_for_update().get(id=selected_coupon.id)
                        if not selected_coupon.is_usable_now() or (not is_guest and not selected_coupon.is_usable_by_user(request.user)):
                            form.add_error("coupon_code", "Mã giảm giá vừa hết lượt sử dụng. Vui lòng thử mã khác.")
                            transaction.set_rollback(True)
                            return render(
                                request,
                                "shop/checkout.html",
                                {
                                    "items": items,
                                    "subtotal": subtotal,
                                    "shipping_fee": shipping_fee,
                                    "discount_amount": Decimal("0"),
                                    "total": subtotal + shipping_fee,
                                    "form": form,
                                    "shop_bank_account": SHOP_BANK_ACCOUNT,
                                    "shop_account_name": SHOP_ACCOUNT_NAME,
                                    "demo_qr_url": build_vietqr_url(bank_code or "VCB", subtotal + shipping_fee, "DH-TAM"),
                                    "banks": BANKS,
                                    "saved_addresses": saved_addresses,
                                    "tier_name": tier_name,
                                    "tier_discount_pct": tier_discount_pct_value,
                                    "tier_discount_amount": tier_discount_amount,
                                    "shipping_zone": shipping_fee,
                                },
                            )
                        selected_coupon.used_count += 1
                        selected_coupon.save(update_fields=["used_count", "updated_at"])

                    order = Order.objects.create(
                        user=None if is_guest else request.user,
                        customer_name=form.cleaned_data["customer_name"],
                        customer_email=form.cleaned_data["customer_email"],
                        phone=form.cleaned_data["phone"],
                        shipping_address=form.cleaned_data["shipping_address"],
                        note=form.cleaned_data["note"],
                        delivery_time_slot=form.cleaned_data.get("delivery_time_slot", ""),
                        gift_wrap=form.cleaned_data.get("gift_wrap", False),
                        gift_note=form.cleaned_data.get("gift_note", ""),
                        payment_method=payment_method,
                        bank_code=bank_code,
                        subtotal_amount=subtotal,
                        shipping_fee=shipping_fee,
                        discount_amount=discount_amount + tier_discount_amount,
                        points_used=points_to_use,
                        coupon=selected_coupon,
                        coupon_code=selected_coupon.code if selected_coupon else "",
                        total_amount=total_amount,
                        is_paid=False,
                        status="processing" if payment_method in ("bank", "vnpay") else "pending",
                    )

                    if points_to_use and not is_guest:
                        profile.points -= points_to_use
                        profile.save(update_fields=["points"])

                    if selected_coupon:
                        CouponRedemption.objects.create(
                            coupon=selected_coupon,
                            user=None if is_guest else request.user,
                            order=order,
                        )

                    variant_ids = [item["variant"].id for item in items if item.get("variant")]
                    plain_product_ids = [item["product"].id for item in items if not item.get("variant")]

                    locked_variants = {
                        v.id: v
                        for v in ProductVariant.objects.select_for_update().filter(id__in=variant_ids)
                    }
                    locked_products = {
                        p.id: p
                        for p in Product.objects.select_for_update().filter(id__in=plain_product_ids)
                    }

                    for item in items:
                        variant = item.get("variant")
                        quantity = item["quantity"]
                        product = item["product"]

                        if variant:
                            lv = locked_variants.get(variant.id)
                            if not lv or lv.stock < quantity:
                                transaction.set_rollback(True)
                                messages.error(request, f"Sản phẩm {product.name} ({lv.color_name}/{lv.size}) không đủ hàng.")
                                return redirect("orders:cart_detail")
                            ProductVariant.objects.filter(id=variant.id).update(
                                stock=Greatest(F("stock") - quantity, 0)
                            )
                        else:
                            lp = locked_products.get(product.id)
                            if not lp or lp.stock < quantity:
                                transaction.set_rollback(True)
                                messages.error(request, f"Sản phẩm {product.name} không đủ hàng.")
                                return redirect("orders:cart_detail")
                            Product.objects.filter(id=product.id).update(
                                stock=Greatest(F("stock") - quantity, 0),
                                updated=timezone.now(),
                            )

                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            variant=variant,
                            selected_color=variant.color_name if variant else "",
                            selected_size=variant.size if variant else "",
                            quantity=quantity,
                            price=item["price"],
                        )

                    for item in items:
                        product = item["product"]
                        variant = item.get("variant")
                        if variant:
                            product.stock = ProductVariant.objects.filter(product=product, is_active=True).aggregate(total=Sum("stock"))["total"] or 0
                            product.save(update_fields=["stock", "updated"])

                clear_cart(request)
                from ..services.order_email import send_order_email

                send_order_email(order, event="created")
                log_activity(
                    request,
                    event_type="checkout",
                    metadata={
                        "order_id": order.id,
                        "subtotal": str(order.subtotal_amount),
                        "shipping_fee": str(order.shipping_fee),
                        "discount_amount": str(order.discount_amount),
                        "coupon_code": order.coupon_code,
                        "total_amount": str(order.total_amount),
                    },
                    status_code=201,
                )
                messages.success(request, "Đặt hàng thành công.")
                if payment_method == "bank":
                    return redirect("orders:bank_payment_waiting", order_id=order.id)
                if payment_method == "vnpay":
                    return redirect("orders:vnpay_payment", order_id=order.id)
                return redirect("orders:order_success", order_id=order.id)
    else:
        form = CheckoutForm(initial=initial)

    demo_bank_code = request.POST.get("bank_code") if request.method == "POST" else "VCB"
    if demo_bank_code not in BANKS:
        demo_bank_code = "VCB"

    if request.method == "POST" and form.is_valid() and not coupon_error:
        discount_amount = calculate_coupon_discount(selected_coupon, subtotal, shipping_fee)

    total = max(Decimal("0"), subtotal + shipping_fee - discount_amount - tier_discount_amount)

    if is_guest:
        user_points = 0
    else:
        user_points = UserProfile.objects.get_or_create(user=request.user)[0].points

    return render(
        request,
        "shop/checkout.html",
        {
            "items": items,
            "subtotal": subtotal,
            "shipping_fee": shipping_fee,
            "discount_amount": discount_amount,
            "tier_name": tier_name,
            "tier_discount_pct": tier_discount_pct_value,
            "tier_discount_amount": tier_discount_amount,
            "shipping_zone": shipping_zone(form.cleaned_data["shipping_address"]) if request.method == "POST" and form.is_valid() else shipping_zone(default_address.address if default_address else ""),
            "total": total,
            "form": form,
            "shop_bank_account": SHOP_BANK_ACCOUNT,
            "shop_account_name": SHOP_ACCOUNT_NAME,
            "demo_qr_url": build_vietqr_url(demo_bank_code, total, "DH-TAM"),
            "freeship_threshold": FREESHIP_THRESHOLD,
            "banks": BANKS,
            "user_points": user_points,
            "saved_addresses": saved_addresses,
            "is_guest": is_guest,
        },
    )


def promo_page(request: HttpRequest) -> HttpResponse:
    coupons = [c for c in Coupon.objects.filter(is_active=True) if c.is_usable_now()]
    return render(request, "shop/promo.html", {"coupons": coupons, "freeship_threshold": FREESHIP_THRESHOLD})
