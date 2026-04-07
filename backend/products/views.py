import json
import unicodedata

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import Category, Product, ProductVariant, WishlistItem


SORT_OPTIONS = {
    "newest": "-created",
    "price_asc": "price",
    "price_desc": "-price",
    "name_asc": "name",
}
PRODUCTS_PER_PAGE = 12



# -------------------------------------------
# | HÀM XỬ LÝ (FUNCTION): NORMALIZE_VN_TEXT |
# -------------------------------------------
def normalize_vn_text(value):
    text = (value or "").casefold()
    normalized = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")



# -------------------------------------
# | HÀM XỬ LÝ (FUNCTION): PARSE_PRICE |
# -------------------------------------
def parse_price(value):
    if not value:
        return None
    try:
        cleaned = str(value).replace(",", "").strip()
        parsed = int(cleaned)
        return parsed if parsed >= 0 else None
    except (TypeError, ValueError):
        return None



# --------------------------------------
# | HÀM XỬ LÝ (FUNCTION): PRODUCT_LIST |
# --------------------------------------
def product_list(request):
    base_products = Product.objects.filter(available=True).select_related("category")
    products_qs = base_products
    categories = Category.objects.all()

    category_slug = request.GET.get("category", "").strip()
    keyword = request.GET.get("q", "").strip()
    min_price_raw = request.GET.get("min_price", "").strip()
    max_price_raw = request.GET.get("max_price", "").strip()
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

        db_matched = products_qs.filter(Q(name__icontains=keyword) | Q(description__icontains=keyword))
        accent_insensitive_matched = [
            item
            for item in products_qs
            if normalized_keyword in normalize_vn_text(item.name)
            or normalized_keyword in normalize_vn_text(item.description)
        ]

        db_ids = list(db_matched.values_list("id", flat=True))
        merged_ids = list(db_ids)
        db_id_set = set(db_ids)
        merged_ids.extend([item.id for item in accent_insensitive_matched if item.id not in db_id_set])
        products_qs = products_qs.filter(id__in=merged_ids)

    no_filter_mode = not any([category_slug, keyword, min_price_raw, max_price_raw]) and selected_sort == "newest"
    if no_filter_mode:
        is_random_home = True
        featured_limit = 12
        featured_qs = base_products.filter(featured=True).order_by("id")
        slider_products = list(featured_qs[:featured_limit])

        if slider_products:
            products_qs = featured_qs
        else:
            products_qs = base_products.order_by("id")
    else:
        products_qs = products_qs.order_by(SORT_OPTIONS[selected_sort])

    paginator = Paginator(products_qs, PRODUCTS_PER_PAGE)
    products = paginator.get_page(request.GET.get("page"))

    query_params = request.GET.copy()
    query_params.pop("page", None)
    query_without_page = query_params.urlencode()

    wishlist_product_ids = set()
    if request.user.is_authenticated and products:
        visible_ids = [item.id for item in products.object_list]
        wishlist_product_ids = set(
            WishlistItem.objects.filter(user=request.user, product_id__in=visible_ids).values_list("product_id", flat=True)
        )

    context = {
        "products": products,
        "total_products": paginator.count,
        "categories": categories,
        "selected_category": selected_category,
        "keyword": keyword,
        "slider_products": slider_products,
        "is_random_home": is_random_home,
        "selected_sort": selected_sort,
        "min_price": min_price_raw,
        "max_price": max_price_raw,
        "wishlist_product_ids": wishlist_product_ids,
        "query_without_page": query_without_page,
    }
    return render(request, "shop/home.html", context)



# ----------------------------------------
# | HÀM XỬ LÝ (FUNCTION): PRODUCT_DETAIL |
# ----------------------------------------
def product_detail(request, pk, slug):
    product = get_object_or_404(Product, id=pk, slug=slug, available=True)
    related_products = Product.objects.filter(available=True, category=product.category).exclude(id=product.id)[:4]
    variants = ProductVariant.objects.filter(product=product, is_active=True).order_by("color_name", "size")
    requires_variant = product.category.slug in {"ao", "quan"}

    default_variant = variants.filter(color_name__iexact="Den", size__iexact="M").first()
    if not default_variant:
        default_variant = variants.first()

    variant_data = list(variants.values("id", "color_name", "size", "stock"))
    color_options = sorted({item["color_name"] for item in variant_data})
    size_options = sorted({item["size"] for item in variant_data})
    is_in_wishlist = False
    if request.user.is_authenticated:
        is_in_wishlist = WishlistItem.objects.filter(user=request.user, product=product).exists()

    return render(
        request,
        "shop/product_detail.html",
        {
            "product": product,
            "related_products": related_products,
            "variants": variants,
            "requires_variant": requires_variant,
            "default_variant_id": default_variant.id if default_variant else None,
            "default_color": default_variant.color_name if default_variant else "",
            "default_size": default_variant.size if default_variant else "",
            "color_options": color_options,
            "size_options": size_options,
            "variant_data_json": json.dumps(variant_data),
            "is_in_wishlist": is_in_wishlist,
        },
    )


@login_required

# ---------------------------------------
# | HÀM XỬ LÝ (FUNCTION): WISHLIST_LIST |
# ---------------------------------------
def wishlist_list(request):
    products = Product.objects.filter(available=True, wishlist_items__user=request.user).select_related("category").distinct()
    return render(request, "account/wishlist.html", {"products": products})


@require_POST
@login_required

# -----------------------------------------
# | HÀM XỬ LÝ (FUNCTION): WISHLIST_TOGGLE |
# -----------------------------------------
def wishlist_toggle(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)
    item, created = WishlistItem.objects.get_or_create(user=request.user, product=product)
    if created:
        messages.success(request, "Đã thêm vào danh sách yêu thích.")
    else:
        item.delete()
        messages.info(request, "Đã bỏ khỏi danh sách yêu thích.")

    next_url = request.POST.get("next") or request.GET.get("next")
    if not next_url:
        next_url = reverse("products:product_detail", kwargs={"pk": product.id, "slug": product.slug})
    return redirect(next_url)
