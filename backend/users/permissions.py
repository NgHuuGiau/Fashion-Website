"""Phân quyền truy cập bảng điều khiển quản trị.

Quy ước vai trò:
  - admin  (is_superuser): toàn quyền, quản lý tài khoản và phân quyền.
  - staff  (is_staff): quản lý đơn hàng, kho hàng và sản phẩm.
  - user   (tài khoản thường): không vào được khu vực quản trị.
"""

ROLE_ADMIN = "admin"
ROLE_STAFF = "staff"
ROLE_USER = "user"


def role_of(user):
    if user.is_superuser:
        return ROLE_ADMIN
    if user.is_staff:
        return ROLE_STAFF
    return ROLE_USER


def is_admin(user):
    return bool(user and user.is_authenticated and user.is_superuser)


def is_staff_member(user):
    return bool(user and user.is_authenticated and (user.is_staff or user.is_superuser))


def can_manage_orders(user):
    return is_staff_member(user)


def can_manage_inventory(user):
    return is_staff_member(user)


def can_manage_products(user):
    return is_staff_member(user)


def can_delete_product(user):
    return is_admin(user)


def can_manage_coupons(user):
    return is_admin(user)


def can_manage_users(user):
    return is_admin(user)