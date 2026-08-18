from django.conf import settings
from django.contrib import admin
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse

from .models import (
    BackInStock,
    BlogPost,
    Category,
    NewsletterSubscriber,
    Product,
    ProductQuestion,
    ProductVariant,
    Review,
    SupportFAQ,
    WishlistItem,
)


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


@admin.register(BlogPost)

class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "is_published", "created", "updated")
    list_filter = ("is_published", "created")
    list_editable = ("is_published",)
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "excerpt", "body")


@admin.register(NewsletterSubscriber)

class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "created")
    list_filter = ("is_active", "created")
    list_editable = ("is_active",)
    search_fields = ("email",)


@admin.register(ProductQuestion)

class ProductQuestionAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "question", "is_published", "answered_at", "created")
    list_filter = ("is_published", "created")
    list_editable = ("is_published",)
    search_fields = ("question", "answer", "product__name", "user__username")
    raw_id_fields = ("product", "user")
    fieldsets = (
        (None, {"fields": ("product", "user", "question", "is_published")}),
        ("Trả lời", {"fields": ("answer", "answered_at")}),
    )
    readonly_fields = ("answered_at",)


@admin.register(BackInStock)

class BackInStockAdmin(admin.ModelAdmin):
    list_display = ("product", "email", "notified", "created")
    list_filter = ("notified", "created")
    list_editable = ("notified",)
    search_fields = ("email", "product__name")
    raw_id_fields = ("product",)
    actions = ("notify_restocked",)

    @admin.action(description="Gửi email báo có hàng (chỉ sản phẩm đã nhập kho)")
    def notify_restocked(self, request, queryset):
        sent = 0
        for sub in queryset.select_related("product").filter(notified=False):
            if sub.product.stock <= 0 or not settings.EMAIL_HOST:
                continue
            url = request.build_absolute_uri(
                reverse("products:product_detail", kwargs={"pk": sub.product.id, "slug": sub.product.slug})
            )
            html = render_to_string("emails/back_in_stock.html", {"product": sub.product, "product_url": url})
            msg = EmailMultiAlternatives(
                subject=f"Hàng đã về — {sub.product.name} — HUUGIAU Studio",
                body=f"Hàng đã về: {sub.product.name}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[sub.email],
            )
            msg.attach_alternative(html, "text/html")
            msg.send(fail_silently=True)
            sub.notified = True
            sub.save(update_fields=["notified"])
            sent += 1
        self.message_user(request, f"Đã gửi {sent} email thông báo.")
