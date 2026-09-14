from pathlib import Path

from django.core.exceptions import ValidationError

MAX_UPLOAD_SIZE = 5 * 1024 * 1024
ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}


def validate_product_image(uploaded_file):
    if not uploaded_file:
        return

    if uploaded_file.size > MAX_UPLOAD_SIZE:
        raise ValidationError("Ảnh không được vượt quá 5MB.")

    extension = Path(uploaded_file.name).suffix.lower().lstrip(".")
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError("Chỉ chấp nhận ảnh JPG, PNG hoặc WebP.")

    try:
        from PIL import Image

        image = Image.open(uploaded_file)
        image.verify()
        uploaded_file.seek(0)
    except Exception as exc:
        raise ValidationError("Tệp tải lên không phải ảnh hợp lệ.") from exc
