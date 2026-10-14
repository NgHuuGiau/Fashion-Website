import hashlib
import json
import tempfile
from io import BytesIO, StringIO
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from PIL import Image

from .models import Category, Product, ProductVariant


class SourcedCatalogTest(TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.settings_override = override_settings(DEBUG=True, MEDIA_ROOT=self.root)
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)
        self.manifest = self.root / "catalog.json"
        self.items = []
        blobs = []
        for color in ("red", "green", "blue", "yellow"):
            stream = BytesIO()
            Image.new("RGB", (600, 800), color).save(stream, "JPEG")
            blobs.append(stream.getvalue())
        for category, count in (("ao", 30), ("quan", 40), ("phu-kien", 20)):
            for _ in range(count):
                source_id = str(len(self.items) + 1)
                directory = self.root / "products/sourced/myntra" / source_id
                directory.mkdir(parents=True)
                images = []
                for angle, blob in enumerate(blobs):
                    file = directory / f"{angle}.jpg"
                    file.write_bytes(blob)
                    images.append(
                        {
                            "file": file.relative_to(self.root).as_posix(),
                            "sha256": hashlib.sha256(blob).hexdigest(),
                        }
                    )
                self.items.append(
                    {
                        "sku": f"MYNTRA-{source_id}",
                        "slug": f"myntra-{source_id}",
                        "name": f"Source shirt {source_id}",
                        "category_slug": category,
                        "category_name": category,
                        "brand": "Source Brand",
                        "price": 200000,
                        "spec_bullets": ["Chất liệu: Cotton"],
                        "descriptors": {
                            "description": {"value": "Cotton<br>Wash cold"}
                        },
                        "images": images,
                        "attributes": {
                            "source_id": source_id,
                            "source_name": f"Source shirt {source_id}",
                            "source": "myntra-kaggle",
                            "price_is_reference": True,
                        },
                    }
                )
        self.write_manifest()

    def write_manifest(self):
        self.manifest.write_text(json.dumps(self.items), encoding="utf-8")

    def import_catalog(self):
        call_command("seed_sourced_catalog", file=str(self.manifest), stdout=StringIO())

    def test_import_is_exact_and_repeatable_preserving_old_products_and_stock(self):
        category = Category.objects.create(name="Old", slug="old")
        old = Product.objects.create(
            category=category, name="Old product", slug="old", price=100, stock=5
        )
        self.import_catalog()
        self.assertEqual(Product.objects.filter(available=True).count(), 90)
        for slug, count in (("ao", 30), ("quan", 40), ("phu-kien", 20)):
            self.assertEqual(
                Product.objects.filter(category__slug=slug, available=True).count(),
                count,
            )
        old.refresh_from_db()
        self.assertFalse(old.available)
        self.assertEqual(old.stock, 5)
        product = Product.objects.get(sku="MYNTRA-1")
        self.assertEqual(product.stock, 0)
        self.assertEqual(product.description, "Cotton\nWash cold")
        self.assertEqual(len(product.get_gallery_images()), 4)
        product.price = 300000
        product.stock = 3
        product.save()
        variant = ProductVariant.objects.create(
            product=product, color_name="Red", size="M", stock=3
        )
        self.import_catalog()
        product.refresh_from_db()
        variant.refresh_from_db()
        self.assertEqual(product.price, 300000)
        self.assertEqual(product.stock, 3)
        self.assertEqual(variant.stock, 3)
        self.assertEqual(product.gallery_images.count(), 3)
        self.assertEqual(Product.objects.count(), 91)

    def test_incomplete_catalog_does_not_change_database(self):
        self.items.pop()
        self.write_manifest()
        with self.assertRaises(CommandError):
            self.import_catalog()
        self.assertEqual(Product.objects.count(), 0)

    def test_mismatched_name_or_tampered_photo_is_rejected_before_writes(self):
        self.items[-1]["name"] = "Different item"
        self.write_manifest()
        with self.assertRaises(CommandError):
            self.import_catalog()
        self.assertEqual(Product.objects.count(), 0)
        self.items[-1]["name"] = self.items[-1]["attributes"]["source_name"]
        (self.root / self.items[-1]["images"][0]["file"]).write_bytes(b"bad image")
        self.write_manifest()
        with self.assertRaises(CommandError):
            self.import_catalog()
        self.assertEqual(Product.objects.count(), 0)

    @override_settings(DEBUG=False)
    def test_import_refused_in_production(self):
        with self.assertRaisesMessage(CommandError, "DEBUG=False"):
            self.import_catalog()

    def test_detail_uses_only_real_images_and_does_not_offer_reference_price(self):
        self.import_catalog()
        product = Product.objects.get(sku="MYNTRA-1")
        response = self.client.get(product.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        slots = response.context["detail_gallery_slots"]
        self.assertEqual(len(slots), 4)
        self.assertTrue(all(not item["is_placeholder"] for item in slots))
        self.assertNotIn("offers", response.context["product_schema"])
        self.assertContains(response, "GIÁ THAM KHẢO QUY ĐỔI")
        self.assertContains(response, "Shop chưa xác nhận giá bán, size và tồn kho")
        self.assertContains(response, '"name": "Source Brand"')
