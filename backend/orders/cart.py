from decimal import Decimal

from products.models import Product, ProductVariant


CART_SESSION_ID = "cart"



# -----------------------------------
# | HÀM XỬ LÝ (FUNCTION): _GET_CART |
# -----------------------------------
def _get_cart(session):
    return session.setdefault(CART_SESSION_ID, {})



# -----------------------------------
# | HÀM XỬ LÝ (FUNCTION): _ITEM_KEY |
# -----------------------------------
def _item_key(product_id, variant_id=None):
    return f"{product_id}:{variant_id or 0}"



# -----------------------------------------
# | HÀM XỬ LÝ (FUNCTION): _PARSE_ITEM_KEY |
# -----------------------------------------
def _parse_item_key(item_key):
    try:
        product_str, variant_str = str(item_key).split(":", 1)
        return int(product_str), int(variant_str)
    except (ValueError, TypeError):
        return None, None



# ----------------------------------
# | HÀM XỬ LÝ (FUNCTION): SAFE_INT |
# ----------------------------------
def safe_int(value, default=1, minimum=1):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    return max(minimum, parsed)



# ----------------------------------
# | HÀM XỬ LÝ (FUNCTION): ADD_CART |
# ----------------------------------
def add_cart(request, product_id, quantity=1, override_quantity=False, variant_id=None):
    cart = _get_cart(request.session)
    product = Product.objects.filter(id=product_id, available=True).first()
    if not product:
        return

    variant = None
    if variant_id:
        variant = ProductVariant.objects.filter(id=variant_id, product=product, is_active=True).first()
        if not variant:
            return

    key = _item_key(product_id, variant_id)

    if key not in cart:
        cart[key] = {
            "quantity": 0,
            "price": str(product.price),
            "variant_id": variant.id if variant else 0,
        }

    safe_quantity = safe_int(quantity, default=1, minimum=1)
    if override_quantity:
        cart[key]["quantity"] = safe_quantity
    else:
        cart[key]["quantity"] += safe_quantity

    max_stock = variant.stock if variant else product.stock
    if max_stock > 0:
        cart[key]["quantity"] = min(cart[key]["quantity"], max_stock)
    else:
        cart[key]["quantity"] = 1

    request.session.modified = True



# -------------------------------------
# | HÀM XỬ LÝ (FUNCTION): REMOVE_CART |
# -------------------------------------
def remove_cart(request, item_key=None):
    cart = _get_cart(request.session)

    if item_key and item_key in cart:
        del cart[item_key]
        request.session.modified = True



# ------------------------------------
# | HÀM XỬ LÝ (FUNCTION): CLEAR_CART |
# ------------------------------------
def clear_cart(request):
    if CART_SESSION_ID in request.session:
        del request.session[CART_SESSION_ID]
        request.session.modified = True



# -----------------------------------
# | HÀM XỬ LÝ (FUNCTION): ITER_CART |
# -----------------------------------
def iter_cart(request):
    cart = _get_cart(request.session)
    product_ids = set()
    variant_ids = set()

    for key in cart.keys():
        product_id, variant_id = _parse_item_key(key)
        if product_id:
            product_ids.add(product_id)
        if variant_id and variant_id > 0:
            variant_ids.add(variant_id)

    products = Product.objects.filter(id__in=product_ids, available=True).select_related("category")
    products_by_id = {product.id: product for product in products}
    variants_by_id = {
        variant.id: variant
        for variant in ProductVariant.objects.filter(id__in=variant_ids, is_active=True, product_id__in=product_ids)
    }

    rows = []
    total = Decimal("0")

    for key, item in cart.items():
        product_id, variant_id = _parse_item_key(key)
        if not product_id:
            continue

        product = products_by_id.get(product_id)
        if not product:
            continue

        variant = variants_by_id.get(variant_id) if variant_id else None
        quantity = safe_int(item.get("quantity", 1), default=1, minimum=1)
        price = Decimal(item.get("price", product.price))
        subtotal = price * quantity
        total += subtotal

        rows.append(
            {
                "item_key": key,
                "product": product,
                "variant": variant,
                "quantity": quantity,
                "price": price,
                "subtotal": subtotal,
            }
        )

    return rows, total



# ------------------------------------
# | HÀM XỬ LÝ (FUNCTION): CART_COUNT |
# ------------------------------------
def cart_count(request):
    cart = _get_cart(request.session)
    return sum(safe_int(item.get("quantity", 0), default=0, minimum=0) for item in cart.values())
