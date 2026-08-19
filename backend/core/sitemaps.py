from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from products.models import Product, Category, BlogPost


class StaticSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return [
            "products:product_list",
            "products:blog_list",
            "products:wishlist_list",
            "orders:cart_detail",
            "users:login",
            "users:register",
        ]

    def location(self, item):
        return reverse(item)


class ProductSitemap(Sitemap):
    priority = 0.9
    changefreq = "daily"

    def items(self):
        return Product.objects.filter(available=True).only("id", "slug", "updated")

    def lastmod(self, obj):
        return obj.updated or obj.created


class CategorySitemap(Sitemap):
    priority = 0.7
    changefreq = "weekly"

    def items(self):
        return Category.objects.all().only("id", "slug")


class BlogSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return BlogPost.objects.filter(is_published=True).only("id", "slug", "updated")

    def lastmod(self, obj):
        return obj.updated or obj.created