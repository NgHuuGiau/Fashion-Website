from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from products.models import Category, Product, ProductImage, ProductVariant


class ProductImageLimitAdminTest(TestCase):
    TEST_IMAGE_BYTES = (
        b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00"
        b"\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00\x00"
        b"\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b"
    )

    def setUp(self):
        self.staff = User.objects.create_user(username="staff_gallery", password="StrongPass123!", is_staff=True)
        self.category = Category.objects.create(name="Áo", slug="ao")
        self.product = Product.objects.create(
            category=self.category,
            name="Áo giới hạn ảnh",
            slug="ao-gioi-han-anh",
            description="Test giới hạn ảnh",
            price=420000,
            stock=5,
            available=True,
            image_url="https://example.com/cover.jpg",
        )
        ProductVariant.objects.create(
            product=self.product,
            color_name="Đen",
            color_code="#111111",
            size="M",
            stock=5,
            is_active=True,
        )

    def test_admin_rejects_more_than_six_total_images(self):
        self.client.login(username="staff_gallery", password="StrongPass123!")

        for index in range(5):
            ProductImage.objects.create(
                product=self.product,
                image=SimpleUploadedFile(f"existing-{index}.gif", self.TEST_IMAGE_BYTES, content_type="image/gif"),
                sort_order=index,
            )

        upload_payload = {
            "action": "save_product",
            "product_id": str(self.product.id),
            "category_id": str(self.category.id),
            "name": self.product.name,
            "price": "420000",
            "stock": "0",
            "description": self.product.description,
            "image_url": self.product.image_url,
            "available": "on",
            "gallery_count": "5",
            "variant_row_key[]": ["row-1"],
            "variant_color_name[]": ["Đen"],
            "variant_color_code[]": ["#111111"],
            "variant_size[]": ["M"],
            "variant_stock[]": ["5"],
            "variant_is_active[]": ["row-1"],
            "gallery_images": [
                SimpleUploadedFile("new-1.gif", self.TEST_IMAGE_BYTES, content_type="image/gif"),
            ],
        }

        response = self.client.post(reverse("orders:admin_dashboard"), upload_payload)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "tối đa 6 hình ảnh")
        self.assertEqual(self.product.gallery_images.count(), 5)
