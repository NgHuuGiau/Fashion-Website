from pathlib import Path
from tempfile import TemporaryDirectory
import json

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Category, Product, ProductImage, ProductVariant


class ProductGalleryViewTest(TestCase):
    TEST_IMAGE_BYTES = (
        b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00"
        b"\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00\x00"
        b"\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b"
    )

    def setUp(self):
        self.temp_media = TemporaryDirectory()
        self.media_override = override_settings(MEDIA_ROOT=self.temp_media.name, MEDIA_URL="/media/")
        self.media_override.enable()

        self.category = Category.objects.create(name="Ao", slug="ao")
        self.product = Product.objects.create(
            category=self.category,
            name="Ao gallery",
            slug="ao-gallery",
            description="Mo ta test",
            price=390000,
            stock=8,
            available=True,
        )
        ProductVariant.objects.create(
            product=self.product,
            color_name="Den",
            color_code="#111111",
            size="M",
            stock=4,
            is_active=True,
        )

    def tearDown(self):
        self.media_override.disable()
        self.temp_media.cleanup()

    def test_product_detail_includes_gallery_images(self):
        ProductImage.objects.create(
            product=self.product,
            image=SimpleUploadedFile("gallery-1.gif", self.TEST_IMAGE_BYTES, content_type="image/gif"),
            sort_order=0,
        )
        ProductImage.objects.create(
            product=self.product,
            image=SimpleUploadedFile("gallery-2.gif", self.TEST_IMAGE_BYTES, content_type="image/gif"),
            sort_order=1,
        )

        response = self.client.get(
            reverse("products:product_detail", kwargs={"pk": self.product.id, "slug": self.product.slug})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["gallery_images"]), 2)
        self.assertEqual(len(response.context["detail_gallery_slots"]), 6)
        self.assertFalse(response.context["detail_gallery_slots"][0]["is_placeholder"])
        self.assertTrue(response.context["detail_gallery_slots"][5]["is_placeholder"])
        payload = json.loads(response.context["variant_data_json"])
        self.assertEqual(payload[0]["size"], "M")

    def test_product_detail_falls_back_to_generated_detail_images(self):
        product_asset_dir = Path(self.temp_media.name) / "products" / "generated" / self.product.slug
        product_asset_dir.mkdir(parents=True, exist_ok=True)
        (product_asset_dir / "detail-1.svg").write_text("<svg></svg>", encoding="utf-8")
        (product_asset_dir / "detail-2.svg").write_text("<svg></svg>", encoding="utf-8")

        response = self.client.get(
            reverse("products:product_detail", kwargs={"pk": self.product.id, "slug": self.product.slug})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["gallery_images"],
            [
                {"url": f"/media/products/generated/{self.product.slug}/detail-1.svg", "is_primary": False},
                {"url": f"/media/products/generated/{self.product.slug}/detail-2.svg", "is_primary": False},
            ],
        )
        self.assertEqual(len(response.context["detail_gallery_slots"]), 6)
