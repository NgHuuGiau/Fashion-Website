from django.urls import path

from .admin_product_dashboard import admin_dashboard
from .views import (
    admin_export_orders,
    bank_payment_cancel,
    bank_payment_confirm,
    bank_payment_mobile,
    bank_payment_status,
    bank_payment_waiting,
    cart_add,
    cart_clear_all,
    cart_detail,
    cart_remove,
    cart_update,
    checkout,
    my_orders,
    order_failed,
    order_lookup,
    order_review,
    order_success,
    print_invoice,
    reorder_order,
    user_cancel_order,
)

app_name = "orders"

urlpatterns = [
    path("admin-dashboard/", admin_dashboard, name="admin_dashboard"),
    path("gio-hang/", cart_detail, name="cart_detail"),
    path("gio-hang/them/<int:product_id>/", cart_add, name="cart_add"),
    path("gio-hang/cap-nhat/", cart_update, name="cart_update"),
    path("gio-hang/xoa/", cart_remove, name="cart_remove"),
    path("gio-hang/xoa-tat-ca/", cart_clear_all, name="cart_clear_all"),
    path("thanh-toan/", checkout, name="checkout"),
    path("dat-hang-thanh-cong/<int:order_id>/", order_success, name="order_success"),
    path("cho-thanh-toan-ngan-hang/<int:order_id>/", bank_payment_waiting, name="bank_payment_waiting"),
    path("cho-thanh-toan-ngan-hang/<int:order_id>/trang-thai/", bank_payment_status, name="bank_payment_status"),
    path("dat-hang-chua-thanh-cong/<int:order_id>/", order_failed, name="order_failed"),
    path("don-hang/<int:order_id>/xem-lai/", order_review, name="order_review"),
    path("don-hang/<int:order_id>/xac-nhan-thanh-toan/", bank_payment_confirm, name="bank_payment_confirm"),
    path("don-hang/<int:order_id>/huy-thanh-toan/", bank_payment_cancel, name="bank_payment_cancel"),
    path("qr-thanh-toan/<str:token>/<int:order_id>/", bank_payment_mobile, name="bank_payment_mobile"),
    path("don-hang-cua-toi/", my_orders, name="my_orders"),
    path("tra-cuu-don/", order_lookup, name="order_lookup"),
    path("don-hang/<int:order_id>/huy/", user_cancel_order, name="user_cancel_order"),
    path("don-hang/<int:order_id>/mua-lai/", reorder_order, name="reorder_order"),
    path("admin-dashboard/xuat-don/", admin_export_orders, name="admin_export_orders"),
    path("admin-dashboard/in-hoa-don/<int:order_id>/", print_invoice, name="admin_print_invoice"),
]
