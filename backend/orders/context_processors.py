from .cart import cart_count



def cart_info(request):
    return {
        "cart_item_count": cart_count(request),
    }
