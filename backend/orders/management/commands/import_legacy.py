from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import connection

from orders.models import Coupon, Order, OrderItem
from products.models import Category, Product, ProductVariant, SupportFAQ, WishlistItem
from users.models import UserActivity, UserProfile


def _dictfetchall(cursor):
    cols = [col[0] for col in cursor.description]
    return [dict(zip(cols, row)) for row in cursor.fetchall()]


def _null(val):
    return None if val == "" else val


class Command(BaseCommand):
    help = "Import data from legacy SQL tables (Users, Categories, Products, ...) into Django ORM tables."

    def handle(self, *args, **options):
        self.stdout.write("Importing legacy data...")

        self._import_categories()
        self._import_products()
        self._import_variants()
        self._import_users()
        self._import_coupons()
        self._import_orders()
        self._import_order_items()
        self._import_wishlists()
        self._import_faqs()
        self._import_activities()

        self.stdout.write(self.style.SUCCESS("Done!"))

    def _table_exists(self, table_name):
        tables = [t.lower() for t in connection.introspection.table_names()]
        return table_name.lower() in tables

    def _fetch(self, sql):
        with connection.cursor() as cur:
            cur.execute(sql)
            return _dictfetchall(cur)

    def _import_categories(self):
        if not self._table_exists("Categories"):
            self.stdout.write("  [bỏ qua] Không tìm thấy bảng legacy Categories")
            return
        for row in self._fetch("SELECT id, name, slug FROM [Categories]"):
            Category.objects.get_or_create(id=row["id"], defaults={"name": row["name"], "slug": row["slug"]})
        self.stdout.write(f"  -> {Category.objects.count()} categories")

    def _import_products(self):
        if not self._table_exists("Products"):
            self.stdout.write("  [bỏ qua] Không tìm thấy bảng legacy Products")
            return
        for row in self._fetch("SELECT * FROM [Products]"):
            Product.objects.get_or_create(
                id=row["id"],
                defaults={
                    "category_id": row["category_id"],
                    "name": row["name"],
                    "slug": row["slug"],
                    "price": row["price"],
                    "stock": row["stock"],
                    "available": row["available"],
                    "featured": row["featured"],
                    "image_url": row["image_url"] or "",
                    "created": row["created"],
                },
            )
        self.stdout.write(f"  -> {Product.objects.count()} products")

    def _import_variants(self):
        if not self._table_exists("Variants"):
            self.stdout.write("  [bỏ qua] Không tìm thấy bảng legacy Variants")
            return
        for row in self._fetch("SELECT * FROM [Variants]"):
            ProductVariant.objects.get_or_create(
                id=row["id"],
                defaults={
                    "product_id": row["product_id"],
                    "color_name": row["color_name"],
                    "color_code": row["color_code"],
                    "size": row["size"],
                    "stock": row["stock"],
                    "is_active": row["is_active"],
                },
            )
        self.stdout.write(f"  -> {ProductVariant.objects.count()} variants")

    def _import_users(self):
        if not self._table_exists("Users"):
            self.stdout.write("  [bỏ qua] Không tìm thấy bảng legacy Users")
            return
        for row in self._fetch("SELECT * FROM [Users]"):
            role = row["role"]
            is_super = role == 0
            is_staff = role in (0, 1)
            user, created = User.objects.get_or_create(
                id=row["id"],
                defaults={
                    "username": row["username"],
                    "email": row["email"],
                    "password": row["password"],
                    "is_superuser": is_super,
                    "is_staff": is_staff,
                    "is_active": row["is_active"],
                    "date_joined": row["date_joined"],
                },
            )
            if created:
                UserProfile.objects.get_or_create(user=user, defaults={"phone_number": row["phone"] or ""})
        self.stdout.write(f"  -> {User.objects.count()} users, {UserProfile.objects.count()} profiles")

    def _import_coupons(self):
        if not self._table_exists("Coupons"):
            self.stdout.write("  [bỏ qua] Không tìm thấy bảng legacy Coupons")
            return
        for row in self._fetch("""
            SELECT id, code, type AS discount_type, value, is_active,
                   min_amount AS min_order_amount, max_amount AS max_discount_amount,
                   max_uses AS usage_limit, used_count
            FROM [Coupons]
        """):
            Coupon.objects.get_or_create(
                id=row["id"],
                defaults={
                    "code": row["code"],
                    "discount_type": row["discount_type"],
                    "value": row["value"],
                    "is_active": row["is_active"],
                    "min_order_amount": row["min_order_amount"],
                    "max_discount_amount": _null(row["max_discount_amount"]),
                    "usage_limit": _null(row["usage_limit"]),
                    "used_count": row["used_count"],
                },
            )
        self.stdout.write(f"  -> {Coupon.objects.count()} coupons")

    def _import_orders(self):
        if not self._table_exists("Orders"):
            self.stdout.write("  [bỏ qua] Không tìm thấy bảng legacy Orders")
            return
        for row in self._fetch("SELECT * FROM [Orders]"):
            coupon_code = row["coupon"] or ""
            coupon = None
            if coupon_code:
                coupon = Coupon.objects.filter(code=coupon_code).first()
            Order.objects.get_or_create(
                id=row["id"],
                defaults={
                    "user_id": row["user_id"] or 1,
                    "customer_name": row["customer_name"],
                    "phone": row["phone"],
                    "shipping_address": row["shipping_address"],
                    "status": row["status"],
                    "total_amount": row["total_amount"],
                    "is_paid": row["is_paid"],
                    "payment_method": row["payment_method"],
                    "discount_amount": row["discount_amount"],
                    "coupon": coupon,
                    "coupon_code": coupon_code,
                    "created_at": row["created_at"],
                },
            )
        self.stdout.write(f"  -> {Order.objects.count()} orders")

    def _import_order_items(self):
        if not self._table_exists("OrderItems"):
            self.stdout.write("  [bỏ qua] Không tìm thấy bảng legacy OrderItems")
            return
        for row in self._fetch("SELECT id, order_id, product_id, variant_id, color AS selected_color, size AS selected_size, quantity, price FROM [OrderItems]"):
            OrderItem.objects.get_or_create(
                id=row["id"],
                defaults={
                    "order_id": row["order_id"],
                    "product_id": row["product_id"],
                    "variant_id": _null(row["variant_id"]),
                    "selected_color": row["selected_color"],
                    "selected_size": row["selected_size"],
                    "quantity": row["quantity"],
                    "price": row["price"],
                },
            )
        self.stdout.write(f"  -> {OrderItem.objects.count()} order items")

    def _import_wishlists(self):
        if not self._table_exists("Wishlist"):
            self.stdout.write("  [bỏ qua] Không tìm thấy bảng legacy Wishlist")
            return
        for row in self._fetch("SELECT * FROM [Wishlist]"):
            WishlistItem.objects.get_or_create(
                id=row["id"],
                defaults={
                    "user_id": row["user_id"],
                    "product_id": row["product_id"],
                    "created": row["created"],
                },
            )
        self.stdout.write(f"  -> {WishlistItem.objects.count()} wishlist items")

    def _import_faqs(self):
        if not self._table_exists("FAQs"):
            self.stdout.write("  [bỏ qua] Không tìm thấy bảng legacy FAQs")
            return
        for row in self._fetch("SELECT * FROM [FAQs]"):
            SupportFAQ.objects.get_or_create(
                id=row["id"],
                defaults={
                    "question": row["question"],
                    "answer": row["answer"],
                    "priority": row["priority"],
                    "is_active": row["is_active"],
                },
            )
        self.stdout.write(f"  -> {SupportFAQ.objects.count()} FAQs")

    def _import_activities(self):
        if not self._table_exists("Activities"):
            self.stdout.write("  [bỏ qua] Không tìm thấy bảng legacy Activities")
            return
        for row in self._fetch("SELECT id, user_id, event AS event_type, path, created_at FROM [Activities]"):
            UserActivity.objects.get_or_create(
                id=row["id"],
                defaults={
                    "user_id": row["user_id"],
                    "event_type": row["event_type"],
                    "path": row["path"],
                    "created_at": row["created_at"],
                },
            )
        self.stdout.write(f"  -> {UserActivity.objects.count()} activities")
