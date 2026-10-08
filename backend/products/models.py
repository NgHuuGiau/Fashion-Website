from html import escape
from pathlib import Path
from textwrap import wrap
from urllib.parse import quote

from django.conf import settings
from django.db import models
from django.db.models import Q, Sum
from django.utils import timezone

from .constants import APPAREL_CATEGORY_SLUGS
from .validators import validate_product_image


MAX_PRODUCT_GALLERY_IMAGES = 6
GENERATED_DETAIL_IMAGE_FILENAMES = ("detail-1.svg", "detail-2.svg")

# ponytail: 1 bo line-art chung cho placeholder (card + gallery), phan biet theo loai
# chu khong dung hop text xau. Toa do tren viewBox 900x1125.
GARMENT_ART = {
    # ao thun: vai - tay - than
    "ao": (
        "<path d='M318,300 L398,256 Q450,288 502,256 L582,300 L648,392 "
        "L578,424 L566,378 L566,806 L334,806 L334,378 L322,424 L252,392 Z' />"
        "<path d='M398,256 Q450,288 502,256' />"
    ),
    # quan dai: cap - 2 ong
    "quan": (
        "<path d='M336,250 L564,250 L582,806 L476,806 L450,470 L424,806 "
        "L318,806 Z' />"
        "<path d='M336,292 L564,292' />"
    ),
    # mu: vom + luoi trai + nut
    "phukien": (
        "<path d='M296,500 Q296,330 450,330 Q604,330 604,500 Z' />"
        "<path d='M228,500 L672,500 L672,524 L228,524 Z' />"
        "<circle cx='450' cy='306' r='14' />"
    ),
    # mac ao (hanger): dung cho loai la
    "generic": (
        "<circle cx='450' cy='318' r='30' />"
        "<path d='M450,348 L450,372 M450,372 L252,640 L648,640 Z' />"
    ),
}

GARMENT_INK = "#2e2620"


def garment_key_for_slug(slug):
    slug = (slug or "").lower()
    if "quan" in slug:
        return "quan"
    if "phu-kien" in slug or "phukien" in slug or "mu" in slug or "tui" in slug or "giay" in slug:
        return "phukien"
    if "ao" in slug:
        return "ao"
    return "generic"


def garment_group(slug, cx=450, cy=540, scale=1.0):
    key = garment_key_for_slug(slug)
    paths = GARMENT_ART.get(key, GARMENT_ART["generic"])
    return (
        "<g transform='translate({0},{1}) scale({2}) translate(-450,-540)' "
        "fill='none' stroke='{3}' stroke-width='9' stroke-linecap='round' "
        "stroke-linejoin='round'>{4}</g>"
    ).format(cx, cy, scale, GARMENT_INK, paths)


PLACEHOLDER_BG_TOP = "#faf7f1"
PLACEHOLDER_BG_BOTTOM = "#ece2d2"


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên danh mục")
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "Danh mục"
        verbose_name_plural = "Danh mục"
        ordering = ["name"]

    def __str__(self):
        return self.name



class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Ten thuong hieu")
    slug = models.SlugField(max_length=100, unique=True, db_index=True)
    logo = models.ImageField(upload_to="brands/", blank=True, verbose_name="Logo")
    description = models.TextField(blank=True, verbose_name="Mo ta")
    is_active = models.BooleanField(default=True, verbose_name="Hoat dong")
    # ponytail: size guide per brand - JSON {size: {chest, waist, hip, length}}
    size_guide = models.JSONField(default=dict, blank=True, verbose_name="Bang size")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "Thuong hieu"
        verbose_name_plural = "Thuong hieu"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("products:brand_detail", kwargs={"slug": self.slug})


class Collection(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Ten bo suu tap")
    slug = models.SlugField(max_length=100, unique=True, db_index=True)
    image = models.ImageField(upload_to="collections/", blank=True, verbose_name="Anh bo suu tap")
    description = models.TextField(blank=True, verbose_name="Mo ta")
    is_active = models.BooleanField(default=True, verbose_name="Hoat dong")
    featured = models.BooleanField(default=False, verbose_name="Noi bat")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created",)
        verbose_name = "Bo suu tap"
        verbose_name_plural = "Cac bo suu tap"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("products:collection_detail", kwargs={"slug": self.slug})


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Ten tag")
    slug = models.SlugField(max_length=50, unique=True, db_index=True)
    color = models.CharField(max_length=7, default="#6366f1", verbose_name="Mau sac")
    is_active = models.BooleanField(default=True, verbose_name="Hoat dong")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category, related_name="products", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=200, verbose_name="Tên sản phẩm")
    slug = models.SlugField(max_length=200, db_index=True)
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="Mã SKU", db_index=True)
    image = models.ImageField(
        upload_to="products/%Y/%m/%d",
        blank=True,
        validators=[validate_product_image],
        verbose_name="Ảnh sản phẩm",
    )
    image_url = models.URLField(blank=True, verbose_name="URL ảnh")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    price = models.DecimalField(
        max_digits=10, decimal_places=0, verbose_name="Giá tiền", db_index=True
    )
    compare_price = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        null=True,
        blank=True,
        verbose_name="Giá gốc (trước khuyến mãi)",
    )
    stock = models.PositiveIntegerField(
        default=0, verbose_name="Số lượng kho", db_index=True
    )
    available = models.BooleanField(
        default=True, verbose_name="Đang bán", db_index=True
    )
    featured = models.BooleanField(default=False, verbose_name="Nổi bật", db_index=True)
    # SEO fields
    meta_title = models.CharField(max_length=60, blank=True, verbose_name="SEO Title")
    meta_description = models.CharField(max_length=160, blank=True, verbose_name="SEO Description")
    meta_keywords = models.CharField(max_length=255, blank=True, verbose_name="SEO Keywords")
    # Brand & Collection
    brand = models.ForeignKey(
        'Brand', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='products', verbose_name="Thương hiệu"
    )
    collection = models.ForeignKey(
        'Collection', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='products', verbose_name="Bộ sưu tập"
    )
    # Tags for filtering
    tags = models.ManyToManyField('Tag', blank=True, related_name='products', verbose_name="Tags")
    # Attributes for flexible filtering (color, size, material, etc.)
    attributes = models.JSONField(default=dict, blank=True, verbose_name="Thuộc tính")
    # Inventory tracking
    reserved_stock = models.PositiveIntegerField(default=0, verbose_name="Số lượng đã giữ")
    low_stock_threshold = models.PositiveIntegerField(default=5, verbose_name="Ngưỡng cảnh báo tồn kho")
    track_inventory = models.BooleanField(default=True, verbose_name="Theo dõi tồn kho")
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        ordering = ("-created",)
        indexes = [
            models.Index(fields=["id", "slug"]),
            models.Index(fields=["name"]),
            models.Index(fields=["sku"]),
            models.Index(fields=["available", "featured", "price"]),
            models.Index(fields=["available", "stock"]),
            models.Index(fields=["category", "available", "-created"]),
            models.Index(fields=["brand", "available", "-created"]),
            models.Index(fields=["collection", "available", "-created"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(stock__gte=0),
                name="product_stock_non_negative",
            ),
            models.CheckConstraint(
                condition=Q(reserved_stock__gte=0),
                name="product_reserved_stock_non_negative",
            ),
            models.CheckConstraint(
                condition=Q(reserved_stock__lte=models.F('stock')),
                name="product_reserved_not_exceed_stock",
            ),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Auto-generate SKU if not provided
        if not self.sku and self.name:
            import re
            base = re.sub(r'[^a-zA-Z0-9]', '', self.name.upper())[:20]
            import uuid
            self.sku = "{}-{}".format(base, uuid.uuid4().hex[:8].upper())
        # P3.2: ghi lich su khi gia doi (cover dashboard + admin + shell).
        # Bo qua khi save chi update stock (checkout hot path).
        update_fields = kwargs.get("update_fields")
        watch_price = update_fields is None or "price" in update_fields
        old_price = None
        if self.pk and watch_price:
            old_price = (
                type(self)
                .objects.filter(pk=self.pk)
                .values_list("price", flat=True)
                .first()
            )
        super().save(*args, **kwargs)
        if old_price is not None and old_price != self.price:
            PriceHistory.objects.create(
                product=self,
                old_price=old_price,
                new_price=self.price,
                changed_by=getattr(self, "_price_changed_by", ""),
            )

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse(
            "products:product_detail", kwargs={"pk": self.id, "slug": self.slug}
        )

    def _media_file_exists(self, relative_name):
        if not relative_name:
            return False
        return (Path(settings.MEDIA_ROOT) / relative_name).exists()

    def _build_placeholder_image(self):
        slug = self.category.slug if self.category else ""
        category_label = (
            (self.category.name or slug or "HUUGIAU")
            .upper()
            .replace("-", " ")
        )
        product_label_raw = (self.name or "HUUGIAU").upper()
        product_lines = wrap(
            product_label_raw,
            width=22,
            break_long_words=False,
            break_on_hyphens=False,
        ) or ["HUUGIAU"]
        product_lines = product_lines[:2]
        if len(product_lines) == 2 and len(wrap(product_label_raw, width=22)) > 2:
            product_lines[1] = "{}...".format(product_lines[1][:19].rstrip())
        product_lines = [escape(line) for line in product_lines]
        title_svg = "".join(
            "<text x='450' y='{0}' text-anchor='middle' "
            "fill='#241c16' font-family='Georgia, Times New Roman, serif' "
            "font-size='46' font-weight='400' letter-spacing='2'>{1}</text>".format(
                912 + index * 58, line
            )
            for index, line in enumerate(product_lines)
        )
        category_label = escape(category_label)
        art = garment_group(slug, cx=450, cy=520, scale=0.92)
        svg = """
        <svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 900 1125'>
            <defs>
                <linearGradient id='bg' x1='0' y1='0' x2='0' y2='1'>
                    <stop offset='0%' stop-color='{bg_top}' />
                    <stop offset='100%' stop-color='{bg_bottom}' />
                </linearGradient>
                <radialGradient id='halo' cx='50%' cy='42%' r='45%'>
                    <stop offset='0%' stop-color='#ffffff' stop-opacity='0.85' />
                    <stop offset='100%' stop-color='#ffffff' stop-opacity='0' />
                </radialGradient>
            </defs>
            <rect width='900' height='1125' fill='url(#bg)' />
            <ellipse cx='450' cy='470' rx='330' ry='330' fill='url(#halo)' />
            <circle cx='450' cy='148' r='52' fill='none' stroke='#2e2620' stroke-width='5' />
            <text x='450' y='166' text-anchor='middle' fill='#2e2620' font-family='Georgia, Times New Roman, serif' font-size='52'>H</text>
            {art}
            <text x='450' y='858' text-anchor='middle' fill='#96754f' font-family='Arial, sans-serif' font-size='30' font-weight='700' letter-spacing='10'>{category_label}</text>
            {title_svg}
            <text x='450' y='1062' text-anchor='middle' fill='#a08b74' font-family='Arial, sans-serif' font-size='22' font-weight='600' letter-spacing='6'>HUUGIAU ATELIER</text>
        </svg>
        """.strip().format(
            bg_top=PLACEHOLDER_BG_TOP,
            bg_bottom=PLACEHOLDER_BG_BOTTOM,
            art=art,
            category_label=category_label,
            title_svg=title_svg,
        )
        return "data:image/svg+xml;utf8,{0}".format(quote(svg))

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
        if first_gallery_image and self._media_file_exists(
            first_gallery_image[0].image.name
        ):
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
        return "{0}{1}".format(settings.MEDIA_URL, relative_url)

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
                self._append_unique_image(
                    images,
                    seen_urls,
                    generated_image["url"],
                    generated_image["is_primary"],
                )

        if not images:
            if include_primary:
                self._append_unique_image(
                    images, seen_urls, self._build_placeholder_image(), True
                )

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
        base_count = (
            1
            if (
                self.image_url
                or (self.image and self._media_file_exists(self.image.name))
            )
            else 0
        )
        return min(MAX_PRODUCT_GALLERY_IMAGES, base_count + self.gallery_images.count())

    def get_total_stock(self):
        variant_stock = self.variants.filter(is_active=True).aggregate(
            total=Sum("stock")
        )["total"]
        if variant_stock is not None:
            return variant_stock
        return self.stock

    def get_effective_price(self):
        # ponytail: gia flash sale neu dang chay, khong thi gia thuong - 1 cho duy nhat
        try:
            now = timezone.now()
            item = self.flash_items.filter(sale__is_active=True, sale__starts_at__lte=now, sale__ends_at__gte=now).order_by("sale_price").first()
            if item and item.remaining > 0:
                return item.sale_price
        except Exception:
            pass
        return self.price

    def get_available_stock(self):
        """Get stock available for sale (total - reserved)."""
        return max(0, self.get_total_stock() - self.reserved_stock)

    def reserve_stock(self, quantity):
        """Reserve stock for an order/cart. Returns True if successful."""
        if not self.track_inventory:
            return True
        if self.get_available_stock() >= quantity:
            self.reserved_stock += quantity
            self.save(update_fields=["reserved_stock"])
            return True
        return False

    def release_stock(self, quantity):
        """Release reserved stock (e.g., cart abandoned, order cancelled)."""
        self.reserved_stock = max(0, self.reserved_stock - quantity)
        self.save(update_fields=["reserved_stock"])

    def is_low_stock(self):
        """Check if stock is at or below threshold."""
        return self.get_available_stock() <= self.low_stock_threshold

    def get_cross_sell_products(self, limit=4):
        """Sản phẩm thường được mua cùng (cross-sell) dựa trên lịch sử đơn hàng."""
        from orders.models import OrderItem

        order_ids = (
            OrderItem.objects.filter(product=self)
            .values_list("order_id", flat=True)
            .distinct()
        )

        cross_sell_ids = (
            OrderItem.objects.filter(order_id__in=order_ids)
            .exclude(product=self)
            .values("product_id")
            .annotate(cnt=models.Count("product_id"))
            .order_by("-cnt")[:limit]
        )

        ids = [item["product_id"] for item in cross_sell_ids]
        return Product.objects.filter(id__in=ids, available=True).only(
            "id", "name", "slug", "price", "image", "image_url"
        )

class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product, related_name="variants", on_delete=models.CASCADE
    )
    color_name = models.CharField(max_length=50, verbose_name="Màu sắc", db_index=True)
    color_code = models.CharField(
        max_length=20, default="#111111", verbose_name="Mã màu"
    )
    size = models.CharField(max_length=20, verbose_name="Size", db_index=True)
    stock = models.PositiveIntegerField(
        default=0, verbose_name="Tồn kho", db_index=True
    )
    is_active = models.BooleanField(
        default=True, verbose_name="Hiển thị", db_index=True
    )
    # Shipping dimensions (grams, cm) - dùng cho tính phí GHN/GHTK
    weight = models.PositiveIntegerField(
        default=200, verbose_name="Trọng lượng (gram)", help_text="Trọng lượng một sản phẩm, mặc định 200g"
    )
    length = models.PositiveIntegerField(
        default=30, verbose_name="Dài (cm)", help_text="Chiều dài bao bì"
    )
    width = models.PositiveIntegerField(
        default=20, verbose_name="Rộng (cm)", help_text="Chiều rộng bao bì"
    )
    height = models.PositiveIntegerField(
        default=10, verbose_name="Cao (cm)", help_text="Chiều cao bao bì"
    )

    class Meta:
        ordering = ["color_name", "size"]
        unique_together = ("product", "color_name", "size")
        constraints = [
            models.CheckConstraint(
                condition=Q(stock__gte=0),
                name="productvariant_stock_non_negative",
            ),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.color_name} / {self.size}"


class PriceHistory(models.Model):
    """P3.2: lich su doi gia (ghi tu dong trong Product.save)."""

    product = models.ForeignKey(
        Product, related_name="price_history", on_delete=models.CASCADE
    )
    old_price = models.DecimalField(max_digits=10, decimal_places=0)
    new_price = models.DecimalField(max_digits=10, decimal_places=0)
    changed_at = models.DateTimeField(auto_now_add=True, db_index=True)
    changed_by = models.CharField(max_length=150, blank=True)

    class Meta:
        verbose_name = "Lịch sử giá"
        verbose_name_plural = "Lịch sử giá"
        ordering = ["-changed_at"]

    def __str__(self):
        return f"{self.product.name}: {self.old_price} -> {self.new_price}"


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, related_name="gallery_images", on_delete=models.CASCADE
    )
    image = models.ImageField(
        upload_to="products/gallery/%Y/%m/%d",
        validators=[validate_product_image],
        verbose_name="Ảnh gallery",
    )
    sort_order = models.PositiveSmallIntegerField(
        default=0, verbose_name="Thứ tự", db_index=True
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Ảnh sản phẩm"
        verbose_name_plural = "Ảnh sản phẩm"
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.product.name} - ảnh {self.id}"


class WishlistItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist_items",
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="wishlist_items"
    )
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

    product = models.ForeignKey(
        Product, related_name="reviews", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="reviews", on_delete=models.CASCADE
    )
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES, verbose_name="Số sao", db_index=True
    )
    # ponytail: review media - photo/video upload cho social proof
    media_type = models.CharField(
        max_length=10, choices=[("image", "Ảnh"), ("video", "Video")], blank=True
    )
    media_file = models.FileField(upload_to="reviews/%Y/%m/", blank=True)
    media_thumb = models.ImageField(upload_to="reviews/thumbs/%Y/%m/", blank=True)
    comment = models.TextField(blank=True, verbose_name="Nội dung đánh giá")
    shop_reply = models.TextField(blank=True, verbose_name="Shop phản hồi")
    customer_reply = models.TextField(
        blank=True, verbose_name="Khách hàng phản hồi shop"
    )
    image = models.ImageField(
        upload_to="reviews/%Y/%m/%d",
        blank=True,
        validators=[validate_product_image],
        verbose_name="Ảnh kèm đánh giá",
    )
    is_published = models.BooleanField(
        default=True, verbose_name="Hiển thị", db_index=True
    )
    verified_purchase = models.BooleanField(
        default=False, verbose_name="Đã mua hàng", db_index=True
    )
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
    is_active = models.BooleanField(
        default=True, verbose_name="Đang nhận tin", db_index=True
    )
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
    slug = models.SlugField(
        max_length=220, unique=True, db_index=True, verbose_name="Slug"
    )
    excerpt = models.CharField(max_length=300, blank=True, verbose_name="Mô tả ngắn")
    body = models.TextField(verbose_name="Nội dung")
    cover_image_url = models.URLField(blank=True, verbose_name="URL ảnh bìa")
    is_published = models.BooleanField(
        default=True, verbose_name="Hiển thị", db_index=True
    )
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
    product = models.ForeignKey(
        Product, related_name="questions", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="product_questions",
        on_delete=models.CASCADE,
    )
    question = models.TextField(verbose_name="Câu hỏi")
    answer = models.TextField(blank=True, verbose_name="Trả lời")
    is_published = models.BooleanField(
        default=True, verbose_name="Hiển thị", db_index=True
    )
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


# ponytail: flash sale + bundle toi gian - 2 model, khong tach app moi
class FlashSale(models.Model):
    name = models.CharField(max_length=150)
    starts_at = models.DateTimeField(db_index=True)
    ends_at = models.DateTimeField(db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-starts_at"]

    def __str__(self):
        return self.name

    def is_running(self):
        now = timezone.now()
        return self.is_active and self.starts_at <= now <= self.ends_at


class FlashSaleItem(models.Model):
    sale = models.ForeignKey(FlashSale, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="flash_items", on_delete=models.CASCADE)
    sale_price = models.DecimalField(max_digits=10, decimal_places=0)
    quantity = models.PositiveIntegerField(default=0, verbose_name="SL flash sale")
    sold = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = [("sale", "product")]

    def __str__(self):
        return f"{self.sale.name} - {self.product.name}"

    @property
    def remaining(self):
        return max(0, self.quantity - self.sold)


class Bundle(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    products = models.ManyToManyField(Product, related_name="bundles")
    bundle_price = models.DecimalField(max_digits=12, decimal_places=0)
    is_active = models.BooleanField(default=True, db_index=True)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.name

    def total_compare(self):
        return sum((p.price for p in self.products.all()), 0)


class BackInStock(models.Model):
    product = models.ForeignKey(
        Product, related_name="back_in_stock_requests", on_delete=models.CASCADE
    )
    email = models.EmailField(max_length=254, verbose_name="Email")
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    notified = models.BooleanField(default=False, verbose_name="Đã gửi thông báo")

    class Meta:
        verbose_name = "Báo khi có hàng"
        verbose_name_plural = "Báo khi có hàng"
        ordering = ["-created"]
        constraints = [
            models.UniqueConstraint(
                fields=["product", "email"], name="unique_backinstock_product_email"
            )
        ]

    def __str__(self):
        return f"{self.email} - {self.product.name}"
