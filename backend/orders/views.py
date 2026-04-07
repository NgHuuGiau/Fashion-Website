from datetime import timedelta
from decimal import Decimal
from urllib.parse import quote

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, F, Q, Sum
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from products.models import Product, ProductVariant
from users.activity import log_activity

from .cart import add_cart, clear_cart, iter_cart, remove_cart, safe_int
from .forms import CheckoutForm
from .models import Coupon, Order, OrderItem

SHOP_BANK_ACCOUNT = "1234567890"
SHOP_ACCOUNT_NAME = "HUUGIAU LOCAL BRAND"
PAYMENT_TIMEOUT_MINUTES = 15
STANDARD_SHIPPING_FEE = Decimal("30000")
FREESHIP_THRESHOLD = Decimal("499000")

BANKS = {
    "VCB": {"name": "Vietcombank", "bin": "970436"},
    "TCB": {"name": "Techcombank", "bin": "970407"},
    "MB": {"name": "MBBank", "bin": "970422"},
    "ACB": {"name": "ACB", "bin": "970416"},
    "BIDV": {"name": "BIDV", "bin": "970418"},
    "VPB": {"name": "VPBank", "bin": "970432"},
}


def build_vietqr_url(bank_code, amount, transfer_note):
    bank = BANKS.get(bank_code)
    if not bank:
        return ""
    return (
        f"https://img.vietqr.io/image/{bank['bin']}-{SHOP_BANK_ACCOUNT}-compact2.png"
        f"?amount={int(amount)}&addInfo={quote(transfer_note)}&accountName={quote(SHOP_ACCOUNT_NAME)}"
    )


def calculate_shipping_fee(subtotal):
    if subtotal >= FREESHIP_THRESHOLD:
        return Decimal("0")
    return STANDARD_SHIPPING_FEE


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


def validate_coupon(coupon_code, subtotal):
    if not coupon_code:
        return None, ""

    coupon = Coupon.objects.filter(code=coupon_code).first()
    if not coupon:
        return None, "Mã giảm giá không tồn tại."

    if not coupon.is_usable_now():
        return None, "Mã giảm giá đã hết hạn hoặc không còn hiệu lực."

    if subtotal < coupon.min_order_amount:
        return None, f"Đơn tối thiểu để dùng mã là {int(coupon.min_order_amount)} VND."

    return coupon, ""


def restore_order_stock(order):
    with transaction.atomic():
        for item in order.items.select_related("product", "variant"):
            if item.variant:
                # Sử dụng F() để tránh race condition khi cập nhật tồn kho
                ProductVariant.objects.filter(id=item.variant.id).update(stock=F("stock") + item.quantity)
                # Cập nhật lại tổng tồn kho của Product dựa trên database thực tế
                total_stock = item.product.variants.filter(is_active=True).aggregate(total=Sum("stock"))["total"] or 0
                item.product.stock = total_stock
                item.product.save(update_fields=["stock", "updated"])
            else:
                Product.objects.filter(id=item.product.id).update(
                    stock=F("stock") + item.quantity,
                    updated=timezone.now()
                )


def is_bank_order_expired(order):
    if order.payment_method != "bank":
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


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)
    variant_id = request.POST.get("variant_id")
    selected_variant = None
    requires_variant = product.category.slug in {"ao", "quan"}

    if variant_id:
        selected_variant = ProductVariant.objects.filter(id=variant_id, product=product, is_active=True).first()

    if requires_variant and not selected_variant:
        messages.error(request, "Vui lòng chọn màu và size trước khi thêm vào giỏ.")
        return redirect("products:product_detail", pk=product.id, slug=product.slug)

    stock = selected_variant.stock if selected_variant else product.stock
    if stock <= 0:
        messages.error(request, "Sản phẩm đã hết hàng.")
        return redirect(request.POST.get("next") or "products:product_list")

    quantity = safe_int(request.POST.get("quantity", 1), default=1, minimum=1)
    add_cart(request, product.id, quantity=quantity, variant_id=selected_variant.id if selected_variant else None)
    log_activity(
        request,
        event_type="cart_add",
        metadata={
            "product_id": product.id,
            "variant_id": selected_variant.id if selected_variant else None,
            "quantity": quantity,
        },
    )
    messages.success(request, f"Đã thêm '{product.name}' vào giỏ hàng.")
    return redirect(request.POST.get("next") or "orders:cart_detail")


@require_POST
def cart_update(request):
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
    add_cart(
        request,
        product_id,
        quantity=quantity,
        override_quantity=True,
        variant_id=variant_id if variant_id and variant_id > 0 else None,
    )
    messages.success(request, "Đã cập nhật giỏ hàng.")
    return redirect("orders:cart_detail")


@require_POST
def cart_remove(request):
    item_key = request.POST.get("item_key", "").strip()
    remove_cart(request, item_key=item_key)
    messages.success(request, "Đã xóa sản phẩm khỏi giỏ hàng.")
    return redirect("orders:cart_detail")


@require_POST
def cart_clear_all(request):
    clear_cart(request)
    messages.success(request, "Đã xóa toàn bộ giỏ hàng.")
    return redirect("orders:cart_detail")


def cart_detail(request):
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
        },
    )


@login_required
def checkout(request):
    items, subtotal = iter_cart(request)
    if not items:
        messages.warning(request, "Giỏ hàng đang trống.")
        return redirect("products:product_list")

    initial = {
        "customer_name": f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
        "customer_email": request.user.email,
    }

    selected_coupon = None
    coupon_error = ""
    shipping_fee = calculate_shipping_fee(subtotal)
    discount_amount = Decimal("0")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            payment_method = form.cleaned_data["payment_method"]
            bank_code = form.cleaned_data.get("bank_code", "") if payment_method == "bank" else ""
            coupon_code = form.cleaned_data.get("coupon_code", "")

            selected_coupon, coupon_error = validate_coupon(coupon_code, subtotal)
            if coupon_error:
                form.add_error("coupon_code", coupon_error)
            else:
                discount_amount = calculate_coupon_discount(selected_coupon, subtotal, shipping_fee)
                total_amount = max(Decimal("0"), subtotal + shipping_fee - discount_amount)

                with transaction.atomic():
                    if selected_coupon:
                        selected_coupon = Coupon.objects.select_for_update().get(id=selected_coupon.id)
                        if not selected_coupon.is_usable_now():
                            form.add_error("coupon_code", "Mã giảm giá vừa hết lượt sử dụng. Vui lòng thử mã khác.")
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
                                },
                            )
                        selected_coupon.used_count += 1
                        selected_coupon.save(update_fields=["used_count", "updated_at"])

                    order = Order.objects.create(
                        user=request.user,
                        customer_name=form.cleaned_data["customer_name"],
                        customer_email=form.cleaned_data["customer_email"],
                        phone=form.cleaned_data["phone"],
                        shipping_address=form.cleaned_data["shipping_address"],
                        note=form.cleaned_data["note"],
                        payment_method=payment_method,
                        bank_code=bank_code,
                        subtotal_amount=subtotal,
                        shipping_fee=shipping_fee,
                        discount_amount=discount_amount,
                        coupon=selected_coupon,
                        coupon_code=selected_coupon.code if selected_coupon else "",
                        total_amount=total_amount,
                        is_paid=False,
                        status="processing" if payment_method == "bank" else "pending",
                    )

                    for item in items:
                        variant = item.get("variant")
                        OrderItem.objects.create(
                            order=order,
                            product=item["product"],
                            variant=variant,
                            selected_color=variant.color_name if variant else "",
                            selected_size=variant.size if variant else "",
                            quantity=item["quantity"],
                            price=item["price"],
                        )

                        product = item["product"]
                        if variant:
                            variant.stock = max(0, variant.stock - item["quantity"])
                            variant.save(update_fields=["stock"])
                            # Tối ưu: Tính tổng tồn kho trực tiếp từ Database thay vì xử lý bằng Python
                            product.stock = product.variants.filter(is_active=True).aggregate(total=Sum("stock"))["total"] or 0
                        else:
                            # Đảm bảo tồn kho không bị âm khi trừ
                            Product.objects.filter(id=product.id).update(stock=F("stock") - item["quantity"])
                            product.refresh_from_db()
                            if product.stock < 0:
                                product.stock = 0
                        product.save(update_fields=["stock", "updated"])

                clear_cart(request)
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
                return redirect("orders:order_success", order_id=order.id)
    else:
        form = CheckoutForm(initial=initial)

    demo_bank_code = request.POST.get("bank_code") if request.method == "POST" else "VCB"
    if demo_bank_code not in BANKS:
        demo_bank_code = "VCB"

    if request.method == "POST" and form.is_valid() and not coupon_error:
        discount_amount = calculate_coupon_discount(selected_coupon, subtotal, shipping_fee)

    total = max(Decimal("0"), subtotal + shipping_fee - discount_amount)

    return render(
        request,
        "shop/checkout.html",
        {
            "items": items,
            "subtotal": subtotal,
            "shipping_fee": shipping_fee,
            "discount_amount": discount_amount,
            "total": total,
            "form": form,
            "shop_bank_account": SHOP_BANK_ACCOUNT,
            "shop_account_name": SHOP_ACCOUNT_NAME,
            "demo_qr_url": build_vietqr_url(demo_bank_code, total, "DH-TAM"),
            "freeship_threshold": FREESHIP_THRESHOLD,
        },
    )


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if expire_bank_order_if_needed(order):
        messages.warning(request, "Đơn hàng quá 15 phút chưa thanh toán, hệ thống đã tự hủy.")
        return redirect("orders:order_failed", order_id=order.id)
    if order.payment_method == "bank" and not order.is_paid and order.status != "cancelled":
        return redirect("orders:bank_payment_waiting", order_id=order.id)
    if order.status == "cancelled":
        return redirect("orders:order_failed", order_id=order.id)

    qr_url = ""
    selected_bank_name = ""
    if order.payment_method == "bank" and order.bank_code in BANKS:
        selected_bank_name = BANKS[order.bank_code]["name"]
        qr_url = build_vietqr_url(order.bank_code, order.total_amount, f"DH{order.id}")

    return render(
        request,
        "shop/order_success.html",
        {
            "order": order,
            "shop_bank_account": SHOP_BANK_ACCOUNT,
            "shop_account_name": SHOP_ACCOUNT_NAME,
            "selected_bank_name": selected_bank_name,
            "qr_url": qr_url,
        },
    )


@login_required
def bank_payment_waiting(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.payment_method != "bank":
        return redirect("orders:order_success", order_id=order.id)
    if expire_bank_order_if_needed(order):
        messages.warning(request, "Đơn hàng quá 15 phút chưa thanh toán, hệ thống đã tự hủy.")
        return redirect("orders:order_failed", order_id=order.id)
    if order.is_paid:
        return redirect("orders:order_success", order_id=order.id)
    if order.status == "cancelled":
        return redirect("orders:order_failed", order_id=order.id)

    selected_bank = BANKS.get(order.bank_code) or BANKS["VCB"]
    expires_at = order.created_at + timedelta(minutes=PAYMENT_TIMEOUT_MINUTES)
    qr_url = build_vietqr_url(order.bank_code, order.total_amount, f"DH{order.id}")
    return render(
        request,
        "shop/bank_payment_waiting.html",
        {
            "order": order,
            "selected_bank_name": selected_bank["name"],
            "shop_bank_account": SHOP_BANK_ACCOUNT,
            "shop_account_name": SHOP_ACCOUNT_NAME,
            "qr_url": qr_url,
            "expires_at_iso": expires_at.isoformat(),
            "payment_timeout_minutes": PAYMENT_TIMEOUT_MINUTES,
        },
    )


@login_required
def bank_payment_status(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    expired = expire_bank_order_if_needed(order)
    state = "waiting"
    if order.status == "cancelled" or expired:
        state = "failed"
    elif order.is_paid:
        state = "success"

    return JsonResponse({"state": state, "is_paid": order.is_paid, "status": order.status})


@login_required
def order_failed(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    expired_by_timeout = "[AUTO_TIMEOUT_15_MIN]" in (order.note or "")
    reason = "expired" if expired_by_timeout else "cancelled"
    if request.GET.get("reason"):
        reason = request.GET.get("reason")
    readable_reason = "Quá 15 phút chưa thanh toán" if reason == "expired" else "Đã hủy thanh toán"
    return render(request, "shop/order_failed.html", {"order": order, "failed_reason": readable_reason})


@login_required
def order_review(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related("items__product", "items__variant"),
        id=order_id,
        user=request.user,
    )
    if expire_bank_order_if_needed(order):
        messages.warning(request, "Đơn hàng quá 15 phút chưa thanh toán, hệ thống đã tự hủy.")
        return redirect("orders:order_failed", order_id=order.id)

    editable_statuses = {"pending", "processing"}
    can_edit = (not order.is_paid) and (order.status in editable_statuses)

    if request.method == "POST":
        if not can_edit:
            messages.error(request, "Đơn hàng này không thể chỉnh sửa.")
            return redirect("orders:order_review", order_id=order.id)

        order.customer_name = request.POST.get("customer_name", "").strip() or order.customer_name
        order.customer_email = request.POST.get("customer_email", "").strip()
        phone_input = request.POST.get("phone", "").strip()
        if phone_input:
            import re
            if not re.fullmatch(r"[0-9]{9,15}", phone_input):
                messages.error(request, "Số điện thoại không hợp lệ, vui lòng chỉ nhập số (từ 9 đến 15 chữ số).")
                return redirect("orders:order_review", order_id=order.id)
            order.phone = phone_input

        order.shipping_address = request.POST.get("shipping_address", "").strip() or order.shipping_address
        order.note = request.POST.get("note", "").strip()
        if order.payment_method == "bank":
            selected_bank = request.POST.get("bank_code", "").strip().upper()
            if selected_bank in BANKS:
                order.bank_code = selected_bank
        order.save(
            update_fields=[
                "customer_name",
                "customer_email",
                "phone",
                "shipping_address",
                "note",
                "bank_code",
                "updated_at",
            ]
        )
        messages.success(request, "Đã cập nhật thông tin đơn hàng.")

        if request.POST.get("action") == "pay_now" and order.payment_method == "bank" and not order.is_paid:
            return redirect("orders:bank_payment_waiting", order_id=order.id)
        return redirect("orders:order_review", order_id=order.id)

    if order.payment_method == "bank" and not order.bank_code:
        order.bank_code = "VCB"

    qr_url = ""
    selected_bank_name = ""
    if order.payment_method == "bank" and not order.is_paid and order.status != "cancelled":
        bank_meta = BANKS.get(order.bank_code) or BANKS["VCB"]
        selected_bank_name = bank_meta["name"]
        qr_url = build_vietqr_url(order.bank_code or "VCB", order.total_amount, f"DH{order.id}")

    return render(
        request,
        "account/order_review.html",
        {
            "order": order,
            "can_edit": can_edit,
            "bank_choices": BANKS.items(),
            "selected_bank_name": selected_bank_name,
            "qr_url": qr_url,
            "shop_bank_account": SHOP_BANK_ACCOUNT,
            "shop_account_name": SHOP_ACCOUNT_NAME,
        },
    )


@login_required
@require_POST
def bank_payment_confirm(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.payment_method != "bank":
        messages.error(request, "Đơn hàng này không dùng chuyển khoản ngân hàng.")
        return redirect("orders:order_success", order_id=order.id)
    if expire_bank_order_if_needed(order):
        messages.error(request, "Đơn hàng đã quá hạn 15 phút nên không thể xác nhận thanh toán.")
        return redirect("orders:order_failed", order_id=order.id)
    if order.status == "cancelled":
        messages.error(request, "Đơn hàng đã hủy, không thể xác nhận thanh toán.")
        return redirect("orders:order_success", order_id=order.id)
    if order.is_paid:
        messages.info(request, "Đơn hàng đã được xác nhận thanh toán trước đó.")
        return redirect("orders:order_success", order_id=order.id)

    order.is_paid = True
    order.status = "processing"
    order.save(update_fields=["is_paid", "status", "updated_at"])
    messages.success(request, "Đã xác nhận thanh toán chuyển khoản.")
    return redirect("orders:order_success", order_id=order.id)


@login_required
@require_POST
def bank_payment_cancel(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.payment_method != "bank":
        messages.error(request, "Đơn hàng này không dùng chuyển khoản ngân hàng.")
        return redirect("orders:order_success", order_id=order.id)
    if order.status == "cancelled":
        messages.info(request, "Đơn hàng đã được hủy trước đó.")
        return redirect("orders:order_success", order_id=order.id)
    if order.is_paid:
        messages.error(request, "Đơn hàng đã thanh toán, không thể hủy thanh toán.")
        return redirect("orders:order_success", order_id=order.id)

    restore_order_stock(order)
    order.status = "cancelled"
    order.save(update_fields=["status", "updated_at"])
    messages.warning(request, "Đơn hàng chưa thành công do bạn đã hủy thanh toán.")
    return redirect("orders:order_failed", order_id=order.id)


@login_required
def my_orders(request):
    orders = list(Order.objects.filter(user=request.user).prefetch_related("items__product"))
    for order in orders:
        expire_bank_order_if_needed(order)
    return render(request, "account/my_orders.html", {"orders": orders})


@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, "Bạn không có quyền truy cập trang này.")
        return redirect("products:product_list")

    orders = Order.objects.all().prefetch_related("items__product")
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Tối ưu: Đếm tất cả trạng thái trong 1 câu Query duy nhất bằng aggregate
    status_counts = orders.aggregate(
        total=Count("id"),
        pending=Count("id", filter=Q(status="pending")),
        processing=Count("id", filter=Q(status="processing")),
        shipping=Count("id", filter=Q(status="shipping")),
        delivered=Count("id", filter=Q(status="delivered")),
        cancelled=Count("id", filter=Q(status="cancelled")),
    )

    total_revenue = orders.filter(status="delivered").aggregate(total=Sum("total_amount"))["total"] or 0
    month_revenue = (
        orders.filter(status="delivered", created_at__gte=month_start).aggregate(total=Sum("total_amount"))["total"] or 0
    )

    daily_revenue = (
        orders.filter(status="delivered")
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(total=Sum("total_amount"), orders_count=Count("id"))
        .order_by("-day")[:14]
    )

    recent_orders = orders.order_by("-created_at")[:10]
    low_stock_products = Product.objects.filter(available=True, stock__lte=5).order_by("stock", "name")[:10]
    active_coupons = Coupon.objects.filter(is_active=True).count()

    context = {
        "total_orders": status_counts["total"],
        "pending_orders": status_counts["pending"],
        "processing_orders": status_counts["processing"],
        "shipping_orders": status_counts["shipping"],
        "delivered_orders": status_counts["delivered"],
        "cancelled_orders": status_counts["cancelled"],
        "total_revenue": total_revenue,
        "month_revenue": month_revenue,
        "daily_revenue": daily_revenue,
        "recent_orders": recent_orders,
        "low_stock_products": low_stock_products,
        "active_coupons": active_coupons,
    }
    return render(request, "admin/dashboard.html", context)
