import os

# ruff: noqa: E402
os.environ["DJANGO_SETTINGS_MODULE"] = "core.settings"
import django

django.setup()

from django.contrib.auth.models import User
from orders.models import Coupon, Order, OrderItem
from products.models import Review
from users.models import UserAddress

output_path = r"C:\Users\HUUGIAU\OneDrive\Documents\GitHub\Fashion-Website\database\sql\02_DEMO_DATA.sql"

TARGET_COUNTS = {
    "orders": 5000,
    "orderitems": 3000,
    "reviews": 1500,
    "addresses": 200,
    "coupons": 30,
    "users": 19,
}

with open(output_path, "w", encoding="utf-8") as f:
    f.write("-- ============================================================\n")
    f.write("-- EXPORT DEMO DATA - Fashion Website\n")
    f.write(
        "-- Target: 5000 orders, 3000 items, 1500 reviews, 200 addresses, 30 coupons, 19 users\n"
    )
    f.write(
        "-- Generated: "
        + __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        + "\n"
    )
    f.write("-- ============================================================\n\n")

    f.write("SET NOCOUNT ON;\n\n")

    # Users (exact 19)
    f.write("-- ============================================================\n")
    f.write("-- 1. USERS (19)\n")
    f.write("-- ============================================================\n")
    for u in User.objects.all().order_by("id")[: TARGET_COUNTS["users"]]:
        last_login = (
            u.last_login.strftime("%Y-%m-%d %H:%M:%S") if u.last_login else "NULL"
        )
        f.write(
            "INSERT INTO auth_user (id, username, email, password, first_name, last_name, is_superuser, is_staff, is_active, date_joined, last_login) VALUES\n"
        )
        f.write(
            "({0}, '{1}', '{2}', '{3}', N'{4}', N'{5}', {6}, {7}, {8}, '{9}', {10});\n\n".format(
                u.id,
                u.username,
                u.email,
                u.password,
                u.first_name.replace("'", "''"),
                u.last_name.replace("'", "''"),
                1 if u.is_superuser else 0,
                1 if u.is_staff else 0,
                1 if u.is_active else 0,
                u.date_joined.strftime("%Y-%m-%d %H:%M:%S"),
                "'" + last_login + "'" if last_login != "NULL" else "NULL",
            )
        )

    # Coupons (exact 30)
    f.write("-- ============================================================\n")
    f.write("-- 2. COUPONS (30)\n")
    f.write("-- ============================================================\n")
    for c in Coupon.objects.all().order_by("id")[: TARGET_COUNTS["coupons"]]:
        ends_at = (
            "'" + c.ends_at.strftime("%Y-%m-%d %H:%M:%S") + "'" if c.ends_at else "NULL"
        )
        max_disc = c.max_discount_amount if c.max_discount_amount else "NULL"
        usage_limit = c.usage_limit if c.usage_limit else "NULL"
        f.write(
            "INSERT INTO orders_coupon (id, code, discount_type, value, is_active, min_order_amount, max_discount_amount, usage_limit, used_count, ends_at, created_at) VALUES\n"
        )
        f.write(
            "({0}, '{1}', '{2}', {3}, {4}, {5}, {6}, {7}, {8}, {9}, '{10}');\n\n".format(
                c.id,
                c.code,
                c.discount_type,
                c.value,
                1 if c.is_active else 0,
                c.min_order_amount,
                max_disc,
                usage_limit,
                c.used_count,
                ends_at,
                c.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            )
        )

    # Orders (exact 5000)
    f.write("-- ============================================================\n")
    f.write("-- 3. ORDERS (5000)\n")
    f.write("-- ============================================================\n")
    print(f"Exporting orders, target: {TARGET_COUNTS['orders']}")
    orders_qs = Order.objects.all().order_by("id")[: TARGET_COUNTS["orders"]]
    print(f"Queryset count: {orders_qs.count()}")
    count = 0
    for o in orders_qs:
        coupon_id = o.coupon_id if o.coupon_id else "NULL"
        coupon_code = "'" + o.coupon_code + "'" if o.coupon_code else "NULL"
        bank_code = "'" + o.bank_code + "'" if o.bank_code else "NULL"
        note = "N'" + o.note.replace("'", "''") + "'" if o.note else "N''"
        f.write(
            "INSERT INTO orders_order (id, user_id, customer_name, customer_email, phone, shipping_address, note, payment_method, bank_code, is_paid, status, subtotal_amount, shipping_fee, discount_amount, coupon_id, coupon_code, total_amount, created_at) VALUES\n"
        )
        f.write(
            "({0}, {1}, N'{2}', '{3}', '{4}', N'{5}', {6}, '{7}', {8}, {9}, '{10}', {11}, {12}, {13}, {14}, {15}, {16}, '{17}');\n\n".format(
                o.id,
                o.user_id,
                o.customer_name.replace("'", "''"),
                o.customer_email,
                o.phone,
                o.shipping_address.replace("'", "''"),
                note,
                o.payment_method,
                bank_code,
                1 if o.is_paid else 0,
                o.status,
                o.subtotal_amount,
                o.shipping_fee,
                o.discount_amount,
                coupon_id,
                coupon_code,
                o.total_amount,
                o.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            )
        )
        count += 1
    print(f"Exported {count} orders")

    # OrderItems (exact 3000)
    f.write("-- ============================================================\n")
    f.write("-- 4. ORDER ITEMS (3000)\n")
    f.write("-- ============================================================\n")
    count = 0
    for oi in OrderItem.objects.all().order_by("id")[: TARGET_COUNTS["orderitems"]]:
        variant_id = oi.variant_id if oi.variant_id else "NULL"
        color = "'" + oi.selected_color + "'" if oi.selected_color else "N''"
        size = "'" + oi.selected_size + "'" if oi.selected_size else "N''"
        f.write(
            "INSERT INTO orders_orderitem (id, order_id, product_id, variant_id, selected_color, selected_size, quantity, price) VALUES\n"
        )
        f.write(
            "({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7});\n\n".format(
                oi.id,
                oi.order_id,
                oi.product_id,
                variant_id,
                color,
                size,
                oi.quantity,
                oi.price,
            )
        )
        count += 1
    print(f"Exported {count} order items")

    # Reviews (exact 1500)
    f.write("-- ============================================================\n")
    f.write("-- 5. REVIEWS (1500)\n")
    f.write("-- ============================================================\n")
    count = 0
    for r in Review.objects.all().order_by("id")[: TARGET_COUNTS["reviews"]]:
        comment = "N'" + r.comment.replace("'", "''") + "'" if r.comment else "N''"
        f.write(
            "INSERT INTO products_review (id, product_id, user_id, rating, comment, is_published, verified_purchase, created) VALUES\n"
        )
        f.write(
            "({0}, {1}, {2}, {3}, {4}, {5}, {6}, '{7}');\n\n".format(
                r.id,
                r.product_id,
                r.user_id,
                r.rating,
                comment,
                1 if r.is_published else 0,
                1 if r.verified_purchase else 0,
                r.created.strftime("%Y-%m-%d %H:%M:%S"),
            )
        )
        count += 1
    print(f"Exported {count} reviews")

    # Addresses (exact 200)
    f.write("-- ============================================================\n")
    f.write("-- 6. ADDRESSES (200)\n")
    f.write("-- ============================================================\n")
    count = 0
    for a in UserAddress.objects.all().order_by("id")[: TARGET_COUNTS["addresses"]]:
        addr = a.address.replace("'", "''")
        f.write(
            "INSERT INTO users_useraddress (id, user_id, label, recipient_name, phone, address, is_default) VALUES\n"
        )
        f.write(
            "({0}, {1}, N'{2}', N'{3}', '{4}', N'{5}', {6});\n\n".format(
                a.id,
                a.user_id,
                a.label.replace("'", "''"),
                a.recipient_name.replace("'", "''"),
                a.phone,
                addr,
                1 if a.is_default else 0,
            )
        )
        count += 1
    print(f"Exported {count} addresses")

print("Done! Written to 02_DEMO_DATA.sql")
