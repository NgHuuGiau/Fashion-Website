"""Nap anh demo Unsplash cho san pham (chi DEV).

Anh that de duyet layout nhu DirtyCoins/SWE/Levents. Anh nay KHONG phai
anh that cua san pham - shop phai upload anh that truoc khi ban.
Chi chay khi DEBUG=True; co anh that roi thi bo qua (idempotent).
"""

import time
import urllib.request

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError

from products.models import Product, ProductImage

AO_IDS = [
    "1521572163474-6864f9cf17ab",
    "1576566588028-4147f3842f27",
    "1523381210434-271e8be1f52b",
    "1620799140408-edc6dcb6d633",
    "1618354691373-d851c5c3a990",
    "1611312449408-fcece27cdbb7",
    "1591047139829-d91aecb6caea",
    "1552374196-c4e7ffc6e126",
]
QUAN_IDS = [
    "1542272604-787c3835535d",
    "1541099649105-f69ad21f3246",
    "1594633312681-425c7b97ccd1",
    "1583743814966-8936f5b7be1a",
    "1602810318383-e386cc2a3ccf",
    "1591195853828-11db59a44f6b",
]
PHUKIEN_IDS = [
    "1553062407-98eeb64c6a62",
    "1525966222134-fcfa99b8ae77",
    "1588850561407-ed78c282e89b",
    "1521369909029-2afed882baee",
    "1588117260148-b47818741c74",
    "1610652492500-ded49ceeb378",
]


def pool_for(product):
    slug = (product.category.slug if product.category else "").lower()
    if "quan" in slug:
        return QUAN_IDS
    if "phu-kien" in slug or "phukien" in slug:
        return PHUKIEN_IDS
    return AO_IDS


def fetch_photo(photo_id, w=1200, h=1500):
    url = (
        f"https://images.unsplash.com/photo-{photo_id}"
        f"?q=80&w={w}&h={h}&fit=crop&auto=format&fm=jpg"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    # This development-only downloader always builds HTTPS URLs on the Unsplash image host.
    return urllib.request.urlopen(req, timeout=30).read()  # nosec B310


def has_real_image(product):
    try:
        return bool(product.image and product.image.storage.exists(product.image.name))
    except Exception:
        return False


class Command(BaseCommand):
    help = "Nap anh demo Unsplash (1200x1500, 4:5) cho san pham chua co anh. Chi DEV."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit", type=int, default=0, help="Chi nap N san pham dau (0 = tat ca)."
        )
        parser.add_argument(
            "--overwrite", action="store_true", help="Nap lai ke ca SP da co anh."
        )

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Tu choi nap anh demo khi DEBUG=False.")
        qs = Product.objects.select_related("category").order_by("id")
        limit = options["limit"] or 0
        if limit:
            qs = qs[:limit]
        done, skipped = 0, 0
        for index, product in enumerate(qs):
            if has_real_image(product) and not options["overwrite"]:
                skipped += 1
                continue
            pool = pool_for(product)
            picks = [pool[(index + k) % len(pool)] for k in range(3)]
            try:
                main = fetch_photo(picks[0])
                product.image.save(
                    f"demo_{product.id}_main.jpg", ContentFile(main), save=True
                )
                product.gallery_images.all().delete()
                for pos, pid in enumerate(picks[1:], start=1):
                    blob = fetch_photo(pid, w=800, h=1000)
                    ProductImage.objects.create(
                        product=product,
                        sort_order=pos,
                        image=ContentFile(blob, name=f"demo_{product.id}_g{pos}.jpg"),
                    )
                done += 1
                self.stdout.write(f"  #{product.id} {product.slug[:30]} ok")
            except Exception as exc:
                self.stdout.write(self.style.WARNING(f"  #{product.id} loi: {exc}"))
            time.sleep(0.2)
        self.stdout.write(
            self.style.SUCCESS(f"Xong: {done} nap moi, {skipped} bo qua.")
        )
