"""API JSON (tach tu core/api.py monolith). Logic giu nguyen."""

from django.contrib.auth.decorators import login_required

from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST

from core.text_utils import repair_mojibake_text
from products.models import Category, Product, Review


from .common import (
    PRODUCTS_PER_PAGE,
    SORT_OPTIONS,
    _serialize_product_summary,
    _serialize_review,
    _serialize_variant,
    api_error,
    api_json,
    int_param,
)


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
    # P1.2: phan trang thay vi cat cung 50 (mac dinh 20, toi da 50)
    limit = int_param(request, "limit", 20) or 20
    limit = max(1, min(limit, 50))
    offset = int_param(request, "offset", 0) or 0
    offset = max(0, offset)
    base_qs = product.reviews.filter(is_published=True).select_related("user")
    total = base_qs.count()
    reviews = base_qs[offset : offset + limit]
    return api_json(
        {
            "product_id": product.id,
            "count": total,
            "limit": limit,
            "offset": offset,
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
