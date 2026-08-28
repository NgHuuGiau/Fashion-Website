from products.models import Product


def recently_viewed(request):
    """Context processor: trả về list sản phẩm vừa xem từ localStorage (qua cookie fallback)."""

    cookie_key = "huugiau_recently_viewed"
    ids = []
    try:
        import json

        ids = json.loads(request.COOKIES.get(cookie_key, "[]"))
    except Exception:
        ids = []

    if not ids:
        return {"recently_viewed": []}

    products = Product.objects.filter(id__in=ids, available=True).only(
        "id", "name", "slug", "price", "image", "image_url"
    )

    product_map = {p.id: p for p in products}
    ordered = [product_map[i] for i in ids if i in product_map]
    return {"recently_viewed": ordered[:8]}
