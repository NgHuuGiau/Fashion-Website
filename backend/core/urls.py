from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from django.urls import include, path

from . import api, views
from .sitemaps import ProductSitemap, StaticSitemap

handler404 = views.handler404
handler500 = views.handler500

sitemaps = {
    "static": StaticSitemap,
    "products": ProductSitemap,
}


def robots_txt(request):
    return HttpResponse(
        "User-agent: *\n"
        "Disallow: /gio-hang/\n"
        "Disallow: /thanh-toan/\n"
        "Disallow: /tra-cuu-don/\n"
        "Disallow: /admin-dashboard/\n"
        "Sitemap: https://localhost:8000/sitemap.xml\n",
        content_type="text/plain",
    )


api_urlpatterns = [
    path("", api.api_root, name="api_root"),
    path("products/", api.api_product_list, name="api_product_list"),
    path("products/<int:pk>/", api.api_product_detail, name="api_product_detail"),
    path("products/<int:pk>/reviews/", api.api_product_reviews, name="api_product_reviews"),
    path("products/<int:pk>/reviews/create/", api.api_review_submit, name="api_review_submit"),
    path("categories/", api.api_categories, name="api_categories"),
    path("orders/", api.api_my_orders, name="api_my_orders"),
    path("orders/<int:pk>/", api.api_order_detail, name="api_order_detail"),
    path("orders/lookup/", api.api_order_lookup, name="api_order_lookup"),
    path("coupons/check/", api.api_coupon_check, name="api_coupon_check"),
    path("admin/stats/", api.api_admin_stats, name="api_admin_stats"),
    path("admin/orders/", api.api_admin_orders, name="api_admin_orders"),
    path("admin/orders/<int:pk>/", api.api_admin_order_detail, name="api_admin_order_detail"),
    path("admin/orders/<int:pk>/status/", api.api_admin_order_status, name="api_admin_order_status"),
    path("admin/orders/<int:pk>/refund/", api.api_admin_order_refund, name="api_admin_order_refund"),
    path("admin/orders/<int:pk>/invoice/", api.api_admin_invoice, name="api_admin_invoice"),
    path("admin/export/", api.api_admin_export, name="api_admin_export"),
    path("admin/products/", api.api_admin_products, name="api_admin_products"),
    path("admin/users/", api.api_admin_users, name="api_admin_users"),
    path("admin/coupons/", api.api_admin_coupons, name="api_admin_coupons"),
    path("admin/reviews/", api.api_admin_reviews, name="api_admin_reviews"),
]


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include((api_urlpatterns, "api"), namespace="api")),
    path("", include("products.urls", namespace="products")),
    path("", include("users.urls", namespace="users")),
    path("", include("orders.urls", namespace="orders")),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("robots.txt", robots_txt, name="robots_txt"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
