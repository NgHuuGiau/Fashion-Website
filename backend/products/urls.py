from django.urls import path

from . import views

app_name = "products"

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("ho-tro/chat/", views.support_chat_reply, name="support_chat_reply"),
    path("san-pham/<int:pk>/<slug:slug>/", views.product_detail, name="product_detail"),
    path("yeu-thich/", views.wishlist_list, name="wishlist_list"),
    path(
        "yeu-thich/<int:product_id>/toggle/",
        views.wishlist_toggle,
        name="wishlist_toggle",
    ),
    path("danh-gia/<int:product_id>/", views.review_submit, name="review_submit"),
    path(
        "danh-gia/<int:product_id>/phan-hoi/",
        views.review_customer_reply,
        name="review_customer_reply",
    ),
    path("hoi-dap/<int:product_id>/", views.question_submit, name="question_submit"),
    path(
        "bao-khi-co-hang/<int:product_id>/",
        views.back_in_stock_submit,
        name="back_in_stock_submit",
    ),
    path("nhan-tin/dang-ky/", views.newsletter_subscribe, name="newsletter_subscribe"),
    path("lookbook/", views.blog_list, name="blog_list"),
    path("lookbook/<slug:slug>/", views.blog_detail, name="blog_detail"),
    path("tim-kiem/goi-y/", views.search_suggest, name="search_suggest"),
]
