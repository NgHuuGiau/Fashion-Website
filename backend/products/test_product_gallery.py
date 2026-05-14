import json

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import Category, Product, ProductImage, ProductVariant


class ProductGalleryViewTest(TestCase):
    TEST_IMAGE_BYTES = (
        b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00"
        b"\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00\x00"
        b"\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b"
    )

    def setUp(self):
        self.category = Category.objects.create(name="Áo", slug="ao")
        self.product = Product.objects.create(
            category=self.category,
            name="Áo gallery",
            slug="ao-gallery",
            description="Mô tả test",
            price=390000,
            stock=8,
            available=True,
        )
        ProductVariant.objects.create(
            product=self.product,
            color_name="Đen",
            color_code="#111111",
            size="M",
            stock=4,
            is_active=True,
        )

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
        payload = json.loads(response.context["variant_data_json"])
        self.assertEqual(payload[0]["size"], "M")
