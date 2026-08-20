import random
import string
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont, ImageFilter


CAPTCHA_LENGTH = 6
CAPTCHA_WIDTH = 180
CAPTCHA_HEIGHT = 60
CAPTCHA_FONT_SIZE = 36

_CHARS = "".join(c for c in string.ascii_uppercase + string.digits if c not in "0O1IL")


def generate_captcha_code(length=CAPTCHA_LENGTH):
    return "".join(random.choice(_CHARS) for _ in range(length))


def generate_captcha_image(
    code, width=CAPTCHA_WIDTH, height=CAPTCHA_HEIGHT, font_size=CAPTCHA_FONT_SIZE
):
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Noise lines
    for _ in range(random.randint(3, 6)):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line(
            [(x1, y1), (x2, y2)],
            fill=_random_color(150, 220),
            width=random.randint(1, 2),
        )

    # Noise dots
    for _ in range(random.randint(30, 60)):
        draw.point(
            (random.randint(0, width), random.randint(0, height)),
            fill=_random_color(100, 200),
        )

    # Text
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()

    text_width = draw.textlength(code, font=font)
    x_start = (width - text_width) // 2
    y_start = (height - font_size) // 2

    for i, ch in enumerate(code):
        x = x_start + sum(draw.textlength(c, font=font) for c in code[:i])
        y = y_start + random.randint(-3, 3)
        # Random rotation per char
        char_img = Image.new(
            "RGBA", (font_size + 10, font_size + 10), (255, 255, 255, 0)
        )
        char_draw = ImageDraw.Draw(char_img)
        char_draw.text((5, 0), ch, font=font, fill=_random_color(0, 80))
        char_img = char_img.rotate(random.randint(-15, 15), expand=1)
        img.paste(char_img, (int(x), int(y)), char_img)

    # Blur slightly
    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))

    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()


def _random_color(min_val, max_val):
    return (
        random.randint(min_val, max_val),
        random.randint(min_val, max_val),
        random.randint(min_val, max_val),
    )
