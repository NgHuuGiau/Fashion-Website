from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from products.models import Product


class StaticSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return ["products:product_list", "orders:order_lookup"]

    def location(self, item):
        return reverse(item)


class ProductSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Product.objects.filter(available=True)

    def lastmod(self, obj):
        return obj.updated
