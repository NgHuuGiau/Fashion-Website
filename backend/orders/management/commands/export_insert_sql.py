"""
Management command: export_insert_sql
Export toàn bộ dữ liệu hiện tại ra file 02_INSERT_DATA.sql (format SSMS).
"""

import os
from datetime import datetime
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from orders.models import Coupon, Order, OrderItem
from products.models import Category, Product, ProductVariant, SupportFAQ
from users.models import UserActivity


class Command(BaseCommand):
    help = "Export toàn bộ dữ liệu DB ra file 02_INSERT_DATA.sql (format SSMS)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            default="database/sql/02_INSERT_DATA.sql",
            help="Đường dẫn file output (relative to BASE_DIR)",
        )

    def handle(self, *args, **options):
        output_path = options["output"]
        if not os.path.isabs(output_path):
            from django.conf import settings

            output_path = os.path.join(settings.BASE_DIR, output_path)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(self._header())
            f.write(self._export_users())
            f.write(self._export_categories())
            f.write(self._export_products())
            f.write(self._export_variants())
            f.write(self._export_coupons())
            f.write(self._export_orders())
            f.write(self._export_order_items())
            f.write(self._export_wishlist())
            f.write(self._export_faqs())
            f.write(self._export_activities())
            f.write(
                "\n-- ============================================================\n"
            )
            f.write("-- END OF DATA\n")
            f.write("-- ============================================================\n")

        self.stdout.write(self.style.SUCCESS(f"Đã xuất ra: {output_path}"))

    def _header(self):
        return (
            "-- ============================================================\n"
            "-- HUUGIAU Fashion - INSERT DATA (auto-generated)\n"
            f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            "-- Run in SSMS after 01_CREATE_TABLES.sql\n"
            "-- ============================================================\n\n"
            "USE [HUUGIAU_Fashion];\n"
            "GO\n\n"
        )

    def _quote(self, val):
        if val is None:
            return "NULL"
        if isinstance(val, (int, float, Decimal)):
            return str(val)
        if isinstance(val, bool):
            return "1" if val else "0"
        if isinstance(val, datetime):
            return f"N'{val.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}'"
        escaped = str(val).replace("'", "''")
        return f"N'{escaped}'"

    def _export_users(self):
        users = User.objects.all().order_by("id")
        lines = []
        lines.append("-- Tài khoản người dùng")
        lines.append("SET IDENTITY_INSERT [Users] ON;")
        lines.append("GO")
        if users:
            cols = "[id], [username], [email], [password], [role], [is_active], [date_joined], [phone]"
            lines.append(f"INSERT INTO [Users] ({cols}) VALUES")
            vals = []
            for u in users:
                role = 0 if u.is_superuser else (1 if u.is_staff else 2)
                phone = getattr(u, "phone", "") or ""
                # KHÔNG xuất password hash thật vào SQL (từng lộ trong git).
                # '!' = marker "unusable password" của Django: giữ nguyên số cột
                # để SQL chạy được, nhưng không ai đăng nhập được bằng hash cũ.
                vals.append(
                    f"({u.id}, {self._quote(u.username)}, {self._quote(u.email)}, "
                    f"N'!', {role}, {1 if u.is_active else 0}, "
                    f"{self._quote(u.date_joined)}, {self._quote(phone)})"
                )
            lines.append(",\n".join(vals) + ";")
        lines.append("GO")
        lines.append("SET IDENTITY_INSERT [Users] OFF;")
        lines.append("GO")
        lines.append("")
        return "\n".join(lines) + "\n"

    def _export_categories(self):
        cats = Category.objects.all().order_by("id")
        lines = ["-- Danh mục sản phẩm", "SET IDENTITY_INSERT [Categories] ON;", "GO"]
        if cats:
            lines.append("INSERT INTO [Categories] ([id], [name], [slug]) VALUES")
            vals = [
                f"({c.id}, {self._quote(c.name)}, {self._quote(c.slug)})" for c in cats
            ]
            lines.append(",\n".join(vals) + ";")
        lines.append("GO")
        lines.append("SET IDENTITY_INSERT [Categories] OFF;")
        lines.append("GO")
        lines.append("")
        return "\n".join(lines) + "\n"

    def _export_products(self):
        products = Product.objects.select_related("category").order_by("id")
        lines = ["-- Sản phẩm", "SET IDENTITY_INSERT [Products] ON;", "GO"]
        if products:
            cols = "[id], [name], [slug], [category_id], [price], [stock], [available], [featured], [image_url], [created]"
            lines.append(f"INSERT INTO [Products] ({cols}) VALUES")
            vals = []
            for p in products:
                vals.append(
                    f"({p.id}, {self._quote(p.name)}, {self._quote(p.slug)}, {p.category_id}, "
                    f"{p.price}, {p.stock}, {1 if p.available else 0}, {1 if p.featured else 0}, "
                    f"{self._quote(p.image_url or '')}, {self._quote(p.created)})"
                )
            for i in range(0, len(vals), 50):
                batch = vals[i : i + 50]
                if i > 0:
                    lines.append("GO")
                    lines.append(f"INSERT INTO [Products] ({cols}) VALUES")
                lines.append(",\n".join(batch) + ";")
        lines.append("GO")
        lines.append("SET IDENTITY_INSERT [Products] OFF;")
        lines.append("GO")
        lines.append("")
        return "\n".join(lines) + "\n"

    def _export_variants(self):
        variants = ProductVariant.objects.select_related("product").order_by("id")
        lines = [
            "-- Biến thể sản phẩm (màu sắc, kích cỡ)",
            "SET IDENTITY_INSERT [Variants] ON;",
            "GO",
        ]
        if variants:
            cols = "[id], [product_id], [color_name], [color_code], [size], [stock], [is_active]"
            lines.append(f"INSERT INTO [Variants] ({cols}) VALUES")
            vals = []
            for v in variants:
                vals.append(
                    f"({v.id}, {v.product_id}, {self._quote(v.color_name)}, {self._quote(v.color_code)}, "
                    f"{self._quote(v.size)}, {v.stock}, {1 if v.is_active else 0})"
                )
            for i in range(0, len(vals), 50):
                batch = vals[i : i + 50]
                if i > 0:
                    lines.append("GO")
                    lines.append(f"INSERT INTO [Variants] ({cols}) VALUES")
                lines.append(",\n".join(batch) + ";")
        lines.append("GO")
        lines.append("SET IDENTITY_INSERT [Variants] OFF;")
        lines.append("GO")
        lines.append("")
        return "\n".join(lines) + "\n"

    def _export_coupons(self):
        coupons = Coupon.objects.all().order_by("id")
        lines = ["-- Mã giảm giá", "SET IDENTITY_INSERT [Coupons] ON;", "GO"]
        if coupons:
            cols = "[id], [code], [type], [value], [is_active], [min_amount], [max_amount], [max_uses], [used_count]"
            lines.append(f"INSERT INTO [Coupons] ({cols}) VALUES")
            vals = []
            for c in coupons:
                vals.append(
                    f"({c.id}, {self._quote(c.code)}, {self._quote(c.discount_type)}, {c.value}, "
                    f"{1 if c.is_active else 0}, {c.min_order_amount}, "
                    f"{c.max_discount_amount if c.max_discount_amount is not None else 'NULL'}, "
                    f"{c.usage_limit if c.usage_limit is not None else 'NULL'}, {c.used_count})"
                )
            lines.append(",\n".join(vals) + ";")
        lines.append("GO")
        lines.append("SET IDENTITY_INSERT [Coupons] OFF;")
        lines.append("GO")
        lines.append("")
        return "\n".join(lines) + "\n"

    def _export_orders(self):
        orders = Order.objects.select_related("user", "coupon").order_by("id")
        lines = ["-- Đơn hàng", "SET IDENTITY_INSERT [Orders] ON;", "GO"]
        if orders:
            cols = "[id], [user_id], [customer_name], [phone], [shipping_address], [status], [total_amount], [is_paid], [payment_method], [discount_amount], [coupon], [created_at]"
            lines.append(f"INSERT INTO [Orders] ({cols}) VALUES")
            vals = []
            for o in orders:
                coupon_code = o.coupon.code if o.coupon else ""
                vals.append(
                    f"({o.id}, {o.user_id}, {self._quote(o.customer_name)}, {self._quote(o.phone)}, "
                    f"{self._quote(o.shipping_address)}, {self._quote(o.status)}, {o.total_amount}, "
                    f"{1 if o.is_paid else 0}, {self._quote(o.payment_method)}, {o.discount_amount}, "
                    f"{self._quote(coupon_code)}, {self._quote(o.created_at)})"
                )
            for i in range(0, len(vals), 50):
                batch = vals[i : i + 50]
                if i > 0:
                    lines.append("GO")
                    cols = "[id], [user_id], [customer_name], [phone], [shipping_address], [status], [total_amount], [is_paid], [payment_method], [discount_amount], [coupon], [created_at]"
                    lines.append(f"INSERT INTO [Orders] ({cols}) VALUES")
                lines.append(",\n".join(batch) + ";")
        lines.append("GO")
        lines.append("SET IDENTITY_INSERT [Orders] OFF;")
        lines.append("GO")
        lines.append("")
        return "\n".join(lines) + "\n"

    def _export_order_items(self):
        items = OrderItem.objects.select_related(
            "order", "product", "variant"
        ).order_by("id")
        lines = ["-- Chi tiết đơn hàng", "SET IDENTITY_INSERT [OrderItems] ON;", "GO"]
        if items:
            cols = "[id], [order_id], [product_id], [variant_id], [color], [size], [quantity], [price]"
            lines.append(f"INSERT INTO [OrderItems] ({cols}) VALUES")
            vals = []
            for item in items:
                color = item.selected_color if item.variant else ""
                size = item.selected_size if item.variant else ""
                vals.append(
                    f"({item.id}, {item.order_id}, {item.product_id}, {item.variant_id}, "
                    f"{self._quote(color)}, {self._quote(size)}, {item.quantity}, {item.price})"
                )
            for i in range(0, len(vals), 50):
                batch = vals[i : i + 50]
                if i > 0:
                    lines.append("GO")
                    lines.append(f"INSERT INTO [OrderItems] ({cols}) VALUES")
                lines.append(",\n".join(batch) + ";")
        lines.append("GO")
        lines.append("SET IDENTITY_INSERT [OrderItems] OFF;")
        lines.append("GO")
        lines.append("")
        return "\n".join(lines) + "\n"

    def _export_wishlist(self):
        from products.models import WishlistItem

        wishes = WishlistItem.objects.all().order_by("id")
        lines = ["-- Sản phẩm yêu thích", "SET IDENTITY_INSERT [Wishlist] ON;", "GO"]
        if wishes:
            cols = "[id], [user_id], [product_id], [created]"
            lines.append(f"INSERT INTO [Wishlist] ({cols}) VALUES")
            vals = [
                f"({w.id}, {w.user_id}, {w.product_id}, {self._quote(w.created)})"
                for w in wishes
            ]
            lines.append(",\n".join(vals) + ";")
        lines.append("GO")
        lines.append("SET IDENTITY_INSERT [Wishlist] OFF;")
        lines.append("GO")
        lines.append("")
        return "\n".join(lines) + "\n"

    def _export_faqs(self):
        faqs = SupportFAQ.objects.all().order_by("id")
        lines = ["-- Câu hỏi thường gặp", "SET IDENTITY_INSERT [FAQs] ON;", "GO"]
        if faqs:
            cols = "[id], [question], [answer], [priority], [is_active]"
            lines.append(f"INSERT INTO [FAQs] ({cols}) VALUES")
            vals = [
                f"({f.id}, {self._quote(f.question)}, {self._quote(f.answer)}, {f.priority}, {1 if f.is_active else 0})"
                for f in faqs
            ]
            lines.append(",\n".join(vals) + ";")
        lines.append("GO")
        lines.append("SET IDENTITY_INSERT [FAQs] OFF;")
        lines.append("GO")
        lines.append("")
        return "\n".join(lines) + "\n"

    def _export_activities(self):
        acts = UserActivity.objects.all().order_by("id")
        lines = ["-- Lịch sử hoạt động", "SET IDENTITY_INSERT [Activities] ON;", "GO"]
        if acts:
            cols = "[id], [visitor_id], [user_id], [event_type], [path], [method], [status_code], [metadata], [created_at]"
            lines.append(f"INSERT INTO [Activities] ({cols}) VALUES")
            vals = []
            for a in acts:
                visitor_id = a.visitor_id if a.visitor_id else "NULL"
                user_id = a.user_id if a.user_id else "NULL"
                metadata = a.metadata if isinstance(a.metadata, dict) else {}
                import json

                meta_str = json.dumps(metadata, ensure_ascii=False).replace("'", "''")
                vals.append(
                    f"({a.id}, {visitor_id}, {user_id}, {self._quote(a.event_type)}, "
                    f"{self._quote(a.path)}, {self._quote(a.method)}, {a.status_code}, "
                    f"N'{meta_str}', {self._quote(a.created_at)})"
                )
            lines.append(",\n".join(vals) + ";")
        lines.append("GO")
        lines.append("SET IDENTITY_INSERT [Activities] OFF;")
        lines.append("GO")
        lines.append("")
        return "\n".join(lines) + "\n"
