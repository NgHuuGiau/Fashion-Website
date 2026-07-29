import json
import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from core.text_utils import normalize_vn_text, parse_keyword_list, repair_mojibake_text
from core.ratelimit import rate_limit
from urllib.parse import quote

from .constants import FEATURED_PRODUCT_LIMIT, get_category_type_label
from .models import (
    Category,
    MAX_PRODUCT_GALLERY_IMAGES,
    Product,
    ProductVariant,
    SupportFAQ,
    WishlistItem,
)


SORT_OPTIONS = {
    "newest": "-created",
    "price_asc": "price",
    "price_desc": "-price",
    "name_asc": "name",
}
PRODUCTS_PER_PAGE = 12
SUPPORT_CHAT_SESSION_KEY = "support_chat_state"
DETAIL_GALLERY_SLOT_COUNT = MAX_PRODUCT_GALLERY_IMAGES

DEFAULT_SUPPORT_FAQS = [
    {
        "question": "Phí ship thế nào?",
        "keywords": "ship,giao,van chuyen,phi ship,free ship",
        "answer": "Shop freeship toàn quốc cho đơn từ 499K. Bạn có thể thêm sản phẩm vào giỏ để xem phí ship trước khi đặt.",
    },
    {
        "question": "Có thanh toán chuyển khoản không?",
        "keywords": "thanh toan,chuyen khoan,cod,ngan hang",
        "answer": "Shop hỗ trợ COD và chuyển khoản ngân hàng. Bạn có thể chọn ở bước checkout.",
    },
    {
        "question": "Làm sao theo dõi đơn?",
        "keywords": "don,theo doi,trang thai,ma don",
        "answer": "Nếu đã đăng nhập, bạn vào mục Đơn hàng để xem trạng thái. Sau khi đặt xong, web cũng hiển thị xác nhận ngay.",
    },
    {
        "question": "Tư vấn size",
        "keywords": "size,kich co,rong,chat lieu,form",
        "answer": "Bạn gửi chiều cao, cân nặng và kiểu mặc mong muốn để shop gợi ý size nhanh hơn.",
    },
    {
        "question": "Đổi trả như thế nào?",
        "keywords": "doi,tra,hoan,huy",
        "answer": "Nếu cần đổi trả, bạn liên hệ sớm sau khi nhận hàng và gửi kèm mã đơn để shop hỗ trợ nhanh.",
    },
]

GREETING_KEYWORDS = ("chao", "hello", "hi", "shop oi", "ad oi", "xin chao")
THANKS_KEYWORDS = ("cam on", "thanks", "thank you", "ok shop", "ok cam on")
HUMAN_SUPPORT_KEYWORDS = ("tu van truc tiep", "nguoi that", "nhan vien", "goi lai", "lien he", "hotline")
STYLE_RECOMMEND_KEYWORDS = ("goi y", "phoi do", "mix do", "mac sao", "set do", "outfit")
STOCK_KEYWORDS = ("con hang", "het hang", "ton kho", "con size", "con mau")

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


def parse_price(value):
    if not value:
        return None
    try:
        cleaned = str(value).replace(".", "").replace(",", "").replace(" ", "").strip()
        parsed = int(cleaned)
        return parsed if parsed >= 0 else None
    except (TypeError, ValueError):
        return None
def format_color_label(color_name):
    repaired = repair_mojibake_text(color_name)
    normalized = normalize_vn_text(repaired).strip()
    if normalized in COLOR_DISPLAY_MAP:
        return COLOR_DISPLAY_MAP[normalized]
    return repaired


def build_gallery_placeholder(product, slot_index):

    category_label = normalize_vn_text(get_category_type_label(product.category.slug)).upper()
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


def build_detail_gallery_slots(product, gallery_images):
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
        fit_note = "Nếu thích mặc gọn, ưu tiên size nhỏ hơn khi bảng size có sẵn."
    elif weight_kg >= 78:
        fit_note = "Nếu muốn thoải mái hơn ở vai và bụng, ưu tiên rộng hơn một size."
    else:
        fit_note = "Nếu thích form vừa người, chọn đúng size gợi ý. Nếu thích oversize, có thể tăng lên 1 size."

    return (
        f"Với chiều cao {height_cm}cm và cân nặng {weight_kg}kg, shop gợi ý bạn bắt đầu thử size {base_size}. "
        f"{fit_note} "
        "Bạn có thể gửi thêm kiểu mặc mong muốn như ôm, vừa hay oversize để chốt kỹ hơn."
    )


def build_greeting_reply():
    return "Chào bạn, mình hỗ trợ size, hàng còn, phí ship, thanh toán và đổi trả. Bạn cứ nhắn ngắn gọn như đang chat với shop nhé."


def build_thanks_reply():
    return "Mình luôn sẵn sàng hỗ trợ. Nếu cần chốt size, kiểm tra hàng hay hỏi cách thanh toán thì cứ nhắn tiếp nhé."


def build_human_support_reply():
    return "Bạn cứ để lại câu hỏi cụ thể về sản phẩm, size, màu hoặc mã đơn. Shop sẽ hỗ trợ ngay trong khung chat này."


def build_style_reply():
    return "Bạn có thể gửi tên sản phẩm hoặc nói rõ muốn mặc theo kiểu basic, gọn hay nổi bật. Nếu có thêm chiều cao và cân nặng, mình sẽ gợi ý luôn size và cách phối."


def build_stock_reply():
    return "Bạn mở đúng trang sản phẩm rồi chọn màu và size để xem tồn kho ngay. Nếu muốn hỏi nhanh hơn, hãy nhắn luôn tên sản phẩm kèm màu hoặc size cần kiểm tra."


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
            f"Mình đã thấy bạn cao khoảng {height_cm}cm. Bạn gửi thêm cân nặng hiện tại và kiểu mặc mong muốn "
            "để mình gợi ý size sát hơn."
        )

    if weight_kg and not height_cm:
        state["pending"] = "height"
        return (
            f"Mình đã thấy bạn nặng khoảng {weight_kg}kg. Bạn gửi thêm chiều cao hiện tại bao nhiêu cm hoặc 1m bao nhiêu "
            "để mình gợi ý size sát hơn."
        )

    state["pending"] = "size_profile"
    return (
        "Bạn gửi theo mẫu này để mình tư vấn size nhanh hơn: cao bao nhiêu cm, nặng bao nhiêu kg, thích mặc ôm hay oversize. "
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


def has_any_keyword(message, keywords):
    return any(keyword in message for keyword in keywords)


def product_matches_keyword(product, normalized_keyword):
    return normalized_keyword in normalize_vn_text(product.name) or normalized_keyword in normalize_vn_text(product.description)


def find_support_reply(message, state=None):
    normalized_message = normalize_vn_text(message)
    state = state or {}

    if has_any_keyword(normalized_message, GREETING_KEYWORDS):
        state["topic"] = ""
        return build_greeting_reply()

    if has_any_keyword(normalized_message, THANKS_KEYWORDS):
        return build_thanks_reply()

    if has_any_keyword(normalized_message, HUMAN_SUPPORT_KEYWORDS):
        state["topic"] = "human"
        return build_human_support_reply()

    if has_any_keyword(normalized_message, STYLE_RECOMMEND_KEYWORDS):
        state["topic"] = "style"
        return build_style_reply()

    if has_any_keyword(normalized_message, STOCK_KEYWORDS):
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
            if has_any_keyword(normalized_message, parse_keyword_list(item["keywords"])):
                return item["answer"]
        if state.get("topic") == "style":
            return build_style_reply()
        if state.get("topic") == "stock":
            return build_stock_reply()
        return "Mình có thể hỗ trợ về size, ship, thanh toán, đổi trả và theo dõi đơn hàng. Bạn thử hỏi cụ thể hơn một chút nhé."

    best_answer = None
    best_score = 0
    for faq in faqs:
        keywords = parse_keyword_list(faq.keywords)
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
    base_products = Product.objects.filter(available=True).select_related("category").prefetch_related("variants")
    products_qs = base_products
    categories = list(Category.objects.all())

    category_slug = request.GET.get("category", "").strip()
    keyword = request.GET.get("q", "").strip()
    min_price_raw = request.GET.get("min_price", "").strip()
    max_price_raw = request.GET.get("max_price", "").strip()
    selected_sizes = list(dict.fromkeys(item.upper() for item in request.GET.getlist("size") if item.strip()))
    selected_color_keys = list(dict.fromkeys(normalize_vn_text(item) for item in request.GET.getlist("color") if item.strip()))
    selected_colors = [COLOR_DISPLAY_MAP.get(item, item.title()) for item in selected_color_keys]
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
            if product_matches_keyword(item, normalized_keyword)
        ]

        db_ids = list(db_matched.values_list("id", flat=True))
        merged_ids = list(db_ids)
        db_id_set = set(db_ids)
        merged_ids.extend([item.id for item in accent_insensitive_matched if item.id not in db_id_set])
        products_qs = products_qs.filter(id__in=merged_ids)

    if selected_sizes:
        products_qs = products_qs.filter(variants__size__in=selected_sizes).distinct()

    if selected_colors:
        products_qs = products_qs.filter(variants__color_name__in=selected_colors).distinct()

    no_filter_mode = not any([category_slug, keyword, min_price_raw, max_price_raw]) and selected_sort == "newest"
    if no_filter_mode:
        is_random_home = True
        featured_qs = base_products.filter(featured=True).order_by("id")
        slider_products = list(featured_qs[:FEATURED_PRODUCT_LIMIT])

        if slider_products:
            products_qs = featured_qs
        else:
            products_qs = base_products.order_by("id")
    else:
        products_qs = products_qs.order_by(SORT_OPTIONS[selected_sort])

    paginator = Paginator(products_qs, PRODUCTS_PER_PAGE)
    products = paginator.get_page(request.GET.get("page"))

    def build_catalog_query(**overrides):
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

    available_sizes = list(variant_qs.values_list("size", flat=True).distinct().order_by())
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

    available_colors = list(variant_qs.values("color_name", "color_code").distinct().order_by())
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
    sidebar_color_options = sorted(sidebar_color_map.values(), key=lambda item: item["label"])

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
        "site_total_products": base_products.count(),
        "categories": categories,
        "selected_category": selected_category,
        "keyword": keyword,
        "slider_products": slider_products,
        "is_random_home": is_random_home,
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


def product_detail(request, pk, slug):
    product = get_object_or_404(Product.objects.prefetch_related("gallery_images"), id=pk, slug=slug, available=True)

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
        recently_viewed_products = [ordered_map[rid] for rid in lookback_ids if rid in ordered_map]

    related_products = Product.objects.filter(available=True, category=product.category).exclude(id=product.id)[:4]
    variants = ProductVariant.objects.filter(product=product, is_active=True).order_by("color_name", "size")
    requires_variant = product.requires_variants

    default_variant = variants.filter(size__iexact="M").filter(Q(color_name__iexact="Den") | Q(color_name__iexact="Đen")).first()
    if not default_variant:
        default_variant = variants.first()

    variant_data = list(variants.values("id", "color_name", "color_code", "size", "stock"))
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
        is_in_wishlist = WishlistItem.objects.filter(user=request.user, product=product).exists()

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
        },
    )


@rate_limit("chat", max_requests=30, window=60, error_msg="Quá nhiều yêu cầu chat.")
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
        messages.success(request, f"Đã thêm {product.name} vào mục yêu thích.")
    else:
        item.delete()
        messages.info(request, f"Đã bỏ {product.name} khỏi mục yêu thích.")

    next_url = request.POST.get("next") or request.GET.get("next")
    if not next_url or not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        next_url = reverse("products:product_detail", kwargs={"pk": product.id, "slug": product.slug})
    return redirect(next_url)


def search_suggest(request):
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
