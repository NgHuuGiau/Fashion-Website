import json
import re
import unicodedata

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import Category, Product, ProductVariant, SupportFAQ, WishlistItem


SORT_OPTIONS = {
    "newest": "-created",
    "price_asc": "price",
    "price_desc": "-price",
    "name_asc": "name",
}
PRODUCTS_PER_PAGE = 12
SUPPORT_CHAT_SESSION_KEY = "support_chat_state"

DEFAULT_SUPPORT_FAQS = [
    {
        "question": "Phí ship thế nào?",
        "keywords": "ship,giao,van chuyen,phi ship,free ship",
        "answer": "Shop free ship toàn quốc cho đơn từ 499K. Bạn có thể thêm sản phẩm vào giỏ để xem phí ship trước khi đặt hàng.",
    },
    {
        "question": "Có thanh toán chuyển khoản không?",
        "keywords": "thanh toan,chuyen khoan,cod,ngan hang",
        "answer": "Shop hỗ trợ thanh toán khi nhận hàng và chuyển khoản ngân hàng. Ở trang checkout bạn có thể chọn phương thức phù hợp.",
    },
    {
        "question": "Làm sao theo dõi đơn?",
        "keywords": "don,theo doi,trang thai,ma don",
        "answer": "Nếu đã đăng nhập, bạn vào mục Đơn hàng để xem trạng thái. Sau khi đặt thành công, hệ thống cũng hiện trang xác nhận đơn ngay trên web.",
    },
    {
        "question": "Tư vấn size",
        "keywords": "size,kich co,rong,chat lieu,form",
        "answer": "Bạn nên vào trang chi tiết sản phẩm để chọn màu và size. Nếu cần, hãy gửi thêm chiều cao, cân nặng và form mặc mong muốn để shop tư vấn nhanh hơn.",
    },
    {
        "question": "Đổi trả như thế nào?",
        "keywords": "doi,tra,hoan,huy",
        "answer": "Bạn hãy liên hệ shop sớm nhất sau khi nhận hàng nếu cần đổi trả. Shop sẽ cần mã đơn, sản phẩm và lý do đổi trả để hỗ trợ nhanh.",
    },
]

GREETING_KEYWORDS = ("chao", "hello", "hi", "shop oi", "ad oi", "xin chao")
THANKS_KEYWORDS = ("cam on", "thanks", "thank you", "ok shop", "ok cam on")
HUMAN_SUPPORT_KEYWORDS = ("tu van truc tiep", "nguoi that", "nhan vien", "goi lai", "lien he", "hotline")
STYLE_RECOMMEND_KEYWORDS = ("goi y", "phoi do", "mix do", "mac sao", "set do", "outfit")
STOCK_KEYWORDS = ("con hang", "het hang", "ton kho", "con size", "con mau")


def normalize_vn_text(value):
    text = (value or "").casefold()
    normalized = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def parse_price(value):
    if not value:
        return None
    try:
        cleaned = str(value).replace(",", "").strip()
        parsed = int(cleaned)
        return parsed if parsed >= 0 else None
    except (TypeError, ValueError):
        return None


def get_support_chat_state(request):
    state = request.session.get(SUPPORT_CHAT_SESSION_KEY) or {}
    if not isinstance(state, dict):
        return {}
    return {
        "topic": state.get("topic", ""),
        "height_cm": state.get("height_cm"),
        "weight_kg": state.get("weight_kg"),
        "pending": state.get("pending", ""),
    }


def save_support_chat_state(request, state):
    request.session[SUPPORT_CHAT_SESSION_KEY] = {
        "topic": state.get("topic", ""),
        "height_cm": state.get("height_cm"),
        "weight_kg": state.get("weight_kg"),
        "pending": state.get("pending", ""),
    }
    request.session.modified = True


def extract_height_cm(message):
    normalized = normalize_vn_text(message)

    match_cm = re.search(r"(?<!\d)(1[4-9]\d|20\d)\s*cm\b", normalized)
    if match_cm:
        return int(match_cm.group(1))

    match_meter = re.search(r"(?<!\d)1m\s*(\d{1,2})\b", normalized)
    if match_meter:
        suffix = match_meter.group(1)
        if len(suffix) == 1:
            return 100 + (int(suffix) * 10)
        return 100 + int(suffix)

    return None


def extract_weight_kg(message):
    normalized = normalize_vn_text(message)
    match = re.search(r"(?<!\d)(3\d|[4-9]\d|1[0-4]\d|150)\s*kg\b", normalized)
    if match:
        return int(match.group(1))
    return None


def build_size_recommendation(height_cm, weight_kg):
    if height_cm <= 160 and weight_kg <= 50:
        base_size = "S"
    elif height_cm <= 168 and weight_kg <= 60:
        base_size = "M"
    elif height_cm <= 175 and weight_kg <= 70:
        base_size = "L"
    elif height_cm <= 182 and weight_kg <= 80:
        base_size = "XL"
    else:
        base_size = "XXL"

    if weight_kg <= 50:
        fit_note = "Nếu bạn thích mặc gọn người, ưu tiên size nhỏ hơn nếu bảng size có sẵn."
    elif weight_kg >= 78:
        fit_note = "Nếu bạn muốn thoải mái hơn ở vai và bụng, ưu tiên form rộng hơn một size."
    else:
        fit_note = "Nếu bạn thích form vừa người, chọn đúng size gợi ý. Nếu thích oversize, có thể tăng lên 1 size."

    return (
        f"Với chiều cao {height_cm}cm và cân nặng {weight_kg}kg, shop gợi ý bạn bắt đầu thử size {base_size}. "
        f"{fit_note} "
        "Để chốt size kỹ hơn, bạn có thể gửi thêm style muốn mặc như ôm, vừa hay oversize."
    )


def build_greeting_reply():
    return "Chào bạn, mình hỗ trợ tư vấn size, còn hàng, ship, thanh toán và đổi trả. Bạn cứ nhắn tự nhiên như đang hỏi nhân viên tại shop nhé."


def build_thanks_reply():
    return "Mình luôn sẵn sàng hỗ trợ. Nếu bạn cần chốt size, kiểm tra còn hàng hay hỏi cách thanh toán thì cứ nhắn tiếp nhé."


def build_human_support_reply():
    return "Bạn cứ để lại câu hỏi cụ thể về sản phẩm, size, màu hoặc mã đơn. Shop sẽ dựa trên nội dung đó để hỗ trợ sát hơn ngay trong khung chat này."


def build_style_reply():
    return "Bạn có thể gửi tên sản phẩm hoặc nói rõ muốn mặc theo kiểu basic, gọn hay nổi bật. Nếu có thêm chiều cao và cân nặng, mình sẽ gợi ý luôn size và cách phối phù hợp hơn."


def build_stock_reply():
    return "Bạn mở đúng trang sản phẩm rồi chọn màu và size để xem tồn kho ngay. Nếu muốn hỏi nhanh hơn, bạn nhắn luôn tên sản phẩm kèm màu/size cần kiểm tra nhé."


def build_size_support_reply(message, state=None):
    normalized = normalize_vn_text(message)
    size_keywords = ["size", "kich co", "mac", "form", "cao", "nang", "kg", "cm", "1m"]
    state = state or {}

    if (
        not any(keyword in normalized for keyword in size_keywords)
        and state.get("topic") != "size"
        and state.get("pending") not in {"height", "weight", "size_profile"}
    ):
        return None

    height_cm = extract_height_cm(message) or state.get("height_cm")
    weight_kg = extract_weight_kg(message) or state.get("weight_kg")
    state["topic"] = "size"
    state["height_cm"] = height_cm
    state["weight_kg"] = weight_kg

    if height_cm and weight_kg:
        state["pending"] = ""
        return build_size_recommendation(height_cm, weight_kg)

    if height_cm and not weight_kg:
        state["pending"] = "weight"
        return (
            f"Mình đã thấy bạn cao khoảng {height_cm}cm. Bạn gửi thêm cân nặng hiện tại bao nhiêu kg và thích mặc ôm, vừa hay oversize "
            "để mình gợi ý size chi tiết hơn."
        )

    if weight_kg and not height_cm:
        state["pending"] = "height"
        return (
            f"Mình đã thấy bạn nặng khoảng {weight_kg}kg. Bạn gửi thêm chiều cao hiện tại bao nhiêu cm hoặc 1m bao nhiêu "
            "để mình gợi ý size sát hơn."
        )

    state["pending"] = "size_profile"
    return (
        "Bạn gửi theo mẫu này giúp mình để tư vấn size nhanh và rõ hơn: cao bao nhiêu cm, nặng bao nhiêu kg, thích mặc ôm hay oversize. "
        "Ví dụ: 1m72, 68kg, thích form vừa người."
    )


def detect_topic(normalized_message):
    if any(keyword in normalized_message for keyword in ["size", "kich co", "cao", "nang", "kg", "cm", "1m", "form"]):
        return "size"
    if any(keyword in normalized_message for keyword in ["ship", "giao", "van chuyen", "phi ship", "free ship"]):
        return "shipping"
    if any(keyword in normalized_message for keyword in ["thanh toan", "chuyen khoan", "cod", "ngan hang"]):
        return "payment"
    if any(keyword in normalized_message for keyword in ["don", "theo doi", "trang thai", "ma don"]):
        return "order"
    if any(keyword in normalized_message for keyword in ["doi", "tra", "hoan", "huy"]):
        return "return"
    if any(keyword in normalized_message for keyword in STYLE_RECOMMEND_KEYWORDS):
        return "style"
    if any(keyword in normalized_message for keyword in STOCK_KEYWORDS):
        return "stock"
    if any(keyword in normalized_message for keyword in HUMAN_SUPPORT_KEYWORDS):
        return "human"
    return ""


def find_support_reply(message, state=None):
    normalized_message = normalize_vn_text(message)
    state = state or {}

    if any(keyword in normalized_message for keyword in GREETING_KEYWORDS):
        state["topic"] = ""
        return build_greeting_reply()

    if any(keyword in normalized_message for keyword in THANKS_KEYWORDS):
        return build_thanks_reply()

    if any(keyword in normalized_message for keyword in HUMAN_SUPPORT_KEYWORDS):
        state["topic"] = "human"
        return build_human_support_reply()

    if any(keyword in normalized_message for keyword in STYLE_RECOMMEND_KEYWORDS):
        state["topic"] = "style"
        return build_style_reply()

    if any(keyword in normalized_message for keyword in STOCK_KEYWORDS):
        state["topic"] = "stock"
        return build_stock_reply()

    size_reply = build_size_support_reply(message, state=state)
    if size_reply:
        return size_reply

    faqs = list(SupportFAQ.objects.filter(is_active=True).order_by("priority", "id"))
    detected_topic = detect_topic(normalized_message)
    if detected_topic:
        state["topic"] = detected_topic

    if not faqs:
        for item in DEFAULT_SUPPORT_FAQS:
            keywords = [normalize_vn_text(part) for part in item["keywords"].split(",") if part.strip()]
            if any(keyword in normalized_message for keyword in keywords):
                return item["answer"]
        if state.get("topic") == "style":
            return build_style_reply()
        if state.get("topic") == "stock":
            return build_stock_reply()
        return "Mình có thể hỗ trợ về size, ship, thanh toán, đổi trả và theo dõi đơn hàng. Bạn thử hỏi cụ thể hơn một chút nhé."

    best_answer = None
    best_score = 0
    for faq in faqs:
        keywords = [normalize_vn_text(part) for part in faq.keywords.split(",") if part.strip()]
        score = sum(1 for keyword in keywords if keyword and keyword in normalized_message)
        question_text = normalize_vn_text(faq.question)
        if question_text and question_text in normalized_message:
            score += 3
        if score > best_score:
            best_score = score
            best_answer = faq.answer

    if best_answer:
        return best_answer
    if state.get("topic") == "style":
        return build_style_reply()
    if state.get("topic") == "stock":
        return build_stock_reply()
    if state.get("topic") == "human":
        return build_human_support_reply()
    return "Mình có thể hỗ trợ về size, ship, thanh toán, đổi trả và theo dõi đơn hàng. Bạn thử hỏi cụ thể hơn một chút nhé."


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
    return render(request, "shop/product_catalog.html", context)


def product_detail(request, pk, slug):
    product = get_object_or_404(Product.objects.prefetch_related("gallery_images"), id=pk, slug=slug, available=True)
    related_products = Product.objects.filter(available=True, category=product.category).exclude(id=product.id)[:4]
    variants = ProductVariant.objects.filter(product=product, is_active=True).order_by("color_name", "size")
    requires_variant = product.category.slug in {"ao", "quan"}

    default_variant = variants.filter(color_name__iexact="Den", size__iexact="M").first()
    if not default_variant:
        default_variant = variants.first()

    variant_data = list(variants.values("id", "color_name", "size", "stock"))
    color_options = sorted({item["color_name"] for item in variant_data})
    size_options = sorted({item["size"] for item in variant_data})
    gallery_images = product.get_gallery_images()
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
            "gallery_images": gallery_images,
            "color_options": color_options,
            "size_options": size_options,
            "variant_data_json": json.dumps(variant_data),
            "is_in_wishlist": is_in_wishlist,
        },
    )


def support_chat_reply(request):
    question = request.GET.get("q", "").strip()
    if not question:
        return JsonResponse({"error": "empty_question"}, status=400)

    state = get_support_chat_state(request)
    reply = find_support_reply(question, state=state)
    save_support_chat_state(request, state)
    return JsonResponse({"reply": reply})


@login_required
def wishlist_list(request):
    products = Product.objects.filter(available=True, wishlist_items__user=request.user).select_related("category").distinct()
    return render(request, "account/wishlist.html", {"products": products})


@require_POST
@login_required
def wishlist_toggle(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)
    item, created = WishlistItem.objects.get_or_create(user=request.user, product=product)
    if created:
        messages.success(request, f"Đã thích sản phẩm {product.name}.")
    else:
        item.delete()
        messages.info(request, f"Đã bỏ thích sản phẩm {product.name}.")

    next_url = request.POST.get("next") or request.GET.get("next")
    if not next_url:
        next_url = reverse("products:product_detail", kwargs={"pk": product.id, "slug": product.slug})
    return redirect(next_url)
