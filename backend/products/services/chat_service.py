import re

from core.text_utils import normalize_vn_text, parse_keyword_list
from products.models import Product, SupportFAQ


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
HUMAN_SUPPORT_KEYWORDS = (
    "tu van truc tiep",
    "nguoi that",
    "nhan vien",
    "goi lai",
    "lien he",
    "hotline",
)
STYLE_RECOMMEND_KEYWORDS = ("goi y", "phoi do", "mix do", "mac sao", "set do", "outfit")
STOCK_KEYWORDS = ("con hang", "het hang", "ton kho", "con size", "con mau")
PRICE_KEYWORDS = (
    "gia bao nhieu",
    "gia ban",
    "ban bao nhieu",
    "bao nhieu tien",
    "re khong",
    "gia",
)
COUPON_KEYWORDS = (
    "ma giam gia",
    "giam gia",
    "khuyen mai",
    "voucher",
    "coupon",
    "sale",
    "flash sale",
)

_PRODUCT_TRIGGERS = (
    STOCK_KEYWORDS + PRICE_KEYWORDS + ("khong", "tim mua", "ban khong", "tim")
)

_STOPWORDS = {
    "co",
    "khong",
    "la",
    "va",
    "cua",
    "cho",
    "ban",
    "toi",
    "minh",
    "em",
    "anh",
    "chi",
    "muon",
    "can",
    "gi",
    "nao",
    "the",
    "theo",
    "lam",
    "sao",
    "ra",
    "ve",
    "san",
    "pham",
    "shop",
    "web",
    "site",
    "ngay",
    "hien",
    "thi",
    "de",
    "duoc",
    "them",
    "hay",
    "nhung",
    "cung",
    "khi",
    "neu",
    "ong",
    "ba",
    "o",
    "that",
    "xin",
    "vui",
    "long",
    "tra",
    "loi",
    "ao",
    "quan",
    "bo",
    "con",
    "doi",
    "ai",
    "noi",
    "da",
    "da",
    "dang",
    "kieu",
}

_SUGGESTIONS = {
    "shipping": ["Ship mất bao lâu?", "Freeship từ bao nhiêu?", "Kiểm tra đơn hàng"],
    "payment": [
        "Thanh toán COD được không?",
        "Hướng dẫn chuyển khoản",
        "Kiểm tra đơn hàng",
    ],
    "order": ["Xem đơn hàng của tôi", "Hủy đơn như thế nào?", "Đơn đang giao đến đâu?"],
    "return": ["Đổi size như thế nào?", "Trả hàng hoàn tiền", "Còn hàng không?"],
    "coupon": [
        "Có mã giảm giá nào không?",
        "Freeship từ bao nhiêu?",
        "Mua combo giá tốt",
    ],
    "style": ["Gợi ý set đồ đi làm", "Tư vấn size", "Còn hàng không?"],
    "stock": ["Còn size M không?", "Kiểm tra tồn kho", "Chốt size giúp shop"],
    "human": ["Tư vấn size", "Kiểm tra đơn hàng", "Còn hàng không?"],
    "product": ["Còn size M không?", "Giá ship bao nhiêu?", "Chốt size giúp shop"],
}


def has_any_keyword(message, keywords):
    return any(keyword in message for keyword in keywords)


def product_matches_keyword(product, normalized_keyword):
    return normalized_keyword in normalize_vn_text(
        product.name
    ) or normalized_keyword in normalize_vn_text(product.description)


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
    return (
        "Bạn cho shop biết thêm: đang cần phối cho dịp nào (đi làm, đi chơi, dạo phố), kiểu thích mặc "
        "(basic, gọn, nổi bật) và chiều cao, cân nặng nếu có. Shop sẽ gợi ý set đồ và size phù hợp nhất."
    )


def build_stock_reply():
    return (
        "Tồn kho được cập nhật theo thời gian thực ở từng sản phẩm. Bạn mở trang sản phẩm rồi chọn màu và "
        "size để xem tồn kho còn không. Nếu muốn, nhắn luôn tên sản phẩm kèm màu hoặc size cần kiểm tra, shop xem giúp ngay."
    )


def build_shipping_reply():
    return (
        "Shop free ship toàn quốc cho đơn từ 499K. Đơn dưới mức đó, phí ship hiển thị ngay ở giỏ hàng "
        "trước khi bạn xác nhận đặt. Giao nội thành TP.HCM 1-2 ngày, các tỉnh khác 3-7 ngày làm việc."
    )


def build_payment_reply():
    return (
        "Shop hỗ trợ thanh toán khi nhận hàng (COD) và chuyển khoản ngân hàng (quét QR hoặc chuyển thủ công). "
        "Bạn chọn phương thức ở bước thanh toán. Với COD, bạn trả tiền khi nhận được hàng."
    )


def build_order_tracking_reply():
    return (
        "Nếu đã đăng nhập, bạn vào mục 'Đơn hàng của tôi' để theo dõi từng đơn. Trạng thái gồm: "
        "Chờ xử lý → Đang xử lý → Đang giao → Đã giao. Gửi shop mã đơn nếu cần kiểm tra nhanh."
    )


def build_return_reply():
    return (
        "Bạn có thể đổi/trả trong 7 ngày nếu sản phẩm còn nguyên tem mác và chưa qua sử dụng. "
        "Gửi shop mã đơn và lý do qua chat để được hỗ trợ nhanh nhất."
    )


def build_coupon_reply():
    return (
        "Shop có freeship từ 499K và thường xuyên có mã giảm giá. Ở bước thanh toán, bạn nhập mã vào ô "
        "'Mã giảm giá' để được giảm ngay. Chương trình đang chạy hiển thị ở trang chủ."
    )


_TOPIC_BUILDERS = {
    "shipping": build_shipping_reply,
    "payment": build_payment_reply,
    "order": build_order_tracking_reply,
    "return": build_return_reply,
    "coupon": build_coupon_reply,
    "style": build_style_reply,
    "stock": build_stock_reply,
    "human": build_human_support_reply,
}


def build_topic_reply(topic):
    builder = _TOPIC_BUILDERS.get(topic)
    return builder() if builder else None


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
    if any(
        keyword in normalized_message
        for keyword in ["size", "kich co", "cao", "nang", "kg", "cm", "1m", "form"]
    ):
        return "size"
    if any(
        keyword in normalized_message
        for keyword in ["ship", "giao", "van chuyen", "phi ship", "free ship"]
    ):
        return "shipping"
    if any(
        keyword in normalized_message
        for keyword in ["thanh toan", "chuyen khoan", "cod", "ngan hang"]
    ):
        return "payment"
    if any(
        keyword in normalized_message
        for keyword in ["don", "theo doi", "trang thai", "ma don"]
    ):
        return "order"
    if any(keyword in normalized_message for keyword in COUPON_KEYWORDS):
        return "coupon"
    if any(keyword in normalized_message for keyword in ["doi", "tra", "hoan", "huy"]):
        return "return"
    if any(keyword in normalized_message for keyword in STYLE_RECOMMEND_KEYWORDS):
        return "style"
    if any(keyword in normalized_message for keyword in STOCK_KEYWORDS):
        return "stock"
    if any(keyword in normalized_message for keyword in HUMAN_SUPPORT_KEYWORDS):
        return "human"
    return ""


def _significant_tokens(normalized_message):
    words = re.findall(r"[a-z0-9]+", normalized_message)
    return [word for word in words if word not in _STOPWORDS and len(word) >= 2]


def find_matching_products(normalized_message, limit=3):
    tokens = _significant_tokens(normalized_message)
    if not tokens:
        return []
    scored = []
    for product in Product.objects.filter(available=True):
        haystack = normalize_vn_text(product.name)
        score = sum(1 for token in tokens if token in haystack)
        if score:
            scored.append((score, product))
    scored.sort(key=lambda item: (-item[0], -item[1].stock, item[1].id))
    return [product for _, product in scored[:limit]]


def _is_product_query(normalized_message):
    if has_any_keyword(normalized_message, _PRODUCT_TRIGGERS):
        return True
    return len(_significant_tokens(normalized_message)) <= 2


def _format_price(price):
    return f"{price:,.0f} VNĐ".replace(",", ".")


def build_product_stock_reply(products):
    lines = []
    for product in products:
        if product.stock > 0:
            lines.append(
                f"- {product.name}: còn hàng, giá {_format_price(product.price)}."
            )
        else:
            lines.append(
                f"- {product.name}: hiện hết hàng (giá {_format_price(product.price)})."
            )
    joined = " ".join(lines)
    return f"Shop tìm thấy: {joined} Bạn mở trang sản phẩm để chọn màu/size và xem tồn kho chính xác hơn nhé."


def build_product_price_reply(products):
    if len(products) == 1:
        product = products[0]
        return (
            f"{product.name} có giá {_format_price(product.price)}. "
            "Bạn mở trang sản phẩm để xem chi tiết và khuyến mãi (nếu có)."
        )
    names = ", ".join(product.name for product in products)
    return (
        f"Shop có các sản phẩm: {names}. Giá từng sản phẩm hiển thị trên trang chi tiết, "
        "bạn bấm vào tên sản phẩm để xem nhé."
    )


def match_faq(normalized_message):
    faqs = list(SupportFAQ.objects.filter(is_active=True).order_by("priority", "id"))
    if not faqs:
        for item in DEFAULT_SUPPORT_FAQS:
            if has_any_keyword(
                normalized_message, parse_keyword_list(item["keywords"])
            ):
                return item["answer"]
        return None

    best_answer = None
    best_score = 0
    for faq in faqs:
        keywords = parse_keyword_list(faq.keywords)
        score = sum(
            1 for keyword in keywords if keyword and keyword in normalized_message
        )
        question_text = normalize_vn_text(faq.question)
        if question_text and question_text in normalized_message:
            score += 3
        if score > best_score:
            best_score = score
            best_answer = faq.answer
    return best_answer


def _is_pure_greeting(normalized_message):
    return len(normalized_message) <= 20 and has_any_keyword(
        normalized_message, GREETING_KEYWORDS
    )


def _fallback_reply(state):
    topic = state.get("topic")
    if topic == "style":
        return build_style_reply()
    if topic == "stock":
        return build_stock_reply()
    if topic == "human":
        return build_human_support_reply()
    return "Mình có thể hỗ trợ về size, ship, thanh toán, đổi trả và theo dõi đơn hàng. Bạn thử hỏi cụ thể hơn một chút nhé."


def build_support_reply(message, state=None):
    state = state or {}
    normalized_message = normalize_vn_text(message)

    if has_any_keyword(normalized_message, THANKS_KEYWORDS):
        return {"reply": build_thanks_reply(), "suggestions": _SUGGESTIONS["order"]}

    if has_any_keyword(normalized_message, HUMAN_SUPPORT_KEYWORDS):
        state["topic"] = "human"
        return {
            "reply": build_human_support_reply(),
            "suggestions": _SUGGESTIONS["human"],
        }

    if _is_pure_greeting(normalized_message):
        state["topic"] = ""
        return {
            "reply": build_greeting_reply(),
            "suggestions": ["Tư vấn size", "Phí ship bao nhiêu?", "Còn hàng không?"],
        }

    size_reply = build_size_support_reply(message, state=state)
    if size_reply:
        return {
            "reply": size_reply,
            "suggestions": ["Mẫu: 1m72 68kg", "Còn size M không?", "Xem bảng size"],
        }

    if has_any_keyword(normalized_message, STYLE_RECOMMEND_KEYWORDS):
        state["topic"] = "style"
        return {"reply": build_style_reply(), "suggestions": _SUGGESTIONS["style"]}

    if _is_product_query(normalized_message):
        products = find_matching_products(normalized_message)
        if products:
            state["topic"] = "product"
            if has_any_keyword(normalized_message, PRICE_KEYWORDS):
                reply = build_product_price_reply(products)
            else:
                reply = build_product_stock_reply(products)
            return {"reply": reply, "suggestions": _SUGGESTIONS["product"]}

    if has_any_keyword(normalized_message, STOCK_KEYWORDS):
        state["topic"] = "stock"
        return {"reply": build_stock_reply(), "suggestions": _SUGGESTIONS["stock"]}

    faq_answer = match_faq(normalized_message)
    if faq_answer:
        return {"reply": faq_answer, "suggestions": _SUGGESTIONS["order"]}

    topic = detect_topic(normalized_message)
    if topic:
        state["topic"] = topic
        topic_reply = build_topic_reply(topic)
        if topic_reply:
            return {
                "reply": topic_reply,
                "suggestions": _SUGGESTIONS.get(
                    topic, ["Tư vấn size", "Còn hàng không?"]
                ),
            }

    return {
        "reply": _fallback_reply(state),
        "suggestions": ["Tư vấn size", "Phí ship bao nhiêu?", "Còn hàng không?"],
    }


def find_support_reply(message, state=None):
    return build_support_reply(message, state=state)["reply"]
