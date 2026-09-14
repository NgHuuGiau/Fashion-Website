import os

# ruff: noqa: E402
os.environ["DJANGO_SETTINGS_MODULE"] = "core.settings"
import django

django.setup()

import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from orders.models import Coupon, Order, OrderItem
from products.models import Product, Review
from users.models import UserProfile, UserAddress
from django.utils import timezone

# Clear existing data
Review.objects.all().delete()
OrderItem.objects.all().delete()
Order.objects.all().delete()
Coupon.objects.all().delete()
UserAddress.objects.all().delete()
User.objects.filter(is_superuser=False).delete()

# 1. Create users: 1 admin, 3 staff, 15 users = 19 total
users_data = [
    ("admin", "admin@example.com", "admin123", True, True, "Quản Trị", "Viên"),
    ("staff1", "staff1@example.com", "staff123", False, True, "Nhân", "Viên 1"),
    ("staff2", "staff2@example.com", "staff123", False, True, "Nhân", "Viên 2"),
    ("staff3", "staff3@example.com", "staff123", False, True, "Nhân", "Viên 3"),
    ("user01", "user01@example.com", "user123", False, False, "Nguyễn Văn", "An"),
    ("user02", "user02@example.com", "user123", False, False, "Trần Thị", "Bình"),
    ("user03", "user03@example.com", "user123", False, False, "Lê Văn", "Cường"),
    ("user04", "user04@example.com", "user123", False, False, "Phạm Thị", "Dung"),
    ("user05", "user05@example.com", "user123", False, False, "Hoàng Văn", "Em"),
    ("user06", "user06@example.com", "user123", False, False, "Võ Thị", "Phương"),
    ("user07", "user07@example.com", "user123", False, False, "Đặng Văn", "Giang"),
    ("user08", "user08@example.com", "user123", False, False, "Bùi Thị", "Hoa"),
    ("user09", "user09@example.com", "user123", False, False, "Đỗ Văn", "Kiên"),
    ("user10", "user10@example.com", "user123", False, False, "Ngô Thị", "Lan"),
    ("user11", "user11@example.com", "user123", False, False, "Dương Văn", "Minh"),
    ("user12", "user12@example.com", "user123", False, False, "Lý Thị", "Na"),
    ("user13", "user13@example.com", "user123", False, False, "Kim Văn", "Quang"),
    ("user14", "user14@example.com", "user123", False, False, "Trịnh Thị", "Thảo"),
    ("user15", "user15@example.com", "user123", False, False, "Vũ Văn", "Đạt"),
]

created_users = []
for username, email, pw, is_super, is_staff, first, last in users_data:
    user, created = User.objects.get_or_create(
        username=username,
        defaults=dict(
            email=email,
            is_superuser=is_super,
            is_staff=is_staff,
            first_name=first,
            last_name=last,
        ),
    )
    if created:
        user.set_password(pw)
        user.save()
    UserProfile.objects.get_or_create(user=user)
    print(f"Created user: {username}")

# 2. Create 30 coupons
coupons_data = [
    {
        "code": "FREESHIP",
        "type": "freeship",
        "value": 0,
        "active": True,
        "min_amt": 200000,
    },
    {
        "code": "SALE10",
        "type": "percent",
        "value": 10,
        "active": True,
        "min_amt": 100000,
        "max_disc": 50000,
    },
    {
        "code": "GIAM50K",
        "type": "fixed",
        "value": 50000,
        "active": True,
        "min_amt": 300000,
    },
    {
        "code": "WELCOME",
        "type": "percent",
        "value": 15,
        "active": True,
        "min_amt": 0,
        "max_disc": 100000,
        "usage_limit": 100,
    },
    {
        "code": "HBD",
        "type": "percent",
        "value": 20,
        "active": True,
        "min_amt": 0,
        "max_disc": 200000,
        "usage_limit": 500,
        "ends_at": timezone.now() + timedelta(days=3650),
    },
    {
        "code": "BLACKFRI",
        "type": "percent",
        "value": 30,
        "active": False,
        "max_disc": 200000,
    },
    {
        "code": "VIP20",
        "type": "percent",
        "value": 20,
        "active": True,
        "min_amt": 500000,
        "max_disc": 200000,
    },
    {
        "code": "NEWUSER",
        "type": "fixed",
        "value": 30000,
        "active": True,
        "min_amt": 150000,
        "usage_limit": 200,
    },
    {
        "code": "FLASH15",
        "type": "percent",
        "value": 15,
        "active": True,
        "min_amt": 200000,
        "max_disc": 100000,
        "ends_at": timezone.now() + timedelta(days=7),
    },
    {
        "code": "STUDENT",
        "type": "percent",
        "value": 10,
        "active": True,
        "min_amt": 100000,
        "max_disc": 50000,
    },
    {
        "code": "SALE20",
        "type": "percent",
        "value": 20,
        "active": True,
        "min_amt": 200000,
        "max_disc": 100000,
    },
    {
        "code": "SALE30",
        "type": "percent",
        "value": 30,
        "active": True,
        "min_amt": 500000,
        "max_disc": 200000,
    },
    {
        "code": "GIAM100K",
        "type": "fixed",
        "value": 100000,
        "active": True,
        "min_amt": 500000,
    },
    {
        "code": "GIAM200K",
        "type": "fixed",
        "value": 200000,
        "active": True,
        "min_amt": 1000000,
    },
    {
        "code": "FREESHIP2",
        "type": "freeship",
        "value": 0,
        "active": True,
        "min_amt": 100000,
    },
    {
        "code": "VIP15",
        "type": "percent",
        "value": 15,
        "active": True,
        "min_amt": 300000,
        "max_disc": 150000,
    },
    {
        "code": "NEWYEAR",
        "type": "percent",
        "value": 25,
        "active": True,
        "min_amt": 0,
        "max_disc": 300000,
        "usage_limit": 500,
        "ends_at": timezone.now() + timedelta(days=30),
    },
    {
        "code": "SUMMER",
        "type": "percent",
        "value": 20,
        "active": True,
        "min_amt": 200000,
        "max_disc": 150000,
        "ends_at": timezone.now() + timedelta(days=90),
    },
    {
        "code": "AUTUMN",
        "type": "percent",
        "value": 15,
        "active": True,
        "min_amt": 150000,
        "max_disc": 100000,
        "ends_at": timezone.now() + timedelta(days=90),
    },
    {
        "code": "WINTER",
        "type": "percent",
        "value": 10,
        "active": True,
        "min_amt": 100000,
        "max_disc": 50000,
        "ends_at": timezone.now() + timedelta(days=90),
    },
    {
        "code": "FLASH50",
        "type": "percent",
        "value": 50,
        "active": True,
        "min_amt": 0,
        "max_disc": 500000,
        "usage_limit": 100,
        "ends_at": timezone.now() + timedelta(days=7),
    },
    {
        "code": "WEEKEND",
        "type": "percent",
        "value": 15,
        "active": True,
        "min_amt": 200000,
        "max_disc": 100000,
        "ends_at": timezone.now() + timedelta(days=2),
    },
    {
        "code": "MIDNIGHT",
        "type": "percent",
        "value": 20,
        "active": True,
        "min_amt": 300000,
        "max_disc": 200000,
        "ends_at": timezone.now() + timedelta(days=1),
    },
    {
        "code": "LOYALTY",
        "type": "percent",
        "value": 10,
        "active": True,
        "min_amt": 0,
        "max_disc": 50000,
        "usage_limit": 1000,
    },
    {
        "code": "REFERRAL",
        "type": "fixed",
        "value": 50000,
        "active": True,
        "min_amt": 200000,
        "usage_limit": 200,
    },
    {
        "code": "BULK5",
        "type": "percent",
        "value": 5,
        "active": True,
        "min_amt": 1000000,
        "max_disc": 500000,
    },
    {
        "code": "BULK10",
        "type": "percent",
        "value": 10,
        "active": True,
        "min_amt": 2000000,
        "max_disc": 1000000,
    },
    {
        "code": "FLASH20",
        "type": "percent",
        "value": 20,
        "active": True,
        "min_amt": 0,
        "max_disc": 200000,
        "usage_limit": 50,
        "ends_at": timezone.now() + timedelta(days=3),
    },
    {
        "code": "MEMBER",
        "type": "percent",
        "value": 5,
        "active": True,
        "min_amt": 0,
        "max_disc": 50000,
    },
    {
        "code": "STAFF20",
        "type": "percent",
        "value": 20,
        "active": True,
        "min_amt": 0,
        "max_disc": 200000,
        "usage_limit": 100,
    },
]

for c in coupons_data:
    Coupon.objects.create(
        code=c["code"],
        discount_type=c["type"],
        value=c["value"],
        is_active=c["active"],
        min_order_amount=c.get("min_amt", 0),
        max_discount_amount=c.get("max_disc"),
        usage_limit=c.get("usage_limit"),
        ends_at=c.get("ends_at"),
    )
    print(f"Created coupon: {c['code']}")

# 3. Create 5000 orders with reviews
products = list(Product.objects.select_related("category").prefetch_related("variants"))
if not products:
    print("ERROR: No products found!")
    exit(1)

statuses = [
    "pending",
    "processing",
    "processing",
    "shipping",
    "delivered",
    "delivered",
    "cancelled",
]
streets = [
    "Nguyễn Huệ",
    "Lê Lợi",
    "Trần Hưng Đạo",
    "Phạm Ngũ Lão",
    "Hai Bà Trưng",
    "Lý Thường Kiệt",
    "Võ Văn Tần",
    "Cách Mạng Tháng 8",
]
notes = ["", "Giao hàng trong giờ hành chính", "Gọi trước khi giao", "Để tại cửa", ""]
payment_methods = ["cod", "bank", "vnpay"]

active_coupons = [c for c in Coupon.objects.filter(is_active=True)]
users = list(User.objects.filter(is_superuser=False))

count = 0
review_count = 0

for i in range(5000):
    user = random.choice(users)
    status = random.choice(statuses)
    num_items = random.choices([1, 2, 3, 4], weights=[50, 30, 15, 5])[0]
    chosen = random.sample(products, min(num_items, len(products)))

    subtotal = Decimal(0)
    items_data = []

    for p in chosen:
        variant = p.variants.filter(is_active=True).first()
        qty = random.randint(1, 3)
        price = p.price
        subtotal += price * qty
        items_data.append((p, variant, qty, price))

    shipping = random.choice([0, 25000, 30000, 35000])
    discount = 0
    coupon = None
    coupon_code = ""

    if (
        status in ("delivered", "shipping", "processing")
        and random.random() > 0.5
        and active_coupons
    ):
        coupon = random.choice(active_coupons)
        if coupon and subtotal >= coupon.min_order_amount:
            if coupon.discount_type == "percent":
                discount = min(
                    int(subtotal * coupon.value / 100),
                    coupon.max_discount_amount or 999999,
                )
            elif coupon.discount_type == "fixed":
                discount = coupon.value
            elif coupon.discount_type == "freeship":
                discount = shipping
            coupon_code = coupon.code

    total = subtotal + shipping - discount
    is_paid = status in ("delivered", "shipping", "processing")
    created = timezone.now() - timedelta(
        days=random.randint(0, 365),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )

    order = Order.objects.create(
        user=user,
        customer_name=user.get_full_name() or user.username,
        customer_email=user.email,
        phone=f"09{random.randint(10000000, 99999999)}",
        shipping_address=f"{random.randint(1, 999)} Đường {random.choice(streets)}, Quận {random.randint(1, 12)}, TP.HCM",
        note=random.choice(notes),
        payment_method=random.choice(payment_methods),
        bank_code="VCB" if random.random() > 0.5 else "",
        is_paid=is_paid,
        status=status,
        subtotal_amount=subtotal,
        shipping_fee=shipping,
        discount_amount=discount,
        coupon=coupon,
        coupon_code=coupon_code,
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

    # Reviews for delivered orders (85% chance, more reviews per order)
    if status == "delivered" and random.random() < 0.85:
        for product, variant, qty, price in items_data:
            if random.random() < 0.9:
                rating = random.choices([5, 4, 3, 2, 1], weights=[40, 30, 15, 10, 5])[0]
                review_texts = {
                    5: [
                        "Rất tốt! Chất lượng vượt mong đợi.",
                        "Sẽ mua lại.",
                        "Đẹp như ảnh.",
                        "Chất lượng vượt mong đợi.",
                    ],
                    4: [
                        "Tốt.",
                        "Đáng đồng tiền bát gạo.",
                        "Hài lòng.",
                        "Chỉnh size chuẩn.",
                    ],
                    3: [
                        "Bình thường.",
                        "Chấp nhận được.",
                        "Không tệ.",
                        "Size hơi lớn/nhỏ.",
                    ],
                    2: ["Chất lượng chưa tốt.", "Màu khác ảnh.", "Size sai."],
                    1: ["Rất tệ.", "Khác hoàn toàn mô tả.", "Sẽ không mua lại."],
                }
                Review.objects.get_or_create(
                    product=product,
                    user=user,
                    defaults=dict(
                        rating=rating,
                        comment=random.choice(review_texts[rating]),
                        is_published=True,
                        verified_purchase=True,
                    ),
                )
                review_count += 1

    if (i + 1) % 500 == 0:
        print(f"Created {i + 1}/5000 orders...")

# 4. Create 200 addresses
UserAddress.objects.all().delete()
districts = [
    "Quận 1",
    "Quận 3",
    "Quận 4",
    "Quận 5",
    "Quận 7",
    "Quận 10",
    "Bình Thạnh",
    "Phú Nhuận",
    "Gò Vấp",
    "Tân Bình",
]
wards = [
    "Phường 1",
    "Phường 2",
    "Phường 3",
    "Phường 4",
    "Phường 5",
    "Phường 6",
    "Phường 7",
    "Phường 8",
]
streets = [
    "Nguyễn Huệ",
    "Lê Lợi",
    "Trần Hưng Đạo",
    "Phạm Ngũ Lão",
    "Hai Bà Trưng",
    "Lý Thường Kiệt",
    "Võ Văn Tần",
    "Cách Mạng Tháng 8",
]

addresses_created = 0
users = list(User.objects.filter(is_superuser=False))
while addresses_created < 200:
    user = random.choice(users)
    j = addresses_created % 4
    is_default = j == 0
    full_addr = f"{random.randint(1, 999)} Đường {random.choice(streets)}, {random.choice(wards)}, {random.choice(districts)}, TP.HCM"
    UserAddress.objects.create(
        user=user,
        label=f"Địa chỉ {j + 1}",
        recipient_name=user.get_full_name() or user.username,
        phone=f"09{random.randint(10000000, 99999999)}",
        address=full_addr,
        is_default=is_default,
    )
    addresses_created += 1

print("Done! Created orders, reviews, and addresses.")
