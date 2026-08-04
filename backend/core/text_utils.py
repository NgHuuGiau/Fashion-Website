import unicodedata


def repair_mojibake_text(value):
    text = str(value or "")
    try:
        return text.encode("latin1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text


def normalize_vn_text(value):
    repaired = repair_mojibake_text(value).casefold()
    normalized = unicodedata.normalize("NFD", repaired)
    stripped = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
    return stripped.replace("\u0111", "d")


def parse_keyword_list(value):
    return [normalize_vn_text(part) for part in str(value or "").split(",") if part.strip()]
