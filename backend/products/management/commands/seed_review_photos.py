from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from products.models import Review


SVG_TPL = """<svg xmlns="http://www.w3.org/2000/svg" width="640" height="480">
  <rect width="640" height="480" fill="#{bg}"/>
  <circle cx="480" cy="120" r="60" fill="#fff" opacity="0.25"/>
  <rect x="60" y="260" width="520" height="16" rx="8" fill="#fff" opacity="0.9"/>
  <rect x="60" y="290" width="380" height="12" rx="6" fill="#fff" opacity="0.6"/>
  <text x="60" y="150" font-family="Arial" font-size="34" fill="#fff">{label}</text>
</svg>"""

PHOTOS = [
    ("#8a5a3a", "Outfit thực tế - áo"),
    ("#3a5a7a", "Mặc thử tại nhà"),
    ("#5a3a6a", "Form chuẩn, vải dày"),
    ("#2a5a4a", "Màu đẹp như hình"),
]


class Command(BaseCommand):
    help = "Gán ảnh thực tế cho một số đánh giá để demo"

    def handle(self, *args, **options):
        reviews = list(
            Review.objects.filter(is_published=True, image="").select_related("product").order_by("?")[:12]
        )
        photo_dir = Path("frontend/static/images/reviews")
        photo_dir.mkdir(parents=True, exist_ok=True)
        count = 0
        for i, review in enumerate(reviews):
            bg, label = PHOTOS[i % len(PHOTOS)]
            name = f"{review.product.slug or 'sp'}-review-{review.id}.svg"
            path = photo_dir / name
            if not path.exists():
                path.write_text(SVG_TPL.format(bg=bg, label=label), encoding="utf-8")
            review.image.save(name, ContentFile(path.read_bytes()), save=True)
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Seeded {count} review photos"))
