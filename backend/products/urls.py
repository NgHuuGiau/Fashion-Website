from django.urls import path

from . import views

app_name = "products"

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("ho-tro/chat/", views.support_chat_reply, name="support_chat_reply"),
    path("san-pham/<int:pk>/<slug:slug>/", views.product_detail, name="product_detail"),
    path("yeu-thich/", views.wishlist_list, name="wishlist_list"),
    path("yeu-thich/<int:product_id>/toggle/", views.wishlist_toggle, name="wishlist_toggle"),
    path("tim-kiem/goi-y/", views.search_suggest, name="search_suggest"),
]
