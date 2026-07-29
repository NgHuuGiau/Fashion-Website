from .cart import cart_count


def wishlist_count(request):
    if not request.user.is_authenticated:
        return 0

    try:
        from products.models import WishlistItem
    except ImportError:
        return 0

    return WishlistItem.objects.filter(user=request.user).count()


def cart_info(request):
    return {
        "cart_item_count": cart_count(request),
        "wishlist_item_count": wishlist_count(request),
    }
