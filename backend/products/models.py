from pathlib import Path
from urllib.parse import quote

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
    slug = models.SlugField(max_length=200, db_index=True)
    image = models.ImageField(upload_to="products/%Y/%m/%d", blank=True, verbose_name="Ảnh sản phẩm")
    image_url = models.URLField(blank=True, verbose_name="URL ảnh")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Giá tiền", db_index=True)
    stock = models.PositiveIntegerField(default=0, verbose_name="Số lượng kho", db_index=True)
    available = models.BooleanField(default=True, verbose_name="Đang bán", db_index=True)
    featured = models.BooleanField(default=False, verbose_name="Nổi bật", db_index=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        ordering = ("-created",)
        indexes = [
            models.Index(fields=["id", "slug"]),
            models.Index(fields=["name"]),
            models.Index(fields=["available", "featured", "price"]),
            models.Index(fields=["available", "stock"]),
            models.Index(fields=["category", "available", "-created"]),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("products:product_detail", kwargs={"pk": self.id, "slug": self.slug})
        if not relative_name:
            return False
        return (Path(settings.MEDIA_ROOT) / relative_name).exists()

    def _build_placeholder_image(self):
        category_label = (self.category.name or self.category.slug or "HUUGIAU").upper().replace("-", " ")
        product_label = (self.name or "HUUGIAU").upper()
        svg = f"""
        <svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 900 1125'>
            <defs>
                <linearGradient id='bg' x1='0' y1='0' x2='1' y2='1'>
                    <stop offset='0%' stop-color='#fffdf8' />
                    <stop offset='100%' stop-color='#f1e1d0' />
                </linearGradient>
            </defs>
            <rect width='900' height='1125' rx='42' fill='url(#bg)' />
            <circle cx='720' cy='140' r='150' fill='#8a4a2a' fill-opacity='0.1' />
            <circle cx='170' cy='920' r='180' fill='#ffffff' fill-opacity='0.7' />
            <rect x='84' y='86' width='732' height='953' rx='34' fill='none' stroke='#d9c2b0' stroke-dasharray='18 12' />
            <text x='450' y='420' text-anchor='middle' fill='#8a4a2a' font-family='Arial, sans-serif' font-size='56' font-weight='800' letter-spacing='8'>{category_label}</text>
            <text x='450' y='530' text-anchor='middle' fill='#16110f' font-family='Arial, sans-serif' font-size='78' font-weight='900'>{product_label[:24]}</text>
            <text x='450' y='620' text-anchor='middle' fill='#7b6758' font-family='Arial, sans-serif' font-size='30' font-weight='700'>HUUGIAU LOOKBOOK</text>
        </svg>
        """.strip()
        return f"data:image/svg+xml;utf8,{quote(svg)}"

    @property
    def requires_variants(self):
        return self.category.slug in APPAREL_CATEGORY_SLUGS

    def get_image(self):
        if self.image and self._media_file_exists(self.image.name):
            return self.image.url
        if self.image_url:
            return self.image_url

        generated_cover = self._build_generated_asset_url("cover.svg")
        if generated_cover:
            return generated_cover

        first_gallery_image = self.gallery_images.order_by("sort_order", "id").first()
        if first_gallery_image and self._media_file_exists(first_gallery_image.image.name):
            return first_gallery_image.image.url
        return self._build_placeholder_image()

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
            if self._media_file_exists(item.image.name):
                self._append_unique_image(images, seen_urls, item.image.url, False)

        if not images:
            for generated_image in self._generated_detail_images():
                self._append_unique_image(images, seen_urls, generated_image["url"], generated_image["is_primary"])

        if not images:
            if include_primary:
                self._append_unique_image(images, seen_urls, self._build_placeholder_image(), True)

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
        base_count = 1 if (self.image_url or (self.image and self._media_file_exists(self.image.name))) else 0
        return min(MAX_PRODUCT_GALLERY_IMAGES, base_count + self.gallery_images.count())


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name="variants", on_delete=models.CASCADE)
    color_name = models.CharField(max_length=50, verbose_name="Màu sắc", db_index=True)
    color_code = models.CharField(max_length=20, default="#111111", verbose_name="Mã màu")
    size = models.CharField(max_length=20, verbose_name="Size", db_index=True)
    stock = models.PositiveIntegerField(default=0, verbose_name="Tồn kho", db_index=True)
    is_active = models.BooleanField(default=True, verbose_name="Hiển thị", db_index=True)

    class Meta:
        ordering = ["color_name", "size"]
        unique_together = ("product", "color_name", "size")

    def __str__(self):
        return f"{self.product.name} - {self.color_name} / {self.size}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name="gallery_images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="products/gallery/%Y/%m/%d", verbose_name="Ảnh gallery")
    sort_order = models.PositiveSmallIntegerField(default=0, verbose_name="Thứ tự", db_index=True)
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


class Review(models.Model):
    RATING_CHOICES = [(i, f"{i} sao") for i in range(1, 6)]

    product = models.ForeignKey(Product, related_name="reviews", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="reviews", on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, verbose_name="Số sao", db_index=True)
    comment = models.TextField(blank=True, verbose_name="Nội dung đánh giá")
    is_published = models.BooleanField(default=True, verbose_name="Hiển thị", db_index=True)
    verified_purchase = models.BooleanField(default=False, verbose_name="Đã mua hàng", db_index=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Đánh giá sản phẩm"
        verbose_name_plural = "Đánh giá sản phẩm"
        ordering = ["-created"]
        unique_together = ("product", "user")
        indexes = [
            models.Index(fields=["product", "is_published", "-created"]),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.rating}★ - {self.user}"


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
