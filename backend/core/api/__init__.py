"""API JSON (tach tu core/api.py monolith). Logic giu nguyen."""

from .admin import (
    api_admin_stats,
    api_admin_orders,
    api_admin_order_detail,
    api_admin_order_status,
    api_admin_order_refund,
    api_admin_invoice,
    api_admin_export,
    api_admin_products,
    api_admin_users,
    api_admin_coupons,
    api_admin_reviews,
)
from .misc import (
    api_geocode,
    api_root,
    api_gdpr_export,
    api_gdpr_delete,
    api_gdpr_guest_export,
    api_schema_file,
)
from .orders import (
    api_my_orders,
    api_order_detail,
    api_order_lookup,
    api_coupon_check,
)
from .products import (
    api_product_list,
    api_product_detail,
    api_product_reviews,
    api_review_submit,
    api_categories,
)

__all__ = [
    "api_admin_stats",
    "api_admin_orders",
    "api_admin_order_detail",
    "api_admin_order_status",
    "api_admin_order_refund",
    "api_admin_invoice",
    "api_admin_export",
    "api_admin_products",
    "api_admin_users",
    "api_admin_coupons",
    "api_admin_reviews",
    "api_geocode",
    "api_root",
    "api_gdpr_export",
    "api_gdpr_delete",
    "api_gdpr_guest_export",
    "api_schema_file",
    "api_my_orders",
    "api_order_detail",
    "api_order_lookup",
    "api_coupon_check",
    "api_product_list",
    "api_product_detail",
    "api_product_reviews",
    "api_review_submit",
    "api_categories",
]
