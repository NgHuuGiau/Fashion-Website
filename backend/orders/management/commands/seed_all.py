import random
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

from orders.models import Coupon, Order, OrderItem
from products.models import Product, SupportFAQ, WishlistItem
from users.models import UserActivity, UserProfile, VisitorSession


class Command(BaseCommand):
    help = "Seed toàn bộ database: migrate, sản phẩm, users, coupons, đơn hàng các trạng thái."

    def handle(self, *args, **options):
        self.stdout.write("[1/6] Migrating...")
        call_command("migrate", verbosity=0)

        self.stdout.write("[2/6] Seeding products...")
        call_command("seed_products", sync=True, verbosity=0)

        self.stdout.write("[3/6] Creating users...")
        self._create_users()

        self.stdout.write("[4/6] Creating coupons...")
        self._create_coupons()

        self.stdout.write("[5/6] Creating orders...")
        self._create_orders()

        self.stdout.write("[6/6] Creating FAQs & wishlist...")
        self._create_faqs()
        self._create_wishlists()
        self._create_activities()

        self.stdout.write(self.style.SUCCESS("Done!"))

    def _create_users(self):
        users_data = [
            ("admin", "admin@example.com", "admin123", True, True, "Quản Trị", "Viên"),
            ("codexstaff", "staff@codex.com", "staff123", False, True, "Nhân", "Viên"),
            ("readmestaff", "readme@staff.com", "readme123", False, True, "Điều Phối", "Đơn Hàng"),
            ("nguyenvanA", "nguyenvana@email.com", "user123", False, False, "Nguyễn Văn", "An"),
            ("tranthib", "tranthib@email.com", "user123", False, False, "Trần Thị", "Bích"),
            ("lethic", "lethic@email.com", "user123", False, False, "Lê Thị", "Cẩm"),
            ("phamvand", "phamvand@email.com", "user123", False, False, "Phạm Văn", "Dũng"),
            ("hoangthie", "hoangthie@email.com", "user123", False, False, "Hoàng Thị", "Em"),
        ]
        for username, email, pw, is_super, is_staff, first, last in users_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults=dict(email=email, is_superuser=is_super, is_staff=is_staff),
            )
            if created:
                user.set_password(pw)
                user.first_name = first
                user.last_name = last
                user.save()
                UserProfile.objects.get_or_create(user=user)
        self.stdout.write(f"  -> {User.objects.count()} users")

    def _create_coupons(self):
        coupons = [
            Coupon(code="FREESHIP", discount_type="freeship", value=0, is_active=True, min_order_amount=200000),
            Coupon(code="SALE10", discount_type="percent", value=10, is_active=True, min_order_amount=100000, max_discount_amount=50000),
            Coupon(code="GIAM50K", discount_type="fixed", value=50000, is_active=True, min_order_amount=300000),
            Coupon(code="WELCOME", discount_type="percent", value=15, is_active=True, min_order_amount=0, max_discount_amount=100000, usage_limit=100),
            Coupon(code="BLACKFRI", discount_type="percent", value=30, is_active=False, max_discount_amount=200000),
        ]
        for c in coupons:
            Coupon.objects.get_or_create(code=c.code, defaults=dict(
                discount_type=c.discount_type, value=c.value, is_active=c.is_active,
                min_order_amount=c.min_order_amount, max_discount_amount=c.max_discount_amount,
                usage_limit=c.usage_limit,
            ))
        self.stdout.write(f"  -> {Coupon.objects.count()} coupons")

    def _create_orders(self):
        users = list(User.objects.filter(is_superuser=False))
        products = list(Product.objects.select_related("category"))
        now = timezone.now()
        statuses = ["pending", "processing", "processing", "shipping", "delivered", "delivered", "cancelled"]
        count = 0

        for user in users:
            for _ in range(random.randint(3, 7)):
                status = random.choice(statuses)
                num_items = random.choices([1, 2, 3], weights=[60, 30, 10])[0]
                chosen = random.sample(products, min(num_items, len(products)))
                subtotal = 0
                items_data = []

                for p in chosen:
                    variant = p.variants.filter(is_active=True).first()
                    qty = random.randint(1, 3)
                    price = p.price
                    subtotal += price * qty
                    items_data.append((p, variant, qty, price))

                shipping = 30000
                discount = 0
                coupon = None
                if status in ("delivered", "processing") and random.random() > 0.6:
                    coupon = Coupon.objects.filter(is_active=True).order_by("?").first()
                    if coupon and subtotal >= coupon.min_order_amount:
                        if coupon.discount_type == "percent":
                            discount = min(int(subtotal * coupon.value / 100), coupon.max_discount_amount or 999999)
                        elif coupon.discount_type == "fixed":
                            discount = coupon.value
                total = subtotal + shipping - discount

                is_paid = status in ("delivered", "shipping")
                created = now - timedelta(
                    days=random.randint(1, 45),
                    hours=random.randint(0, 23),
                )

                order = Order.objects.create(
                    user=user,
                    customer_name=user.get_full_name() or user.username,
                    customer_email=user.email,
                    phone=f"09{random.randint(10000000, 99999999)}",
                    shipping_address=f"{random.randint(1, 999)} Đường {random.choice(['Nguyễn Huệ', 'Lê Lợi', 'Trần Hưng Đạo', 'Phạm Ngũ Lão', 'Hai Bà Trưng', 'Lý Thường Kiệt', 'Võ Văn Tần', 'Cách Mạng Tháng 8'])}, Quận {random.randint(1, 12)}, TP.HCM",
                    note=random.choice(["", "Giao hàng trong giờ hành chính", "Gọi trước khi giao", ""]),
                    payment_method=random.choice(["cod", "bank"]),
                    bank_code="VCB" if random.random() > 0.5 else "",
                    is_paid=is_paid,
                    status=status,
                    subtotal_amount=subtotal,
                    shipping_fee=shipping,
                    discount_amount=discount,
                    coupon=coupon,
                    coupon_code=coupon.code if coupon else "",
                    total_amount=total,
                )
                Order.objects.filter(pk=order.pk).update(created_at=created)

                for product, variant, qty, price in items_data:
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        variant=variant,
                        selected_color=variant.color_name if variant else "",
                        selected_size=variant.size if variant else "",
                        quantity=qty,
                        price=price,
                    )
                count += 1

        self.stdout.write(f"  -> {count} orders, {OrderItem.objects.count()} items")

    def _create_faqs(self):
        faqs = [
            ("Tôi có thể đổi trả hàng không?", "đổi trả hàng", "Chúng tôi hỗ trợ đổi trả trong vòng 7 ngày kể từ khi nhận hàng, với điều kiện sản phẩm còn nguyên tem mác và chưa qua sử dụng.", 10),
            ("Thời gian giao hàng bao lâu?", "giao hàng thời gian", "Giao hàng nội thành TP.HCM: 1-2 ngày làm việc. Các tỉnh thành khác: 3-7 ngày làm việc.", 20),
            ("Tôi có thể hủy đơn hàng không?", "hủy đơn hàng", "Bạn có thể hủy đơn hàng trong vòng 24h kể từ khi đặt hàng. Sau thời gian này, vui lòng liên hệ CSKH để được hỗ trợ.", 30),
            ("Phương thức thanh toán nào được hỗ trợ?", "thanh toán", "Chúng tôi hỗ trợ thanh toán khi nhận hàng (COD) và chuyển khoản ngân hàng.", 40),
        ]
        for q, kw, a, pri in faqs:
            SupportFAQ.objects.get_or_create(question=q, defaults=dict(keywords=kw, answer=a, priority=pri))
        self.stdout.write(f"  -> {SupportFAQ.objects.count()} FAQs")

    def _create_wishlists(self):
        users = list(User.objects.filter(is_superuser=False))
        products = list(Product.objects.all())
        count = 0
        for user in users:
            for _ in range(random.randint(1, 4)):
                product = random.choice(products)
                _, created = WishlistItem.objects.get_or_create(user=user, product=product)
                if created:
                    count += 1
        self.stdout.write(f"  -> {count} wishlist items")

    def _create_activities(self):
        users = list(User.objects.all())
        paths = ["/", "/products/", "/cart/", "/checkout/", "/orders/"]
        events = ["page_view", "page_view", "page_view", "action", "cart_add", "checkout"]
        count = 0
        for user in users:
            for _ in range(random.randint(3, 8)):
                session_key = f"seed_session_{user.id}"
                session, _ = VisitorSession.objects.get_or_create(
                    session_key=session_key,
                    defaults=dict(is_authenticated=True, user=user),
                )
                UserActivity.objects.create(
                    visitor=session, user=user,
                    event_type=random.choice(events),
                    path=random.choice(paths),
                    metadata={"referrer": "seed"},
                )
                count += 1
        self.stdout.write(f"  -> {count} activity logs")
