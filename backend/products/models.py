from pathlib import Path

from django.conf import settings
from django.db import models

from .constants import APPAREL_CATEGORY_SLUGS


MAX_PRODUCT_GALLERY_IMAGES = 6
GENERATED_DETAIL_IMAGE_FILENAMES = ("detail-1.svg", "detail-2.svg")


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên danh mục")
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "Danh mục"
        verbose_name_plural = "Danh mục"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, related_name="products", on_delete=models.CASCADE)
    name = models.CharField(max_length=200, verbose_name="Tên sản phẩm")
    slug = models.SlugField(max_length=200)
    image = models.ImageField(upload_to="products/%Y/%m/%d", blank=True, verbose_name="Ảnh sản phẩm")
    image_url = models.URLField(blank=True, verbose_name="URL ảnh")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Giá tiền")
    stock = models.PositiveIntegerField(default=0, verbose_name="Số lượng kho")
    available = models.BooleanField(default=True, verbose_name="Đang bán")
    featured = models.BooleanField(default=False, verbose_name="Nổi bật")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created",)
        indexes = [
            models.Index(fields=["id", "slug"]),
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name

    @property
    def requires_variants(self):
        return self.category.slug in APPAREL_CATEGORY_SLUGS

    def get_image(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url

        generated_cover = self._build_generated_asset_url("cover.svg")
        if generated_cover:
            return generated_cover

        first_gallery_image = self.gallery_images.order_by("sort_order", "id").first()
        if first_gallery_image:
            return first_gallery_image.image.url
        return ""

    def _build_generated_asset_url(self, filename):
        if not self.slug:
            return ""

        relative_path = Path("products") / "generated" / self.slug / filename
        asset_path = Path(settings.MEDIA_ROOT) / relative_path
        if not asset_path.exists():
            return ""

        relative_url = str(relative_path).replace("\\", "/")
        return f"{settings.MEDIA_URL}{relative_url}"

    def _generated_detail_images(self):
        images = []
        for filename in GENERATED_DETAIL_IMAGE_FILENAMES:
            image_url = self._build_generated_asset_url(filename)
            if image_url:
                images.append({"url": image_url, "is_primary": False})
        return images

    @staticmethod
    def _append_unique_image(images, seen_urls, image_url, is_primary):
        if not image_url or image_url in seen_urls:
            return
        images.append({"url": image_url, "is_primary": is_primary})
        seen_urls.add(image_url)

    def get_gallery_images(self, include_primary=True):
        images = []
        seen_urls = set()

        primary_url = self.get_image() if include_primary else ""
        self._append_unique_image(images, seen_urls, primary_url, True)

        for item in self.gallery_images.order_by("sort_order", "id"):
            self._append_unique_image(images, seen_urls, item.image.url, False)

        if not images:
            for generated_image in self._generated_detail_images():
                self._append_unique_image(images, seen_urls, generated_image["url"], generated_image["is_primary"])

        return images[:MAX_PRODUCT_GALLERY_IMAGES]

    def get_detail_gallery_images(self):
        images = self.get_gallery_images(include_primary=False)
        if images:
            return images

        primary_url = self.get_image()
        if primary_url:
            return [{"url": primary_url, "is_primary": True}]
        return []

    def total_image_count(self):
        base_count = 1 if (self.image or self.image_url) else 0
        return min(MAX_PRODUCT_GALLERY_IMAGES, base_count + self.gallery_images.count())


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name="variants", on_delete=models.CASCADE)
    color_name = models.CharField(max_length=50, verbose_name="Màu sắc")
    color_code = models.CharField(max_length=20, default="#111111", verbose_name="Mã màu")
    size = models.CharField(max_length=20, verbose_name="Size")
    stock = models.PositiveIntegerField(default=0, verbose_name="Tồn kho")
    is_active = models.BooleanField(default=True, verbose_name="Hiển thị")

    class Meta:
        ordering = ["color_name", "size"]
        unique_together = ("product", "color_name", "size")

    def __str__(self):
        return f"{self.product.name} - {self.color_name} / {self.size}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name="gallery_images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="products/gallery/%Y/%m/%d", verbose_name="Ảnh gallery")
    sort_order = models.PositiveSmallIntegerField(default=0, verbose_name="Thứ tự")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Ảnh sản phẩm"
        verbose_name_plural = "Ảnh sản phẩm"
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.product.name} - ảnh {self.id}"


class WishlistItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlist_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishlist_items")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Sản phẩm yêu thích"
        verbose_name_plural = "Sản phẩm yêu thích"
        ordering = ["-created"]
        unique_together = ("user", "product")

    def __str__(self):
        return f"{self.user} - {self.product.name}"


class SupportFAQ(models.Model):
    question = models.CharField(max_length=255, verbose_name="Câu hỏi")
    keywords = models.CharField(max_length=255, blank=True, verbose_name="Từ khóa")
    answer = models.TextField(verbose_name="Câu trả lời")
    priority = models.PositiveSmallIntegerField(default=100, verbose_name="Độ ưu tiên")
    is_active = models.BooleanField(default=True, verbose_name="Đang dùng")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "FAQ hỗ trợ"
        verbose_name_plural = "FAQ hỗ trợ"
        ordering = ["priority", "id"]
        indexes = [
            models.Index(fields=["is_active", "priority"]),
            models.Index(fields=["question"]),
        ]

    def __str__(self):
        return self.question
