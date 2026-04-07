from django.urls import path

from . import views

app_name = "products"

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("san-pham/<int:pk>/<slug:slug>/", views.product_detail, name="product_detail"),
    path("yeu-thich/", views.wishlist_list, name="wishlist_list"),
    path("yeu-thich/<int:product_id>/toggle/", views.wishlist_toggle, name="wishlist_toggle"),
]
