from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("gio-hang/", views.cart_detail, name="cart_detail"),
    path("gio-hang/them/<int:product_id>/", views.cart_add, name="cart_add"),
    path("gio-hang/cap-nhat/", views.cart_update, name="cart_update"),
    path("gio-hang/xoa/", views.cart_remove, name="cart_remove"),
    path("gio-hang/xoa-tat-ca/", views.cart_clear_all, name="cart_clear_all"),
    path("thanh-toan/", views.checkout, name="checkout"),
    path("dat-hang-thanh-cong/<int:order_id>/", views.order_success, name="order_success"),
    path("cho-thanh-toan-ngan-hang/<int:order_id>/", views.bank_payment_waiting, name="bank_payment_waiting"),
    path("cho-thanh-toan-ngan-hang/<int:order_id>/trang-thai/", views.bank_payment_status, name="bank_payment_status"),
    path("dat-hang-chua-thanh-cong/<int:order_id>/", views.order_failed, name="order_failed"),
    path("don-hang/<int:order_id>/xem-lai/", views.order_review, name="order_review"),
    path("don-hang/<int:order_id>/xac-nhan-thanh-toan/", views.bank_payment_confirm, name="bank_payment_confirm"),
    path("don-hang/<int:order_id>/huy-thanh-toan/", views.bank_payment_cancel, name="bank_payment_cancel"),
    path("don-hang-cua-toi/", views.my_orders, name="my_orders"),
]
