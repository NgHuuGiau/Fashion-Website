import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from products.constants import CATEGORY_SLUG_AO, CATEGORY_SLUG_QUAN
from products.models import Product, ProductImage


PALETTES = [
    ("#f7efe6", "#1c1713", "#9b5c36", "#e9d5c1"),
    ("#eef1f4", "#16181b", "#4d6a81", "#cfdce6"),
    ("#f2ede7", "#1f1915", "#7b6a58", "#ded2c5"),
    ("#f1f0eb", "#131416", "#60726b", "#d9ddd6"),
    ("#f4ece2", "#1a1714", "#a16c46", "#ead8c5"),
]


def slug_hash(value):
    return sum(ord(char) for char in value)


def pick_palette(slug):
    return PALETTES[slug_hash(slug) % len(PALETTES)]


def ensure_dir(path):
    path.mkdir(parents=True, exist_ok=True)


def svg_shell(title, subtitle, art, palette):
    bg, ink, accent, soft = palette
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1400" role="img" aria-label="{title}">
  <rect width="1200" height="1400" fill="{bg}" />
  <circle cx="980" cy="220" r="180" fill="{soft}" />
  <circle cx="220" cy="1180" r="170" fill="{soft}" />
  <rect x="70" y="70" width="1060" height="1260" rx="48" fill="none" stroke="{accent}" stroke-opacity="0.18" stroke-width="4" />
  <text x="110" y="150" fill="{accent}" font-family="'Be Vietnam Pro', Arial, sans-serif" font-size="34" font-weight="700" letter-spacing="4">HUUGIAU ORIGINAL</text>
  <text x="110" y="220" fill="{ink}" font-family="'Archivo Expanded', Arial, sans-serif" font-size="62" font-weight="800">{title}</text>
  <text x="110" y="272" fill="{ink}" fill-opacity="0.72" font-family="'Be Vietnam Pro', Arial, sans-serif" font-size="30">{subtitle}</text>
  {art}
  <text x="110" y="1248" fill="{ink}" fill-opacity="0.7" font-family="'Be Vietnam Pro', Arial, sans-serif" font-size="28">Original product artwork generated locally for this project</text>
</svg>"""


def shirt_art(palette, variant):
    _, ink, accent, soft = palette
    chest = "MẶC CHẤT" if variant == 0 else "LOCAL BRAND"
    hem = "OVERSIZE FIT" if variant == 1 else "URBAN FORM"
    return f"""
  <g transform="translate(185 310)">
    <path d="M180 40 300 0 420 40 520 150 450 250 450 710 150 710 150 250 80 150Z" fill="{accent}" />
    <path d="M230 96 300 58 370 96 420 160 375 210 375 648 225 648 225 210 180 160Z" fill="{soft}" />
    <circle cx="300" cy="150" r="42" fill="{bg_from(palette)}" />
    <text x="300" y="370" text-anchor="middle" fill="{ink}" font-family="'Archivo Expanded', Arial, sans-serif" font-size="40">{chest}</text>
    <text x="300" y="425" text-anchor="middle" fill="{ink}" fill-opacity="0.74" font-family="'Be Vietnam Pro', Arial, sans-serif" font-size="26">{hem}</text>
  </g>"""


def pants_art(palette, variant):
    _, ink, accent, soft = palette
    pocket = "STREET FIT" if variant == 0 else "WIDE LEG"
    return f"""
  <g transform="translate(300 270)">
    <path d="M180 0h240l70 150-70 690H280L230 480 180 840H40L110 150Z" fill="{accent}" />
    <path d="M230 70h140l36 104-42 592H290L260 430 230 766H156L200 174Z" fill="{soft}" />
    <rect x="208" y="240" width="72" height="110" rx="18" fill="{ink}" fill-opacity="0.16" />
    <rect x="320" y="240" width="72" height="110" rx="18" fill="{ink}" fill-opacity="0.16" />
    <text x="300" y="930" text-anchor="middle" fill="{ink}" font-family="'Archivo Expanded', Arial, sans-serif" font-size="40">{pocket}</text>
  </g>"""


def accessory_art(palette, variant):
    _, ink, accent, soft = palette
    if variant == 0:
        return f"""
  <g transform="translate(250 330)">
    <rect x="140" y="190" width="420" height="300" rx="48" fill="{accent}" />
    <rect x="190" y="240" width="320" height="200" rx="36" fill="{soft}" />
    <path d="M250 190c20-90 120-150 200-150s180 60 200 150" fill="none" stroke="{accent}" stroke-width="38" stroke-linecap="round" />
    <text x="350" y="365" text-anchor="middle" fill="{ink}" font-family="'Archivo Expanded', Arial, sans-serif" font-size="44">ACCESSORY</text>
  </g>"""
    return f"""
  <g transform="translate(250 300)">
    <path d="M140 220c0-120 92-210 210-210s210 90 210 210v90H140Z" fill="{accent}" />
    <path d="M198 254c0-84 64-146 152-146s152 62 152 146v42H198Z" fill="{soft}" />
    <rect x="208" y="318" width="284" height="42" rx="21" fill="{ink}" fill-opacity="0.18" />
    <text x="350" y="470" text-anchor="middle" fill="{ink}" font-family="'Archivo Expanded', Arial, sans-serif" font-size="42">DETAIL</text>
  </g>"""


def bg_from(palette):
    return palette[0]


def build_art(category_slug, palette, variant):
    if category_slug == CATEGORY_SLUG_AO:
        return shirt_art(palette, variant)
    if category_slug == CATEGORY_SLUG_QUAN:
        return pants_art(palette, variant)
    return accessory_art(palette, variant)


class Command(BaseCommand):
    help = "Tạo artwork SVG nội bộ cho toàn bộ sản phẩm và gắn vào sản phẩm mà không vượt quá 6 hình."

    def handle(self, *args, **options):
        json_path = settings.BASE_DIR / "database" / "products_to_sync.json"
        name_map = {}
        if json_path.exists():
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            name_map = {item["slug"]: item["name"] for item in payload}

        generated_root = settings.MEDIA_ROOT / "products" / "generated"
        ensure_dir(generated_root)

        updated = 0
        for product in Product.objects.select_related("category").all():
            canonical_name = name_map.get(product.slug)
            if canonical_name and product.name != canonical_name:
                product.name = canonical_name

            palette = pick_palette(product.slug)
            product_dir = generated_root / product.slug
            ensure_dir(product_dir)

            cover_rel = Path("products") / "generated" / product.slug / "cover.svg"
            detail_one_rel = Path("products") / "generated" / product.slug / "detail-1.svg"
            detail_two_rel = Path("products") / "generated" / product.slug / "detail-2.svg"

            cover_path = settings.MEDIA_ROOT / cover_rel
            detail_one_path = settings.MEDIA_ROOT / detail_one_rel
            detail_two_path = settings.MEDIA_ROOT / detail_two_rel

            cover_path.write_text(
                svg_shell(product.name, "Original catalog artwork", build_art(product.category.slug, palette, 0), palette),
                encoding="utf-8",
            )
            detail_one_path.write_text(
                svg_shell(product.name, "Front / silhouette view", build_art(product.category.slug, palette, 1), palette),
                encoding="utf-8",
            )
            detail_two_path.write_text(
                svg_shell(product.name, "Close-up / detail view", build_art(product.category.slug, palette, 2), palette),
                encoding="utf-8",
            )

            if not product.image:
                product.image = str(cover_rel).replace("\\", "/")
            elif not product.image.name:
                product.image.name = str(cover_rel).replace("\\", "/")

            if not product.image_url:
                product.image_url = ""

            product.save(update_fields=["name", "image", "image_url", "updated"])

            existing_generated = list(
                product.gallery_images.filter(image__startswith=f"products/generated/{product.slug}/").order_by("sort_order", "id")
            )
            if not existing_generated:
                current_total = product.total_image_count()
                gallery_targets = [detail_one_rel, detail_two_rel]
                next_sort = product.gallery_images.count()
                for rel in gallery_targets:
                    if current_total >= 6:
                        break
                    ProductImage.objects.create(
                        product=product,
                        image=str(rel).replace("\\", "/"),
                        sort_order=next_sort,
                    )
                    next_sort += 1
                    current_total += 1

            updated += 1

        self.stdout.write(self.style.SUCCESS(f"Đã tạo và gắn artwork nội bộ cho {updated} sản phẩm."))
