"""API JSON đầy đủ dùng Django views thuần (không cần thư viện mới).

Toàn bộ endpoint trả về JsonResponse, không phụ thuộc DRF/third-party.
Mount tại /api/ trong core/urls.py.
"""

from django.contrib.auth.decorators import login_required
import json

from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from core.text_utils import repair_mojibake_text
from products.models import Category, Product, Review
from users.permissions import is_staff_member

from orders.constants import BANKS, SHOP_ACCOUNT_NAME, SHOP_BANK_ACCOUNT
from orders.models import Coupon, Order
from orders.views.cart import apply_order_status_change, build_vietqr_url
from orders.views.order import build_delivery_eta, expire_bank_order_if_needed

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
        "bank_code": order.bank_code,
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
                "product_name": repair_mojibake_text(item.product.name),
                "color": item.selected_color,
                "size": item.selected_size,
                "quantity": item.quantity,
                "price": int(item.price),
                "subtotal": int(item.price * item.quantity),
            }
            for item in order.items.select_related("product")
        ]
    return data


@require_GET
def api_product_list(request: HttpRequest) -> JsonResponse:
    qs = (
        Product.objects.filter(available=True)
        .select_related("category")
        .prefetch_related("variants", "gallery_images")
    )

    category_slug = request.GET.get("category", "").strip()
    keyword = request.GET.get("q", "").strip()
    min_price = int_param(request, "min_price")
    max_price = int_param(request, "max_price")
    sort = request.GET.get("sort", "newest").strip()
    if sort not in SORT_OPTIONS:
        sort = "newest"

    if category_slug:
        qs = qs.filter(category__slug=category_slug)
    if min_price is not None:
        qs = qs.filter(price__gte=min_price)
    if max_price is not None:
        qs = qs.filter(price__lte=max_price)
    if keyword:
        qs = qs.filter(Q(name__icontains=keyword) | Q(description__icontains=keyword))

    qs = qs.order_by(SORT_OPTIONS[sort]).annotate(
        rating_avg=Avg("reviews__rating", filter=Q(reviews__is_published=True)),
        rating_count=Count("reviews", filter=Q(reviews__is_published=True)),
    )
    page = int_param(request, "page", 1)
    page_size = int_param(request, "page_size", PRODUCTS_PER_PAGE)
    page_size = min(max(page_size or PRODUCTS_PER_PAGE, 1), 50)
    paginator = Paginator(qs, page_size)
    current_page = paginator.get_page(page)

    return api_json(
        {
            "count": paginator.count,
            "page": current_page.number,
            "num_pages": paginator.num_pages,
            "page_size": page_size,
            "results": [
                _serialize_product_summary(p) for p in current_page.object_list
            ],
        }
    )


@require_GET
def api_product_detail(request: HttpRequest, pk: int) -> JsonResponse:
    product = get_object_or_404(
        Product.objects.select_related("category").prefetch_related(
            "variants", "gallery_images", "reviews__user"
        ),
        id=pk,
        available=True,
    )
    published_reviews = product.reviews.filter(is_published=True)
    review_stats = published_reviews.aggregate(
        rating_avg=Avg("rating"), rating_count=Count("id")
    )
    rating_avg = review_stats["rating_avg"] or 0
    bucket_map = {
        item["rating"]: item["total"]
        for item in published_reviews.values("rating").annotate(total=Count("id"))
    }
    review_buckets = [
        {"rating": r, "total": bucket_map.get(r, 0)} for r in range(5, 0, -1)
    ]

    data = _serialize_product_summary(product)
    data["description"] = repair_mojibake_text(product.description)
    data["featured"] = product.featured
    data["requires_variants"] = product.requires_variants
    data["variants"] = [
        _serialize_variant(v) for v in product.variants.filter(is_active=True)
    ]
    data["gallery"] = [
        {"url": item["url"], "is_placeholder": item.get("is_placeholder", False)}
        for item in product.get_detail_gallery_images()
    ]
    data["rating_avg"] = round(rating_avg, 1)
    data["rating_count"] = review_stats["rating_count"] or 0
    data["review_buckets"] = review_buckets
    data["reviews"] = [_serialize_review(r) for r in published_reviews[:50]]
    return api_json(data)


@require_GET
def api_product_reviews(request: HttpRequest, pk: int) -> JsonResponse:
    product = get_object_or_404(
        Product.objects.only("id", "name"), id=pk, available=True
    )
    reviews = product.reviews.filter(is_published=True).select_related("user")[:50]
    return api_json(
        {
            "product_id": product.id,
            "count": product.reviews.filter(is_published=True).count(),
            "results": [_serialize_review(r) for r in reviews],
        }
    )


@login_required
@require_POST
def api_review_submit(request: HttpRequest, pk: int) -> JsonResponse:
    product = get_object_or_404(
        Product.objects.only("id", "name"), id=pk, available=True
    )
    try:
        rating = int(request.POST.get("rating", request.GET.get("rating", "")))
    except (TypeError, ValueError):
        return api_error("rating phải là số từ 1 đến 5.")
    if rating not in range(1, 6):
        return api_error("rating phải là số từ 1 đến 5.")
    comment = request.POST.get("comment", "").strip()

    if product.reviews.filter(user=request.user).exists():
        return api_error("Bạn đã đánh giá sản phẩm này rồi.", status=409)

    from orders.models import OrderItem

    verified = OrderItem.objects.filter(
        order__user=request.user, order__status="delivered", product=product
    ).exists()
    review = Review.objects.create(
        product=product,
        user=request.user,
        rating=rating,
        comment=comment,
        verified_purchase=verified,
    )
    return api_json({"success": True, "review": _serialize_review(review)}, status=201)


@require_GET
def api_categories(request: HttpRequest) -> JsonResponse:
    categories = Category.objects.annotate(
        product_count=Count("products", filter=Q(products__available=True))
    ).order_by("name")
    return api_json(
        [
            {
                "id": c.id,
                "name": repair_mojibake_text(c.name),
                "slug": c.slug,
                "product_count": c.product_count,
            }
            for c in categories
        ]
    )


@login_required
@require_GET
def api_my_orders(request: HttpRequest) -> JsonResponse:
    qs = (
        Order.objects.all()
        if is_staff_member(request.user)
        else Order.objects.filter(user=request.user)
    )
    orders = list(qs.prefetch_related("items__product").order_by("-created_at")[:200])
    for order in orders:
        expire_bank_order_if_needed(order)
    return api_json([_serialize_order(o) for o in orders])


@login_required
@require_GET
def api_order_detail(request: HttpRequest, pk: int) -> JsonResponse:
    lookup = {"id": pk}
    if not is_staff_member(request.user):
        lookup["user"] = request.user
    order = get_object_or_404(
        Order.objects.prefetch_related("items__product"), **lookup
    )
    expire_bank_order_if_needed(order)
    data = _serialize_order(order, include_items=True)
    if order.payment_method == "bank":
        data["bank"] = {
            "code": order.bank_code,
            "name": (BANKS.get(order.bank_code) or {}).get("name", ""),
        }
        if not order.is_paid and order.status != "cancelled":
            data["qr_url"] = build_vietqr_url(
                order.bank_code or "VCB", order.total_amount, f"DH{order.id}"
            )
    eta = build_delivery_eta(order)
    data["eta_label"] = eta["eta_label"]
    data["eta_date"] = eta["eta_date"].isoformat()
    return api_json(data)


@require_POST
def api_order_lookup(request: HttpRequest) -> JsonResponse:
    order_id = request.POST.get("order_id", "").strip()
    phone = request.POST.get("phone", "").strip()
    if not order_id.isdigit() or not phone:
        return api_error("Cần cung cấp order_id và phone.")
    try:
        order = Order.objects.get(id=order_id, phone=phone)
    except Order.DoesNotExist:
        return api_error(
            "Không tìm thấy đơn hàng với mã và số điện thoại này.", status=404
        )
    expire_bank_order_if_needed(order)
    return api_json(_serialize_order(order, include_items=True))


@login_required
@require_POST
def api_coupon_check(request: HttpRequest) -> JsonResponse:
    code = request.POST.get("code", "").strip()
    if not code:
        return api_error("Thiếu mã giảm giá.")
    coupon = Coupon.objects.filter(code__iexact=code).first()
    if not coupon:
        return api_error("Mã giảm giá không tồn tại.", status=404)
    if not coupon.is_usable_now():
        return api_error("Mã giảm giá đã hết hạn hoặc ngừng hoạt động.")
    if not coupon.is_usable_by_user(request.user):
        return api_error("Bạn đã dùng hết lượt cho mã giảm giá này.")
    return api_json(
        {
            "code": coupon.code,
            "discount_type": coupon.discount_type,
            "value": int(coupon.value),
            "min_order_amount": int(coupon.min_order_amount),
            "max_discount_amount": int(coupon.max_discount_amount)
            if coupon.max_discount_amount is not None
            else None,
            "label": coupon.get_discount_type_display(),
        }
    )


def _staff_required(request):
    if not is_staff_member(request.user):
        return api_error("Bạn không có quyền truy cập API này.", status=403)


def _serialize_admin_order(order):
    return _serialize_order(order, include_items=True)


@login_required
@require_GET
def api_admin_stats(request: HttpRequest) -> JsonResponse:
    denied = _staff_required(request)
    if denied:
        return denied

    from orders.admin_product_dashboard import build_admin_dashboard_context

    context = build_admin_dashboard_context(current_user=request.user)
    payload = {
        "total_orders": context["total_orders"],
        "pending_orders": context["pending_orders"],
        "processing_orders": context["processing_orders"],
        "shipping_orders": context["shipping_orders"],
        "delivered_orders": context["delivered_orders"],
        "cancelled_orders": context["cancelled_orders"],
        "total_revenue": context["total_revenue"],
        "month_revenue": context["month_revenue"],
        "today_orders": context["today_orders"],
        "today_revenue": context["today_revenue"],
        "today_new_accounts": context["today_new_accounts"],
        "active_coupons": context["active_coupons"],
        "growth_pct": context["revenue_growth_pct"],
        "growth_label": context["revenue_growth_label"],
        "revenue_chart": context["revenue_chart"],
        "orders_chart": context["orders_chart"],
        "status_chart": context["status_chart"],
        "top_products": context["top_products"],
        "category_revenue": context["category_revenue"],
        "inventory_stats": context["inventory_stats"],
        "low_stock_products": [
            {
                "id": p.id,
                "name": repair_mojibake_text(p.name),
                "stock": p.stock,
                "available": p.available,
            }
            for p in context["low_stock_products"]
        ],
    }
    return api_json(payload)


@login_required
@require_GET
def api_admin_orders(request: HttpRequest) -> JsonResponse:
    denied = _staff_required(request)
    if denied:
        return denied

    qs = Order.objects.prefetch_related("items__product").order_by("-created_at")
    status = request.GET.get("status", "").strip()
    if status and status in dict(Order.STATUS_CHOICES):
        qs = qs.filter(status=status)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(id__icontains=q) | Q(customer_name__icontains=q) | Q(phone__icontains=q)
        )
    page = int_param(request, "page", 1)
    page_size = int_param(request, "page_size", 20)
    page_size = min(max(page_size or 20, 1), 100)
    paginator = Paginator(qs, page_size)
    current_page = paginator.get_page(page)
    return api_json(
        {
            "count": paginator.count,
            "page": current_page.number,
            "num_pages": paginator.num_pages,
            "page_size": page_size,
            "results": [_serialize_admin_order(o) for o in current_page.object_list],
        }
    )


@login_required
@require_GET
def api_admin_order_detail(request: HttpRequest, pk: int) -> JsonResponse:
    denied = _staff_required(request)
    if denied:
        return denied
    order = get_object_or_404(Order.objects.prefetch_related("items__product"), id=pk)
    data = _serialize_admin_order(order)
    if order.payment_method == "bank":
        data["bank"] = {
            "code": order.bank_code,
            "name": (BANKS.get(order.bank_code) or {}).get("name", ""),
        }
    return api_json(data)


@login_required
@require_POST
def api_admin_order_status(request: HttpRequest, pk: int) -> JsonResponse:
    denied = _staff_required(request)
    if denied:
        return denied
    order = get_object_or_404(Order, id=pk)
    new_status = request.POST.get("status", "").strip()
    if new_status not in dict(Order.STATUS_CHOICES):
        return api_error("Trạng thái không hợp lệ.")
    is_paid = request.POST.get("is_paid", "").strip() in ("1", "true", "on")
    try:
        apply_order_status_change(order, new_status, is_paid=is_paid)
    except ValueError as exc:
        return api_error(str(exc))
    return api_json(
        {
            "success": True,
            "id": order.id,
            "status": order.status,
            "status_label": order.get_status_display(),
            "is_paid": order.is_paid,
        }
    )


@login_required
@require_POST
def api_admin_order_refund(request: HttpRequest, pk: int) -> JsonResponse:
    denied = _staff_required(request)
    if denied:
        return denied
    order = get_object_or_404(Order, id=pk)
    if order.status == "cancelled":
        return api_error("Đơn hàng này đã được hủy/hoàn tiền trước đó.")
    was_paid = order.is_paid
    amount = int(order.total_amount)
    try:
        apply_order_status_change(order, "cancelled", is_paid=False)
    except ValueError as exc:
        return api_error(str(exc))
    refund_note = (
        f"[REFUND {amount}đ] {request.user.username} {timezone.now():%d/%m/%Y %H:%M}"
    )
    order.note = f"{order.note}\n{refund_note}".strip() if order.note else refund_note
    order.save(update_fields=["note", "updated_at"])
    return api_json(
        {
            "success": True,
            "id": order.id,
            "status": order.status,
            "was_paid": was_paid,
            "refund_amount": amount,
            "refunded": was_paid,
        }
    )


@login_required
@require_GET
def api_admin_invoice(request: HttpRequest, pk: int) -> JsonResponse:
    denied = _staff_required(request)
    if denied:
        return denied
    order = get_object_or_404(Order.objects.prefetch_related("items__product"), id=pk)
    data = _serialize_admin_order(order)
    data["shop"] = {
        "name": "HUUGIAU LOCAL BRAND",
        "bank_account": SHOP_BANK_ACCOUNT,
        "account_name": SHOP_ACCOUNT_NAME,
    }
    return api_json(data)


@login_required
@require_GET
def api_admin_export(request: HttpRequest) -> JsonResponse:
    denied = _staff_required(request)
    if denied:
        return denied
    status = request.GET.get("status", "").strip()
    qs = Order.objects.prefetch_related("items__product").order_by("-created_at")
    if status and status in dict(Order.STATUS_CHOICES):
        qs = qs.filter(status=status)
    return api_json([_serialize_admin_order(o) for o in qs])


@login_required
@require_GET
def api_admin_products(request: HttpRequest) -> JsonResponse:
    denied = _staff_required(request)
    if denied:
        return denied
    qs = (
        Product.objects.select_related("category")
        .prefetch_related("variants")
        .order_by("-created")
    )
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(category__name__icontains=q))
    results = []
    for product in qs[:500]:
        row = {
            "id": product.id,
            "slug": product.slug,
            "name": repair_mojibake_text(product.name),
            "category": repair_mojibake_text(product.category.name),
            "price": int(product.price),
            "stock": product.stock,
            "available": product.available,
            "featured": product.featured,
            "image": product.get_image(),
            "variants": [_serialize_variant(v) for v in product.variants.all()],
        }
        results.append(row)
    return api_json({"count": len(results), "results": results})


@login_required
@require_GET
def api_admin_users(request: HttpRequest) -> JsonResponse:
    denied = _staff_required(request)
    if denied:
        return denied
    from django.contrib.auth import get_user_model

    UserModel = get_user_model()
    users = UserModel.objects.annotate(
        order_count=Count("orders", distinct=True),
        review_count=Count("reviews", distinct=True),
    ).order_by("-is_superuser", "-is_staff", "-date_joined")
    return api_json(
        [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "is_staff": u.is_staff,
                "is_superuser": u.is_superuser,
                "role": (
                    "admin" if u.is_superuser else ("staff" if u.is_staff else "user")
                ),
                "order_count": u.order_count,
                "review_count": u.review_count,
                "date_joined": u.date_joined.isoformat(),
            }
            for u in users[:500]
        ]
    )


@login_required
@require_GET
def api_admin_coupons(request: HttpRequest) -> JsonResponse:
    denied = _staff_required(request)
    if denied:
        return denied
    coupons = Coupon.objects.annotate(
        redemption_count=Count("redemptions", distinct=True)
    ).order_by("-created_at")
    return api_json(
        [
            {
                "id": c.id,
                "code": c.code,
                "discount_type": c.discount_type,
                "discount_label": c.get_discount_type_display(),
                "value": int(c.value),
                "min_order_amount": int(c.min_order_amount),
                "max_discount_amount": int(c.max_discount_amount)
                if c.max_discount_amount is not None
                else None,
                "is_active": c.is_active,
                "usage_limit": c.usage_limit,
                "max_uses_per_user": c.max_uses_per_user,
                "used_count": c.used_count,
                "redemption_count": c.redemption_count,
                "starts_at": c.starts_at.isoformat() if c.starts_at else None,
                "ends_at": c.ends_at.isoformat() if c.ends_at else None,
            }
            for c in coupons
        ]
    )


@login_required
def api_admin_reviews(request: HttpRequest) -> JsonResponse:
    denied = _staff_required(request)
    if denied:
        return denied

    if request.method == "POST":
        review = get_object_or_404(Review, id=request.POST.get("review_id"))
        publish_raw = request.POST.get("is_published", "").strip()
        if publish_raw in ("1", "true", "on"):
            review.is_published = True
        elif publish_raw in ("0", "false", "off"):
            review.is_published = False
        review.save(update_fields=["is_published"])
        return api_json(
            {"success": True, "id": review.id, "is_published": review.is_published}
        )

    reviews = Review.objects.select_related("product", "user").order_by("-created")
    status = request.GET.get("status", "").strip()
    if status in ("published", "hidden"):
        show = status == "published"
        reviews = reviews.filter(is_published=show)
    reviews = reviews[:500]
    return api_json(
        {
            "count": len(reviews),
            "results": [
                {
                    "id": r.id,
                    "product_id": r.product_id,
                    "product_name": repair_mojibake_text(r.product.name),
                    "user": r.user.username,
                    "rating": r.rating,
                    "comment": repair_mojibake_text(r.comment),
                    "is_published": r.is_published,
                    "verified_purchase": r.verified_purchase,
                    "created": r.created.isoformat(),
                }
                for r in reviews
            ],
        }
    )


@csrf_exempt
def api_geocode(request: HttpRequest) -> JsonResponse:
    """Geoapify Geocoding proxy: search forward or reverse without exposing the key."""
    import urllib.parse
    import urllib.request
    from django.conf import settings

    key = getattr(settings, "GEOAPIFY_API_KEY", "")
    if not key:
        return api_json({"error": "Chưa cấu hình GEOAPIFY_API_KEY."}, status=503)

    lat = request.GET.get("lat")
    lng = request.GET.get("lng")
    q = request.GET.get("q")

    lang = "vi"

    if q:
        params = {
            "text": q,
            "apiKey": key,
            "lang": lang,
            "filter": "countrycode:vn",
            "limit": 1,
        }
        end = "https://api.geoapify.com/v1/geocode/search?" + urllib.parse.urlencode(
            params
        )
    elif lat and lng:
        params = {"lat": lat, "lon": lng, "apiKey": key, "lang": lang}
        end = "https://api.geoapify.com/v1/geocode/reverse?" + urllib.parse.urlencode(
            params
        )
    else:
        return api_json({"error": "Thiếu q hoặc lat/lng."}, status=400)

    try:
        with urllib.request.urlopen(end, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception:
        return api_json({"error": "Không gọi được Geoapify."}, status=502)

    if data.get("features"):
        r = data["features"][0]
        p = r.get("properties", {})
        loc = r.get("geometry", {}).get("coordinates", [])
        return api_json(
            {
                "lat": loc[1] if len(loc) == 2 else None,
                "lng": loc[0] if len(loc) == 2 else None,
                "address": p.get("formatted") or p.get("address_line2") or "",
            }
        )
    return api_json({"error": "Không tìm thấy địa chỉ."}, status=404)


@csrf_exempt
def api_root(request: HttpRequest) -> JsonResponse:
    endpoints = {
        "products": "/api/products/",
        "product_detail": "/api/products/<id>/",
        "product_reviews": "/api/products/<id>/reviews/",
        "categories": "/api/categories/",
        "orders": "/api/orders/",
        "order_detail": "/api/orders/<id>/",
        "order_lookup": "/api/orders/lookup/",
        "coupon_check": "/api/coupons/check/",
        "geocode": "/api/geocode/?q=... | ?lat=...&lng=...",
        "admin": {
            "stats": "/api/admin/stats/",
            "orders": "/api/admin/orders/",
            "order_detail": "/api/admin/orders/<id>/",
            "order_status": "/api/admin/orders/<id>/status/",
            "order_refund": "/api/admin/orders/<id>/refund/",
            "invoice": "/api/admin/orders/<id>/invoice/",
            "export": "/api/admin/export/",
            "products": "/api/admin/products/",
            "users": "/api/admin/users/",
            "coupons": "/api/admin/coupons/",
            "reviews": "/api/admin/reviews/",
        },
    }
    return api_json(
        {"name": "HUUGIAU Fashion API", "version": "1.0", "endpoints": endpoints}
    )


@login_required
@require_GET
def api_gdpr_export(request: HttpRequest) -> JsonResponse:
    """GDPR Art. 15/20: Xuất toàn bộ dữ liệu cá nhân của user."""
    from orders.models import Order, CouponRedemption, ReturnRequest, GiftCardUsage
    from products.models import (
        Review,
        WishlistItem,
        ProductQuestion,
        BackInStock,
        NewsletterSubscriber,
    )
    from users.models import (
        UserAddress,
        UserProfile,
        VisitorSession,
        UserActivity,
        ReferralCode,
        ReferralReward,
    )

    user = request.user

    # Basic user data
    data = {
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "date_joined": user.date_joined.isoformat() if user.date_joined else None,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "is_active": user.is_active,
        },
        "profile": {},
        "addresses": [],
        "orders": [],
        "coupon_redemptions": [],
        "returns": [],
        "gift_card_usages": [],
        "reviews": [],
        "wishlist": [],
        "questions": [],
        "back_in_stock_requests": [],
        "newsletter": [],
        "visitor_sessions": [],
        "activities": [],
        "referral_codes": [],
        "referral_rewards": [],
    }

    # Profile
    try:
        profile = UserProfile.objects.get(user=user)
        data["profile"] = {
            "phone_number": profile.phone_number,
            "birthday": profile.birthday.isoformat() if profile.birthday else None,
            "points": profile.points,
            "points_expire_at": profile.points_expire_at.isoformat()
            if profile.points_expire_at
            else None,
        }
    except Exception:
        pass

    # Addresses
    for addr in UserAddress.objects.filter(user=user).values():
        data["addresses"].append(addr)

    # Orders
    for order in Order.objects.filter(user=user).prefetch_related(
        "items__product", "items__variant"
    ):
        data["orders"].append(
            {
                "id": order.id,
                "status": order.status,
                "total_amount": str(order.total_amount),
                "created_at": order.created_at.isoformat(),
                "items": [
                    {
                        "product_id": item.product_id,
                        "variant_id": item.variant_id,
                        "quantity": item.quantity,
                        "price": str(item.price),
                    }
                    for item in order.items.all()
                ],
            }
        )

    # Coupon redemptions
    for cr in CouponRedemption.objects.filter(user=user).select_related("coupon"):
        data["coupon_redemptions"].append(
            {
                "coupon_code": cr.coupon.code,
                "order_id": cr.order_id,
                "redeemed_at": cr.redeemed_at.isoformat() if cr.redeemed_at else None,
            }
        )

    # Returns
    for ret in ReturnRequest.objects.filter(order__user=user).select_related("order"):
        data["returns"].append(
            {
                "id": ret.id,
                "order_id": ret.order_id,
                "return_type": ret.return_type,
                "reason": ret.reason,
                "status": ret.status,
                "created_at": ret.created_at.isoformat(),
            }
        )

    # Gift card usages
    for gcu in GiftCardUsage.objects.filter(user=user).select_related("gift_card"):
        data["gift_card_usages"].append(
            {
                "gift_card_code": gcu.gift_card.code,
                "amount": str(gcu.amount),
                "used_at": gcu.used_at.isoformat() if gcu.used_at else None,
            }
        )

    # Reviews
    for rev in Review.objects.filter(user=user).select_related("product"):
        data["reviews"].append(
            {
                "product_id": rev.product_id,
                "rating": rev.rating,
                "comment": rev.comment,
                "created_at": rev.created_at.isoformat(),
            }
        )

    # Wishlist
    for wi in WishlistItem.objects.filter(user=user).select_related("product"):
        data["wishlist"].append(
            {
                "product_id": wi.product_id,
                "created_at": wi.created_at.isoformat(),
            }
        )

    # Questions
    for q in ProductQuestion.objects.filter(user=user).select_related("product"):
        data["questions"].append(
            {
                "product_id": q.product_id,
                "question": q.question,
                "answer": q.answer,
                "created_at": q.created_at.isoformat(),
            }
        )

    # Back in stock
    for bs in BackInStock.objects.filter(user=user).select_related("product"):
        data["back_in_stock_requests"].append(
            {
                "product_id": bs.product_id,
                "created_at": bs.created_at.isoformat(),
            }
        )

    # Newsletter
    try:
        from products.models import NewsletterSubscriber

        ns = NewsletterSubscriber.objects.filter(email=user.email).first()
        if ns:
            data["newsletter"] = {
                "email": ns.email,
                "is_active": ns.is_active,
                "subscribed_at": ns.subscribed_at.isoformat()
                if ns.subscribed_at
                else None,
            }
    except Exception:
        pass

    # Visitor sessions
    for vs in VisitorSession.objects.filter(user=user).values():
        data["visitor_sessions"].append(vs)

    # Activities
    for act in UserActivity.objects.filter(user=user).values():
        data["activities"].append(act)

    # Referral codes
    for rc in ReferralCode.objects.filter(user=user).values():
        data["referral_codes"].append(rc)

    # Referral rewards
    for rr in (
        ReferralReward.objects.filter(user=user)
        .select_related("referral_code")
        .values()
    ):
        data["referral_rewards"].append(rr)

    # Return as downloadable JSON
    from django.http import HttpResponse
    import json

    filename = f"gdpr-export-user-{user.id}-{timezone.now().strftime('%Y%m%d')}.json"
    resp = HttpResponse(
        json.dumps(data, ensure_ascii=False, indent=2),
        content_type="application/json; charset=utf-8",
    )
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    return resp


@login_required
@require_POST
def api_gdpr_delete(request: HttpRequest) -> JsonResponse:
    """GDPR Art. 17: Xóa tài khoản và dữ liệu liên quan (Right to be Forgotten)."""
    user = request.user

    # Confirm password
    import json

    try:
        payload = json.loads(request.body)
        password = payload.get("password", "")
    except Exception:
        password = request.POST.get("password", "")

    if not user.check_password(password):
        return api_error("Mật khẩu không đúng.", status=400)

    user_id = user.id
    username = user.username
    email = user.email

    # Soft delete: anonymize instead of hard delete to preserve referential integrity
    user.username = f"deleted_{user_id}"
    user.email = f"deleted_{user_id}@example.com"
    user.first_name = ""
    user.last_name = ""
    user.is_active = False
    user.set_unusable_password()
    user.save()

    return api_json(
        {
            "success": True,
            "message": f"Tài khoản {username} ({email}) đã được ẩn danh và vô hiệu hóa.",
        }
    )


@require_GET
def api_gdpr_guest_export(request: HttpRequest) -> JsonResponse:
    """GDPR export cho guest order (tra cứu bằng order_id + phone/email)."""
    order_id = request.GET.get("order_id")
    phone = request.GET.get("phone")
    email = request.GET.get("email")

    if not order_id or not (phone or email):
        return api_error("Thiếu order_id và phone/email.", status=400)

    from orders.models import Order

    try:
        order = Order.objects.get(id=order_id)
    except Exception:
        return api_error("Không tìm thấy đơn hàng.", status=404)

    # Verify identity
    if phone and order.phone != phone:
        return api_error("Số điện thoại không khớp.", status=403)
    if email and order.customer_email != email:
        return api_error("Email không khớp.", status=403)

    data = {
        "order": {
            "id": order.id,
            "customer_name": order.customer_name,
            "customer_email": order.customer_email,
            "phone": order.phone,
            "shipping_address": order.shipping_address,
            "status": order.status,
            "total_amount": str(order.total_amount),
            "created_at": order.created_at.isoformat(),
        }
    }

    from django.http import HttpResponse
    import json

    filename = f"gdpr-guest-order-{order.id}.json"
    resp = HttpResponse(
        json.dumps(data, ensure_ascii=False, indent=2),
        content_type="application/json; charset=utf-8",
    )
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    return resp
