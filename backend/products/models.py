from django.conf import settings
from django.db import models



# ------------------------------
# | KHỐI LỚP (CLASS): CATEGORY |
# ------------------------------
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên danh mục")
    slug = models.SlugField(unique=True)


    # --------------------------
    # | KHỐI LỚP (CLASS): META |
    # --------------------------
    class Meta:
        verbose_name = "Danh mục"
        verbose_name_plural = "Danh mục"
        ordering = ["name"]

    def __str__(self):
        return self.name



# -----------------------------
# | KHỐI LỚP (CLASS): PRODUCT |
# -----------------------------
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


    # --------------------------
    # | KHỐI LỚP (CLASS): META |
    # --------------------------
    class Meta:
        ordering = ("-created",)
        indexes = [
            models.Index(fields=["id", "slug"]),
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name


    # -----------------------------------
    # | HÀM XỬ LÝ (FUNCTION): GET_IMAGE |
    # -----------------------------------
    def get_image(self):
        if self.image:
            return self.image.url
        return self.image_url



# ------------------------------------
# | KHỐI LỚP (CLASS): PRODUCTVARIANT |
# ------------------------------------
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name="variants", on_delete=models.CASCADE)
    color_name = models.CharField(max_length=50, verbose_name="Màu sắc")
    color_code = models.CharField(max_length=20, default="#111111", verbose_name="Mã màu")
    size = models.CharField(max_length=20, verbose_name="Size")
    stock = models.PositiveIntegerField(default=0, verbose_name="Tồn kho")
    is_active = models.BooleanField(default=True, verbose_name="Hiển thị")


    # --------------------------
    # | KHỐI LỚP (CLASS): META |
    # --------------------------
    class Meta:
        ordering = ["color_name", "size"]
        unique_together = ("product", "color_name", "size")

    def __str__(self):
        return f"{self.product.name} - {self.color_name} / {self.size}"



# ----------------------------------
# | KHỐI LỚP (CLASS): WISHLISTITEM |
# ----------------------------------
class WishlistItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlist_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishlist_items")
    created = models.DateTimeField(auto_now_add=True)


    # --------------------------
    # | KHỐI LỚP (CLASS): META |
    # --------------------------
    class Meta:
        verbose_name = "Sản phẩm yêu thích"
        verbose_name_plural = "Sản phẩm yêu thích"
        ordering = ["-created"]
        unique_together = ("user", "product")

    def __str__(self):
        return f"{self.user} - {self.product.name}"
