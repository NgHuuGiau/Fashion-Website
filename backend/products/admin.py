from django.contrib import admin

from .models import Category, Product, ProductVariant, Review, SupportFAQ, WishlistItem


@admin.register(Category)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)



class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    fields = ("color_name", "color_code", "size", "stock", "is_active")


@admin.register(Product)

class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock", "available", "featured", "updated")
    list_filter = ("available", "featured", "category", "updated")
    list_editable = ("price", "stock", "available", "featured")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "description")
    inlines = [ProductVariantInline]


@admin.register(ProductVariant)

class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("product", "color_name", "size", "stock", "is_active")
    list_filter = ("is_active", "color_name", "size")
    search_fields = ("product__name", "color_name", "size")


@admin.register(WishlistItem)

class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "created")
    list_filter = ("created",)
    search_fields = ("user__username", "product__name")


@admin.register(SupportFAQ)

class SupportFAQAdmin(admin.ModelAdmin):
    list_display = ("question", "priority", "is_active", "updated")
    list_filter = ("is_active",)
    list_editable = ("priority", "is_active")
    search_fields = ("question", "keywords", "answer")


@admin.register(Review)

class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "verified_purchase", "is_published", "created")
    list_filter = ("rating", "is_published", "verified_purchase", "created")
    list_editable = ("is_published", "rating")
    search_fields = ("product__name", "user__username", "comment")
    raw_id_fields = ("product", "user")
