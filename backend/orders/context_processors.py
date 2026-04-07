from .cart import cart_count



# -----------------------------------
# | HÀM XỬ LÝ (FUNCTION): CART_INFO |
# -----------------------------------
def cart_info(request):
    return {
        "cart_item_count": cart_count(request),
    }
