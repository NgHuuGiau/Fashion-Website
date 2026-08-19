from pathlib import Path
from urllib.parse import quote

from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.utils import timezone

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
    compare_price = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True, verbose_name="Giá gốc (trước khuyến mãi)")
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

        first_gallery_image = list(self.gallery_images.all()[:1])
        if first_gallery_image and self._media_file_exists(first_gallery_image[0].image.name):
            return first_gallery_image[0].image.url
        return self._build_placeholder_image()

    @property
    def discount_percent(self):
        if self.compare_price and self.compare_price > self.price:
            return int((self.compare_price - self.price) * 100 / self.compare_price)
        return 0

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

        for item in self.gallery_images.all():
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

    def get_total_stock(self):
        variant_stock = self.variants.filter(is_active=True).aggregate(total=Sum("stock"))["total"]
        if variant_stock is not None:
            return variant_stock
        return self.stock

    def get_cross_sell_products(self, limit=4):
        """Sản phẩm thường được mua cùng (cross-sell) dựa trên lịch sử đơn hàng."""
        from orders.models import OrderItem

        # Tìm các đơn hàng chứa sản phẩm này
        order_ids = OrderItem.objects.filter(product=self).values_list("order_id", flat=True).distinct()

        # Tìm sản phẩm khác trong cùng đơn hàng
        cross_sell_ids = (
            OrderItem.objects.filter(order_id__in=order_ids)
            .exclude(product=self)
            .values("product_id")
            .annotate(cnt=models.Count("product_id"))
            .order_by("-cnt")[:limit]
        )

        ids = [item["product_id"] for item in cross_sell_ids]
        return Product.objects.filter(id__in=ids, available=True).only(
            "id", "name", "slug", "price", "discount_percent", "image", "image_url"
        )


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
    shop_reply = models.TextField(blank=True, verbose_name="Shop phản hồi")
    customer_reply = models.TextField(blank=True, verbose_name="Khách hàng phản hồi shop")
    image = models.ImageField(upload_to="reviews/%Y/%m/%d", blank=True, verbose_name="Ảnh kèm đánh giá")
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


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True, verbose_name="Email")
    is_active = models.BooleanField(default=True, verbose_name="Đang nhận tin", db_index=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Đăng ký nhận tin"
        verbose_name_plural = "Đăng ký nhận tin"
        ordering = ["-created"]

    def __str__(self):
        return self.email


class BlogPost(models.Model):
    title = models.CharField(max_length=200, verbose_name="Tiêu đề")
    slug = models.SlugField(max_length=220, unique=True, db_index=True, verbose_name="Slug")
    excerpt = models.CharField(max_length=300, blank=True, verbose_name="Mô tả ngắn")
    body = models.TextField(verbose_name="Nội dung")
    cover_image_url = models.URLField(blank=True, verbose_name="URL ảnh bìa")
    is_published = models.BooleanField(default=True, verbose_name="Hiển thị", db_index=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Bài viết / Lookbook"
        verbose_name_plural = "Bài viết / Lookbook"
        ordering = ["-created"]
        indexes = [models.Index(fields=["is_published", "-created"])]

    def __str__(self):
        return self.title


class ProductQuestion(models.Model):
    product = models.ForeignKey(Product, related_name="questions", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="product_questions", on_delete=models.CASCADE)
    question = models.TextField(verbose_name="Câu hỏi")
    answer = models.TextField(blank=True, verbose_name="Trả lời")
    is_published = models.BooleanField(default=True, verbose_name="Hiển thị", db_index=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    answered_at = models.DateTimeField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Hỏi đáp sản phẩm"
        verbose_name_plural = "Hỏi đáp sản phẩm"
        ordering = ["-created"]
        indexes = [models.Index(fields=["product", "is_published", "-created"])]

    def __str__(self):
        return f"{self.product.name} - {self.user.username}"

    def save(self, *args, **kwargs):
        if self.answer and not self.answered_at:
            self.answered_at = timezone.now()
        super().save(*args, **kwargs)


class BackInStock(models.Model):
    product = models.ForeignKey(Product, related_name="back_in_stock_requests", on_delete=models.CASCADE)
    email = models.EmailField(max_length=254, verbose_name="Email")
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    notified = models.BooleanField(default=False, verbose_name="Đã gửi thông báo")

    class Meta:
        verbose_name = "Báo khi có hàng"
        verbose_name_plural = "Báo khi có hàng"
        ordering = ["-created"]
        constraints = [
            models.UniqueConstraint(fields=["product", "email"], name="unique_backinstock_product_email")
        ]

    def __str__(self):
        return f"{self.email} - {self.product.name}"
