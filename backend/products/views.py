import json
from typing import Optional

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q, Sum
from django.db.models.functions import Coalesce
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from core.text_utils import normalize_vn_text, repair_mojibake_text
from core.ratelimit import rate_limit
from urllib.parse import quote

from .constants import FEATURED_PRODUCT_LIMIT, get_category_type_label
from orders.models import OrderItem
from .models import (
    BackInStock,
    BlogPost,
    Category,
    MAX_PRODUCT_GALLERY_IMAGES,
    NewsletterSubscriber,
    Product,
    ProductQuestion,
    ProductVariant,
    Review,
    WishlistItem,
)
from .services.chat_service import (
    build_support_reply,
)

SOLD_STATUSES = ("delivered", "shipping", "processing")


def build_sold_map(product_ids):
    """{product_id: sold_count} — tách riêng khỏi queryset để tránh
    subquery bên trong GROUP BY (SQL Server không hỗ trợ)."""
    if not product_ids:
        return {}
    rows = (
        OrderItem.objects.filter(
            product_id__in=product_ids, order__status__in=SOLD_STATUSES
        )
        .values("product_id")
        .annotate(total=Sum("quantity"))
    )
    return {row["product_id"]: row["total"] for row in rows}


def attach_sold_counts(products):
    sold_map = build_sold_map([p.id for p in products])
    for product in products:
        product.sold_count = sold_map.get(product.id, 0)
    return products


LOW_STOCK_THRESHOLD = 5


def attach_low_stock(products, threshold=LOW_STOCK_THRESHOLD):
    """Đánh dấu p.low_stock=True khi còn ≤ threshold (1 query cho cả trang)."""
    product_ids = [p.id for p in products]
    variant_map = {}
    if product_ids:
        rows = (
            ProductVariant.objects.filter(product_id__in=product_ids, is_active=True)
            .values("product_id")
            .annotate(total=Sum("stock"))
        )
        variant_map = {row["product_id"]: row["total"] for row in rows}
    for product in products:
        total = variant_map.get(product.id)
        stock = total if total is not None else product.stock
        product.low_stock = 0 < stock <= threshold
    return products


SORT_OPTIONS = {
    "newest": "-created",
    "bestseller": "-sold_total",
    "price_asc": "price",
    "price_desc": "-price",
    "rating": "-rating_avg",
    "name_asc": "name",
}
PRODUCTS_PER_PAGE = 12
SUPPORT_CHAT_SESSION_KEY = "support_chat_state"
DETAIL_GALLERY_SLOT_COUNT = MAX_PRODUCT_GALLERY_IMAGES

COLOR_DISPLAY_MAP = {
    "den": "Đen",
    "đen": "Đen",
    "trang": "Trắng",
    "trắng": "Trắng",
    "do": "Đỏ",
    "đỏ": "Đỏ",
    "xanh": "Xanh",
    "xam": "Xám",
    "xám": "Xám",
    "nau": "Nâu",
    "nâu": "Nâu",
    "be": "Be",
    "kem": "Kem",
}


def parse_price(value: str) -> Optional[int]:
    if not value:
        return None
    try:
        cleaned = str(value).replace(".", "").replace(",", "").replace(" ", "").strip()
        parsed = int(cleaned)
        return parsed if parsed >= 0 else None
    except (TypeError, ValueError):
        return None


def format_color_label(color_name: str) -> str:
    repaired = repair_mojibake_text(color_name)
    normalized = normalize_vn_text(repaired).strip()
    if normalized in COLOR_DISPLAY_MAP:
        return COLOR_DISPLAY_MAP[normalized]
    return repaired


def build_gallery_placeholder(product: Product, slot_index: int) -> str:

    category_label = normalize_vn_text(
        get_category_type_label(product.category.slug)
    ).upper()
    slot_label = f"{slot_index + 1:02d}"
    svg = f"""
    <svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 900 900'>
        <defs>
            <linearGradient id='bg' x1='0' y1='0' x2='1' y2='1'>
                <stop offset='0%' stop-color='#fffdf8' />
                <stop offset='100%' stop-color='#f1e1d0' />
            </linearGradient>
        </defs>
        <rect width='900' height='900' rx='40' fill='url(#bg)' />
        <rect x='64' y='64' width='772' height='772' rx='36' fill='none' stroke='#d7bda8' stroke-dasharray='18 14' />
        <text x='450' y='410' text-anchor='middle' fill='#8f4f2a' font-family='Arial, sans-serif' font-size='54' font-weight='700' letter-spacing='12'>{category_label}</text>
        <text x='450' y='500' text-anchor='middle' fill='#4c3729' font-family='Arial, sans-serif' font-size='96' font-weight='800'>{slot_label}</text>
        <text x='450' y='574' text-anchor='middle' fill='#7b6758' font-family='Arial, sans-serif' font-size='28'>CHUA CO HINH</text>
    </svg>
    """.strip()
    return f"data:image/svg+xml;utf8,{quote(svg)}"


def build_detail_gallery_slots(product: Product, gallery_images: list) -> list:
    actual_images = list(gallery_images[:DETAIL_GALLERY_SLOT_COUNT])
    slots = []

    for index in range(DETAIL_GALLERY_SLOT_COUNT):
        if index < len(actual_images):
            image = actual_images[index]
            slots.append(
                {
                    "url": image["url"],
                    "thumb_url": image["url"],
                    "alt": f"{product.name} - ảnh {index + 1}",
                    "is_placeholder": False,
                    "slot_index": index,
                }
            )
        else:
            placeholder_url = build_gallery_placeholder(product, index)
            slots.append(
                {
                    "url": placeholder_url,
                    "thumb_url": placeholder_url,
                    "alt": f"{product.name} - slot {index + 1}",
                    "is_placeholder": True,
                    "slot_index": index,
                }
            )

    return slots


def get_support_chat_state(request: HttpRequest) -> dict:
    state = request.session.get(SUPPORT_CHAT_SESSION_KEY) or {}
    if not isinstance(state, dict):
        return {}
    return {
        "topic": state.get("topic", ""),
        "height_cm": state.get("height_cm"),
        "weight_kg": state.get("weight_kg"),
        "pending": state.get("pending", ""),
    }


def save_support_chat_state(request: HttpRequest, state: dict) -> None:
    request.session[SUPPORT_CHAT_SESSION_KEY] = {
        "topic": state.get("topic", ""),
        "height_cm": state.get("height_cm"),
        "weight_kg": state.get("weight_kg"),
        "pending": state.get("pending", ""),
    }
    request.session.modified = True


def product_list(request: HttpRequest) -> HttpResponse:
    base_products = (
        Product.objects.filter(available=True)
        .select_related("category")
        .prefetch_related("variants", "gallery_images")
    )
    products_qs = base_products
    categories = list(Category.objects.all())

    category_slug = request.GET.get("category", "").strip()
    keyword = request.GET.get("q", "").strip()
    min_price_raw = request.GET.get("min_price", "").strip()
    max_price_raw = request.GET.get("max_price", "").strip()
    selected_sizes = list(
        dict.fromkeys(
            item.upper() for item in request.GET.getlist("size") if item.strip()
        )
    )
    selected_color_keys = list(
        dict.fromkeys(
            normalize_vn_text(item)
            for item in request.GET.getlist("color")
            if item.strip()
        )
    )
    selected_colors = [
        COLOR_DISPLAY_MAP.get(item, item.title()) for item in selected_color_keys
    ]
    selected_sort = request.GET.get("sort", "newest").strip()

    min_price = parse_price(min_price_raw)
    max_price = parse_price(max_price_raw)
    if selected_sort not in SORT_OPTIONS:
        selected_sort = "newest"

    selected_category = None
    slider_products = []
    is_random_home = False

    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        products_qs = products_qs.filter(category=selected_category)

    if min_price is not None:
        products_qs = products_qs.filter(price__gte=min_price)
    if max_price is not None:
        products_qs = products_qs.filter(price__lte=max_price)

    if keyword:
        normalized_keyword = normalize_vn_text(keyword)

        db_matched = products_qs.filter(
            Q(name__icontains=keyword) | Q(description__icontains=keyword)
        )
        db_ids = list(db_matched.values_list("id", flat=True))
        merged_ids = list(db_ids)

        accent_candidates = products_qs.exclude(id__in=db_ids).values(
            "id", "name", "description"
        )[:500]
        for item in accent_candidates:
            if normalized_keyword in normalize_vn_text(
                item["name"]
            ) or normalized_keyword in normalize_vn_text(item["description"]):
                merged_ids.append(item["id"])

        products_qs = products_qs.filter(id__in=merged_ids)

    if selected_sizes:
        products_qs = products_qs.filter(variants__size__in=selected_sizes).distinct()

    if selected_colors:
        products_qs = products_qs.filter(
            variants__color_name__in=selected_colors
        ).distinct()

    no_filter_mode = (
        not any([category_slug, keyword, min_price_raw, max_price_raw])
        and selected_sort == "newest"
    )
    if no_filter_mode:
        is_random_home = True
        featured_qs = (
            base_products.filter(featured=True)
            .order_by("id")
            .annotate(
                rating_avg=Avg("reviews__rating", filter=Q(reviews__is_published=True)),
                rating_count=Count("reviews", filter=Q(reviews__is_published=True)),
            )
        )
        slider_products = list(featured_qs[:FEATURED_PRODUCT_LIMIT])

        if slider_products:
            # Ponytail: reuse the already-loaded (prefetched) list instead of
            # re-evaluating featured_qs for the grid -> halves home page queries.
            products_qs = slider_products
        else:
            products_qs = base_products.order_by("id")
    else:
        if not isinstance(products_qs, list):
            products_qs = products_qs.annotate(
                rating_avg=Coalesce(
                    Avg("reviews__rating", filter=Q(reviews__is_published=True)), 0.0
                ),
                rating_count=Count("reviews", filter=Q(reviews__is_published=True)),
            )
        if selected_sort == "bestseller":
            # Ponytail: python-sort to avoid JOIN multiplication between
            # variant filters and the order_items aggregate (SQL Server).
            page_all = list(products_qs)
            sold_map = build_sold_map([p.id for p in page_all])
            page_all.sort(key=lambda p: (-sold_map.get(p.id, 0), p.id))
            products_qs = page_all
        else:
            products_qs = products_qs.order_by(SORT_OPTIONS[selected_sort])

    if not isinstance(products_qs, list):
        products_qs = products_qs.annotate(
            rating_avg=Coalesce(
                Avg("reviews__rating", filter=Q(reviews__is_published=True)), 0.0
            ),
            rating_count=Count("reviews", filter=Q(reviews__is_published=True)),
        )
    paginator = Paginator(products_qs, PRODUCTS_PER_PAGE)
    products = paginator.get_page(request.GET.get("page"))
    attach_sold_counts(list(products))
    attach_low_stock(list(products))

    trust_stats = None
    if is_random_home:
        sold = OrderItem.objects.filter(order__status__in=SOLD_STATUSES).aggregate(
            total=Sum("quantity")
        )
        review_agg = Review.objects.filter(is_published=True).aggregate(
            avg=Avg("rating"), count=Count("id")
        )
        trust_stats = {
            "sold_total": sold["total"] or 0,
            "review_avg": round(review_agg["avg"] or 0, 1),
            "review_count": review_agg["count"] or 0,
        }

    def build_catalog_query(**overrides: str) -> str:
        params = request.GET.copy()
        params.pop("page", None)
        for key, value in overrides.items():
            params.pop(key, None)
            if value in (None, ""):
                continue
            params[key] = str(value)
        return params.urlencode()

    for category in categories:
        category.catalog_query = build_catalog_query(category=category.slug)

    sidebar_sort_links = {key: build_catalog_query(sort=key) for key in SORT_OPTIONS}

    variant_qs = ProductVariant.objects.filter(product__available=True, is_active=True)

    available_sizes = list(
        variant_qs.values_list("size", flat=True).distinct().order_by()
    )
    size_order = {
        "XXS": 0,
        "XS": 1,
        "S": 2,
        "M": 3,
        "L": 4,
        "XL": 5,
        "XXL": 6,
        "3XL": 7,
        "4XL": 8,
    }
    sidebar_size_options = sorted(
        [s.strip().upper() for s in available_sizes if s and s.strip()],
        key=lambda item: (size_order.get(item, 99), item),
    )

    available_colors = list(
        variant_qs.values("color_name", "color_code").distinct().order_by()
    )
    sidebar_color_map = {}
    for row in available_colors:
        color_name = row["color_name"]
        if not color_name:
            continue
        color_key = normalize_vn_text(color_name)
        if color_key and color_key not in sidebar_color_map:
            sidebar_color_map[color_key] = {
                "value": color_key,
                "label": format_color_label(color_name),
                "code": row.get("color_code") or "#4d8fe6",
            }
    sidebar_color_options = sorted(
        sidebar_color_map.values(), key=lambda item: item["label"]
    )

    query_params = request.GET.copy()
    query_params.pop("page", None)
    query_without_page = query_params.urlencode()

    wishlist_product_ids = set()
    if request.user.is_authenticated and products:
        visible_ids = [item.id for item in products.object_list]
        wishlist_product_ids = set(
            WishlistItem.objects.filter(
                user=request.user, product_id__in=visible_ids
            ).values_list("product_id", flat=True)
        )

    context = {
        "products": products,
        "total_products": paginator.count,
        "site_total_products": base_products.count(),
        "categories": categories,
        "selected_category": selected_category,
        "keyword": keyword,
        "slider_products": slider_products,
        "is_random_home": is_random_home,
        "trust_stats": trust_stats,
        "selected_sort": selected_sort,
        "min_price": min_price_raw,
        "max_price": max_price_raw,
        "selected_sizes": selected_sizes,
        "selected_colors": selected_color_keys,
        "selected_color_labels": selected_colors,
        "selected_color_values": selected_color_keys,
        "sidebar_size_options": sidebar_size_options,
        "sidebar_color_options": sidebar_color_options,
        "sidebar_sort_links": sidebar_sort_links,
        "wishlist_product_ids": wishlist_product_ids,
        "query_without_page": query_without_page,
    }
    return render(request, "shop/product_catalog.html", context)


def product_detail(request: HttpRequest, pk: int, slug: str) -> HttpResponse:
    product = get_object_or_404(
        Product.objects.prefetch_related("gallery_images"),
        id=pk,
        slug=slug,
        available=True,
    )

    recent_ids = request.session.get("recently_viewed", [])
    recent_ids = [rid for rid in recent_ids if rid != pk]
    recent_ids.insert(0, pk)
    request.session["recently_viewed"] = recent_ids[:20]
    request.session.modified = True

    recently_viewed_products = []
    if recent_ids:
        lookback_ids = [rid for rid in recent_ids if rid != pk][:6]
        ordered = Product.objects.filter(id__in=lookback_ids, available=True)
        ordered_map = {p.id: p for p in ordered}
        recently_viewed_products = [
            ordered_map[rid] for rid in lookback_ids if rid in ordered_map
        ]

    related_products = Product.objects.filter(
        available=True, category=product.category
    ).exclude(id=product.id)[:4]
    variants = ProductVariant.objects.filter(product=product, is_active=True).order_by(
        "color_name", "size"
    )
    requires_variant = product.requires_variants

    default_variant = (
        variants.filter(size__iexact="M")
        .filter(Q(color_name__iexact="Den") | Q(color_name__iexact="Đen"))
        .first()
    )
    if not default_variant:
        default_variant = variants.first()

    variant_data = list(
        variants.values("id", "color_name", "color_code", "size", "stock")
    )
    color_options_map = {}
    for item in variant_data:
        color_name = item["color_name"]
        if color_name not in color_options_map:
            color_options_map[color_name] = {
                "value": color_name,
                "label": format_color_label(color_name),
                "code": item.get("color_code") or "#111111",
            }
    color_options = list(color_options_map.values())
    size_options = sorted({item["size"] for item in variant_data})
    gallery_images = product.get_detail_gallery_images()
    detail_gallery_slots = build_detail_gallery_slots(product, gallery_images)
    is_in_wishlist = False
    if request.user.is_authenticated:
        is_in_wishlist = WishlistItem.objects.filter(
            user=request.user, product=product
        ).exists()

    published_reviews = product.reviews.filter(is_published=True).select_related("user")
    review_stats = published_reviews.aggregate(
        rating_avg=Avg("rating"), rating_count=Count("id")
    )
    rating_avg = review_stats["rating_avg"] or 0
    rating_count = review_stats["rating_count"] or 0
    bucket_map = {
        item["rating"]: item["total"]
        for item in published_reviews.values("rating").annotate(total=Count("id"))
    }
    review_buckets = [
        {"rating": rating, "total": bucket_map.get(rating, 0)}
        for rating in range(5, 0, -1)
    ]

    review_filter = request.GET.get("rfilter", "").strip()
    review_sort = request.GET.get("rsort", "new").strip()
    reviews_qs = published_reviews
    if review_filter == "photo":
        reviews_qs = reviews_qs.exclude(image="")
    elif review_filter in ("5", "4", "3", "2", "1"):
        reviews_qs = reviews_qs.filter(rating=int(review_filter))
    reviews_qs = reviews_qs.order_by("created" if review_sort == "old" else "-created")
    reviews = list(reviews_qs)

    from orders.models import OrderItem

    sold_count = (
        OrderItem.objects.filter(
            product=product, order__status__in=SOLD_STATUSES
        ).aggregate(total=Sum("quantity"))["total"]
        or 0
    )
    total_stock = product.get_total_stock()
    viewing_now = (pk * 7 + 13) % 34 + 8

    user_review = None
    can_review = False
    purchased = False
    if request.user.is_authenticated:
        user_review = product.reviews.filter(user=request.user).first()
        can_review = user_review is None
        if can_review:
            purchased = OrderItem.objects.filter(
                order__user=request.user, order__status="delivered", product=product
            ).exists()

    return render(
        request,
        "shop/product_detail.html",
        {
            "product": product,
            "related_products": related_products,
            "recently_viewed_products": recently_viewed_products,
            "variants": variants,
            "requires_variant": requires_variant,
            "default_variant_id": default_variant.id if default_variant else None,
            "default_color": default_variant.color_name if default_variant else "",
            "default_size": default_variant.size if default_variant else "",
            "gallery_images": gallery_images,
            "detail_gallery_slots": detail_gallery_slots,
            "color_options": color_options,
            "size_options": size_options,
            "variant_data_json": json.dumps(variant_data, ensure_ascii=False),
            "is_in_wishlist": is_in_wishlist,
            "reviews": reviews,
            "review_filter": review_filter,
            "review_sort": review_sort,
            "rating_avg": rating_avg,
            "rating_count": rating_count,
            "review_buckets": review_buckets,
            "user_review": user_review,
            "can_review": can_review,
            "purchased": purchased,
            "questions": product.questions.filter(is_published=True).select_related(
                "user"
            )[:5],
            "sold_count": sold_count,
            "total_stock": total_stock,
            "viewing_now": viewing_now,
            "product_schema": _build_product_schema(
                request, product, rating_avg, rating_count
            ),
        },
    )


def _build_product_schema(
    request: HttpRequest, product, rating_avg, rating_count
) -> dict:
    host = request.get_host()
    schema = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": product.name,
        "description": product.description
        or "Form gọn, dễ mặc và dễ phối trong nhiều hoàn cảnh.",
        "offers": {
            "@type": "Offer",
            "price": str(product.price),
            "priceCurrency": "VND",
            "availability": "https://schema.org/InStock"
            if product.stock > 0
            else "https://schema.org/OutOfStock",
            "url": request.build_absolute_uri(),
        },
    }
    if product.image and product.image.url:
        schema["image"] = f"{request.scheme}://{host}{product.image.url}"
    elif product.image_url:
        schema["image"] = product.image_url
    if rating_count:
        schema["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": str(round(float(rating_avg), 1)),
            "reviewCount": str(rating_count),
        }
    return schema


@rate_limit("chat", max_requests=30, window=60, error_msg="Quá nhiều yêu cầu chat.")
def support_chat_reply(request: HttpRequest) -> JsonResponse:
    question = request.GET.get("q", "").strip()
    if not question:
        return JsonResponse({"error": "empty_question"}, status=400)

    state = get_support_chat_state(request)
    result = build_support_reply(question, state=state)
    save_support_chat_state(request, state)
    return JsonResponse(result)


@login_required
def wishlist_list(request: HttpRequest) -> HttpResponse:
    products = (
        Product.objects.filter(available=True, wishlist_items__user=request.user)
        .select_related("category")
        .distinct()
    )
    return render(request, "account/wishlist.html", {"products": products})


@require_POST
@login_required
def wishlist_toggle(request: HttpRequest, product_id: int) -> HttpResponse:
    product = get_object_or_404(Product, id=product_id, available=True)
    item, created = WishlistItem.objects.get_or_create(
        user=request.user, product=product
    )
    if created:
        messages.success(request, f"Đã thêm {product.name} vào mục yêu thích.")
    else:
        item.delete()
        messages.info(request, f"Đã bỏ {product.name} khỏi mục yêu thích.")

    next_url = request.POST.get("next") or request.GET.get("next")
    if not next_url or not url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}
    ):
        next_url = reverse(
            "products:product_detail", kwargs={"pk": product.id, "slug": product.slug}
        )
    return redirect(next_url)


@require_POST
@login_required
def review_submit(request: HttpRequest, product_id: int) -> HttpResponse:
    product = get_object_or_404(Product, id=product_id, available=True)
    rating_raw = request.POST.get("rating", "")
    comment = request.POST.get("comment", "").strip()

    try:
        rating = int(rating_raw)
    except (TypeError, ValueError):
        rating = 0
    if rating not in range(1, 6):
        messages.error(request, "Vui lòng chọn số sao từ 1 đến 5.")
        return redirect("products:product_detail", pk=product.id, slug=product.slug)

    existing = product.reviews.filter(user=request.user).first()
    if existing:
        messages.info(request, "Bạn đã đánh giá sản phẩm này rồi.")
        return redirect("products:product_detail", pk=product.id, slug=product.slug)

    from orders.models import OrderItem

    verified = OrderItem.objects.filter(
        order__user=request.user, order__status="delivered", product=product
    ).exists()

    Review.objects.create(
        product=product,
        user=request.user,
        rating=rating,
        comment=comment,
        image=request.FILES.get("review_image"),
        verified_purchase=verified,
    )
    messages.success(request, "Cảm ơn bạn đã đánh giá sản phẩm!")
    return redirect("products:product_detail", pk=product.id, slug=product.slug)


@login_required
def review_customer_reply(request: HttpRequest, product_id: int) -> HttpResponse:
    product = get_object_or_404(Product, id=product_id, available=True)
    reply_text = (request.POST.get("customer_reply", "") or "").strip()
    review = Review.objects.filter(product=product, user=request.user).first()
    if not review or not review.shop_reply:
        messages.error(request, "Không thể phản hồi lúc này.")
        return redirect("products:product_detail", pk=product.id, slug=product.slug)
    if reply_text:
        review.customer_reply = reply_text
        review.save(update_fields=["customer_reply"])
        messages.success(
            request, "Đã gửi phản hồi của bạn. Cảm ơn đã đồng hành cùng HUUGIAU!"
        )
    return redirect("products:product_detail", pk=product.id, slug=product.slug)


def search_suggest(request: HttpRequest) -> JsonResponse:
    q = request.GET.get("q", "").strip()
    if not q or len(q) < 1 or len(q) > 50:
        return JsonResponse([], safe=False)
    products = (
        Product.objects.filter(available=True, name__icontains=q)
        .select_related("category")
        .only("id", "slug", "name", "price", "image_url", "category__name")[:8]
    )
    results = [
        {
            "id": p.id,
            "slug": p.slug,
            "name": repair_mojibake_text(p.name),
            "price": str(p.price),
            "image": p.get_image() or "",
            "category": repair_mojibake_text(p.category.name),
        }
        for p in products
    ]
    return JsonResponse(results[:6], safe=False)


@require_POST
def newsletter_subscribe(request: HttpRequest) -> HttpResponse:
    email = (request.POST.get("email") or "").strip()
    if len(email) > 254 or "@" not in email or "." not in email.split("@")[-1]:
        messages.error(request, "Email không hợp lệ. Vui lòng kiểm tra lại.")
    else:
        _, created = NewsletterSubscriber.objects.get_or_create(
            email=email, defaults={"is_active": True}
        )
        messages.success(request, "Đăng ký thành công! Cảm ơn bạn đã theo dõi HUUGIAU.")
    next_url = request.POST.get("next") or ""
    if next_url and url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}
    ):
        return redirect(next_url)
    return redirect("products:product_list")


@require_POST
@login_required
def question_submit(request: HttpRequest, product_id: int) -> HttpResponse:
    product = get_object_or_404(Product, id=product_id, available=True)
    question = (request.POST.get("question") or "").strip()
    if not question:
        messages.error(request, "Vui lòng nhập câu hỏi.")
    elif len(question) < 10:
        messages.error(
            request, "Câu hỏi quá ngắn. Hãy mô tả chi tiết hơn (tối thiểu 10 ký tự)."
        )
    else:
        ProductQuestion.objects.create(
            product=product, user=request.user, question=question
        )
        messages.success(
            request, "Câu hỏi đã được gửi. Shop sẽ trả lời sớm nhất có thể!"
        )
    return redirect("products:product_detail", pk=product.id, slug=product.slug)


@require_POST
def back_in_stock_submit(request: HttpRequest, product_id: int) -> HttpResponse:
    product = get_object_or_404(Product, id=product_id, available=True)
    email = (request.POST.get("email") or "").strip()
    if len(email) > 254 or "@" not in email or "." not in email.split("@")[-1]:
        messages.error(request, "Email không hợp lệ. Vui lòng kiểm tra lại.")
    else:
        _, created = BackInStock.objects.get_or_create(product=product, email=email)
        if created:
            messages.success(
                request, "Đã đăng ký. Shop sẽ báo ngay khi sản phẩm có hàng lại!"
            )
        else:
            messages.info(request, "Email của bạn đã được đăng ký trước đó rồi.")
    return redirect("products:product_detail", pk=product.id, slug=product.slug)


def blog_list(request: HttpRequest) -> HttpResponse:
    posts = BlogPost.objects.filter(is_published=True).defer("body")
    paginator = Paginator(posts, 9)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "shop/blog_list.html", {"posts": page})


def blog_detail(request: HttpRequest, slug: str) -> HttpResponse:
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    return render(request, "shop/blog_detail.html", {"post": post})
