from django.urls import path

from .admin_product_dashboard import admin_dashboard
from .views import (
    admin_export_orders,
    admin_export_revenue,
    bank_payment_cancel,
    bank_payment_confirm,
    bank_payment_mobile,
    bank_payment_status,
    bank_payment_waiting,
    cart_add,
    cart_clear_all,
    cart_detail,
    cart_remove,
    cart_summary,
    cart_update,
    checkout,
    create_return_request,
    my_orders,
    order_failed,
    order_lookup,
    order_review,
    order_success,
    print_invoice,
    promo_page,
    reorder_order,
    user_cancel_order,
    vnpay_ipn,
    vnpay_payment,
    vnpay_refund,
    vnpay_return,
    wallet_ipn,
    wallet_payment,
    wallet_return,
)
from .services.shipping.webhooks import ghn_webhook

app_name = "orders"

urlpatterns = [
    path("admin-dashboard/", admin_dashboard, name="admin_dashboard"),
    path("gio-hang/", cart_detail, name="cart_detail"),
    path("gio-hang/tom-tat/", cart_summary, name="cart_summary"),
    path("gio-hang/them/<int:product_id>/", cart_add, name="cart_add"),
    path("gio-hang/cap-nhat/", cart_update, name="cart_update"),
    path("gio-hang/xoa/", cart_remove, name="cart_remove"),
    path("gio-hang/xoa-tat-ca/", cart_clear_all, name="cart_clear_all"),
    path("thanh-toan/", checkout, name="checkout"),
    path("dat-hang-thanh-cong/<int:order_id>/", order_success, name="order_success"),
    path(
        "cho-thanh-toan-ngan-hang/<int:order_id>/",
        bank_payment_waiting,
        name="bank_payment_waiting",
    ),
    path(
        "cho-thanh-toan-ngan-hang/<int:order_id>/trang-thai/",
        bank_payment_status,
        name="bank_payment_status",
    ),
    path("dat-hang-chua-thanh-cong/<int:order_id>/", order_failed, name="order_failed"),
    path("don-hang/<int:order_id>/xem-lai/", order_review, name="order_review"),
    path(
        "don-hang/<int:order_id>/doi-tra/", create_return_request, name="create_return"
    ),
    path(
        "don-hang/<int:order_id>/xac-nhan-thanh-toan/",
        bank_payment_confirm,
        name="bank_payment_confirm",
    ),
    path(
        "don-hang/<int:order_id>/huy-thanh-toan/",
        bank_payment_cancel,
        name="bank_payment_cancel",
    ),
    path(
        "qr-thanh-toan/<str:token>/<int:order_id>/",
        bank_payment_mobile,
        name="bank_payment_mobile",
    ),
    path("thanh-toan-vnpay/<int:order_id>/", vnpay_payment, name="vnpay_payment"),
    path("thanh-toan-vnpay/callback/", vnpay_return, name="vnpay_return"),
    path("thanh-toan-vnpay/ipn/", vnpay_ipn, name="vnpay_ipn"),
    path("thanh-toan-vnpay/hoan-tien/", vnpay_refund, name="vnpay_refund"),
    # ponytail: 3 vi dung chung view, method truyen qua kwargs de khoi lap 9 ham
    path(
        "thanh-toan-vi/<str:method>/<int:order_id>/",
        wallet_payment,
        name="wallet_payment",
    ),
    path("thanh-toan-vi/<str:method>/callback/", wallet_return, name="wallet_return"),
    path("thanh-toan-vi/<str:method>/ipn/", wallet_ipn, name="wallet_ipn"),
    path(
        "thanh-toan-momo/<int:order_id>/",
        wallet_payment,
        {"method": "momo"},
        name="momo_payment",
    ),
    path(
        "thanh-toan-momo/callback/",
        wallet_return,
        {"method": "momo"},
        name="momo_return",
    ),
    path("thanh-toan-momo/ipn/", wallet_ipn, {"method": "momo"}, name="momo_ipn"),
    path(
        "thanh-toan-zalopay/<int:order_id>/",
        wallet_payment,
        {"method": "zalopay"},
        name="zalopay_payment",
    ),
    path(
        "thanh-toan-zalopay/callback/",
        wallet_return,
        {"method": "zalopay"},
        name="zalopay_return",
    ),
    path(
        "thanh-toan-zalopay/ipn/", wallet_ipn, {"method": "zalopay"}, name="zalopay_ipn"
    ),
    path(
        "thanh-toan-shopeepay/<int:order_id>/",
        wallet_payment,
        {"method": "shopeepay"},
        name="shopeepay_payment",
    ),
    path(
        "thanh-toan-shopeepay/callback/",
        wallet_return,
        {"method": "shopeepay"},
        name="shopeepay_return",
    ),
    path(
        "thanh-toan-shopeepay/ipn/",
        wallet_ipn,
        {"method": "shopeepay"},
        name="shopeepay_ipn",
    ),
    path("don-hang-cua-toi/", my_orders, name="my_orders"),
    path("tra-cuu-don/", order_lookup, name="order_lookup"),
    path("khuyen-mai/", promo_page, name="promo_page"),
    path("don-hang/<int:order_id>/huy/", user_cancel_order, name="user_cancel_order"),
    path("don-hang/<int:order_id>/mua-lai/", reorder_order, name="reorder_order"),
    path("admin-dashboard/xuat-don/", admin_export_orders, name="admin_export_orders"),
    path(
        "admin-dashboard/xuat-doanh-thu/",
        admin_export_revenue,
        name="admin_export_revenue",
    ),
    path(
        "admin-dashboard/in-hoa-don/<int:order_id>/",
        print_invoice,
        name="admin_print_invoice",
    ),
    path("webhook/ghn/", ghn_webhook, name="ghn_webhook"),
]
