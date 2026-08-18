from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from products.models import BlogPost, Product


class StaticSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return [
            "products:product_list",
            "products:blog_list",
            "orders:order_lookup",
            "about",
            "size_guide",
            "return_policy",
            "care_guide",
            "careers",
            "privacy",
            "terms",
            "contact",
        ]

    def location(self, item):
        return reverse(item)


class BlogSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return BlogPost.objects.filter(is_published=True)

    def location(self, item):
        return reverse("products:blog_detail", kwargs={"slug": item.slug})

    def lastmod(self, obj):
        return obj.updated


class ProductSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Product.objects.filter(available=True)

    def lastmod(self, obj):
        return obj.updated
