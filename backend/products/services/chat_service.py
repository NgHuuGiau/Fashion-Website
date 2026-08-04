import re

from core.text_utils import normalize_vn_text, parse_keyword_list
from products.models import SupportFAQ


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


def has_any_keyword(message, keywords):
    return any(keyword in message for keyword in keywords)


def product_matches_keyword(product, normalized_keyword):
    return normalized_keyword in normalize_vn_text(product.name) or normalized_keyword in normalize_vn_text(product.description)


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
