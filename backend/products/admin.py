from django.contrib import admin

from .models import Category, Product, ProductVariant, WishlistItem


@admin.register(Category)

# -----------------------------------
# | KHỐI LỚP (CLASS): CATEGORYADMIN |
# -----------------------------------
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)



# ------------------------------------------
# | KHỐI LỚP (CLASS): PRODUCTVARIANTINLINE |
# ------------------------------------------
class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    fields = ("color_name", "color_code", "size", "stock", "is_active")


@admin.register(Product)

# ----------------------------------
# | KHỐI LỚP (CLASS): PRODUCTADMIN |
# ----------------------------------
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock", "available", "featured", "updated")
    list_filter = ("available", "featured", "category", "updated")
    list_editable = ("price", "stock", "available", "featured")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "description")
    inlines = [ProductVariantInline]


@admin.register(ProductVariant)

# -----------------------------------------
# | KHỐI LỚP (CLASS): PRODUCTVARIANTADMIN |
# -----------------------------------------
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("product", "color_name", "size", "stock", "is_active")
    list_filter = ("is_active", "color_name", "size")
    search_fields = ("product__name", "color_name", "size")


@admin.register(WishlistItem)

# ---------------------------------------
# | KHỐI LỚP (CLASS): WISHLISTITEMADMIN |
# ---------------------------------------
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "created")
    list_filter = ("created",)
    search_fields = ("user__username", "product__name")
