import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from products.models import Product, Review

COMMENTS = {
    5: [
        "Chất vải dày dặn, đường may kỹ. Mặc lên rất sang, đúng kiểu mình cần.",
        "Nhận hàng nhanh, đóng gói cẩn thận. Sản phẩm đẹp hơn cả hình chụp!",
        "Mặc vừa vặn, form chuẩn. Đã ủng hộ shop lần 3, lần nào cũng hài lòng.",
        "Size chuẩn, chất liệu thoáng mát. Sẽ giới thiệu cho bạn bè.",
        "Xịn xò, màu đúng như mô tả. Shop tư vấn nhiệt tình lắm.",
        "Hàng tốt, giá hợp lý. Mặc thoải mái, mix đồ đơn giản mà vẫn đẹp.",
    ],
    4: [
        "Chất lượng ổn, chỉ là màu hơi khác hình chút xíu. Nhìn chung hài lòng.",
        "Mặc đẹp, vải mềm. Giao hàng hơi lâu nhưng đáng chờ.",
        "Form đẹp, mặc lên đúng gu streetwear. Trừ nửa sao vì tà áo hơi dài.",
        "Sản phẩm ok, đóng gói gọn gàng. Sẽ mua tiếp nếu có mẫu mới.",
        "Đúng mô tả, giá hơi cao nhưng chất lượng bù lại.",
    ],
    3: [
        "Bình thường, chất vải không quá ấn tượng như mong đợi.",
        "Được giá, nhưng form hơi rộng hơn size tiêu chuẩn.",
    ],
}

USERNAMES = [f"user{i:02d}" for i in range(1, 51)]


class Command(BaseCommand):
    help = "Tạo dữ liệu đánh giá mẫu cho các sản phẩm có sẵn (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument("--per-product", type=int, default=4, help="Số review mỗi sản phẩm (mặc định 4).")
        parser.add_argument("--force", action="store_true", help="Xóa review cũ trước khi seed.")

    def handle(self, *args, **options):
        per_product = options["per_product"]
        if options["force"]:
            Review.objects.all().delete()

        products = list(Product.objects.filter(available=True))
        users = list(get_user_model().objects.filter(is_staff=False))
        if not products or not users:
            self.stdout.write(self.style.ERROR("Cần sản phẩm và user thường trước khi seed review."))
            return

        created = 0
        random.seed(2026)
        for product in products:
            pool = [u for u in users if not product.reviews.filter(user=u).exists()]
            chosen = random.sample(pool, min(per_product, len(pool)))
            for idx, user in enumerate(chosen):
                rating = random.choice([5, 5, 5, 4, 4, 3])
                Review.objects.create(
                    product=product,
                    user=user,
                    rating=rating,
                    comment=random.choice(COMMENTS[rating]),
                    verified_purchase=random.random() < 0.8,
                    created=timezone.now() - timedelta(days=random.randint(1, 60), hours=random.randint(0, 23)),
                )
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Đã tạo {created} đánh giá mẫu cho {len(products)} sản phẩm."))
