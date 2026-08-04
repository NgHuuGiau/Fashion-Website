from .cart import safe_int


def wishlist_count(request):
    if not request.user.is_authenticated:
        return 0

    cache_key = f"_wishlist_count_{request.user.id}"
    cached = request.session.get(cache_key)
    if cached is not None:
        return cached

    try:
        from products.models import WishlistItem
    except ImportError:
        return 0

    count = WishlistItem.objects.filter(user=request.user).count()
    request.session[cache_key] = count
    request.session.set_expiry(300)
    return count


def cart_count_cached(request):
    cart = request.session.get("cart", {})
    if not cart:
        return 0
    count_key = "_cart_item_count"
    cached = cart.get(count_key)
    if cached is not None:
        return cached
    total = sum(safe_int(item.get("quantity", 0)) for item in cart.values() if isinstance(item, dict))
    cart[count_key] = total
    request.session.modified = True
    return total


def cart_info(request):
    return {
        "cart_item_count": cart_count_cached(request),
        "wishlist_item_count": wishlist_count(request),
    }
