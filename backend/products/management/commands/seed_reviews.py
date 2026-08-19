import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from products.models import Product, Review

FIVE_OPENERS = [
    "Chất liệu dày dặn, đường may kỹ càng.",
    "Mình nhận hàng nhanh, đóng gói cẩn thận.",
    "Form chuẩn, mặc lên đúng gu luôn.",
    "Size chuẩn như bảng hướng dẫn, khỏi phải đổi.",
    "Hàng đẹp hơn cả hình chụp, màu chuẩn như mô tả.",
    "Đặt lần 3 rồi, chất lượng ổn định từ đầu đến giờ.",
    "Vải mềm, thoáng, mặc cả ngày không bí.",
    "Màu lên đẹp, phối đồ dễ dàng.",
    "Đóng gói chỉn chu, kèm hóa đơn, mở ra thấy ưng liền.",
    "Giao hàng đúng hẹn, shipper thân thiện.",
    "Áo cân đối, đường chỉ đều tăm tắp.",
    "Chất liệu xịn xò hơn mức giá mình trả.",
]

FIVE_DETAILS = [
    " Mặc lên rất sang, đúng kiểu mình cần.",
    " Đã ủng hộ shop mấy lần, lần nào cũng hài lòng.",
    " Sẽ giới thiệu cho bạn bè mua cùng.",
    " Mix với quần jean và giày trắng là có set đẹp.",
    " Shop tư vấn nhiệt tình về size trước khi đặt.",
    " So với giá tiền thì quá xứng đáng.",
    " Chất vải không bị xù, giặt vài lần vẫn mới.",
    " Mặc đi làm, đi chơi đều phù hợp.",
    " Đúng phong cách streetwear mình đang tìm.",
    " Ông xã khen mặc lên nhìn trẻ hơn hẳn.",
    " Có túi giấy xịn xò, tặng quà cũng được.",
]

FIVE_CLOSERS = [
    " Sẽ mua thêm mẫu khác trong lần tới.",
    " 5 sao cho shop!",
    " Cảm ơn shop đã phục vụ tận tình.",
    " Nhìn chung rất hài lòng.",
    " Sẽ quay lại nếu có sale.",
    " Đánh giá này hoàn toàn chân thật từ trải nghiệm.",
]

FOUR_COMMENTS = [
    "Chất lượng ổn, chỉ là màu hơi khác hình chút xíu. Nhìn chung hài lòng.",
    "Mặc đẹp, vải mềm. Giao hàng hơi lâu nhưng đáng chờ.",
    "Form đẹp, đúng gu streetwear. Trừ nửa sao vì tà áo hơi dài.",
    "Sản phẩm ok, đóng gói gọn gàng. Sẽ mua tiếp nếu có mẫu mới.",
    "Đúng mô tả, giá hơi cao nhưng chất lượng bù lại.",
    "Vải ổn, đường may tốt. Hơi ra mùi thuốc nhuộm, giặt một lần là hết.",
    "Mặc vừa người. Mong shop thêm màu tối vì dễ dùng hơn.",
    "Hàng chuẩn, đóng gói kỹ. Chờ 2 ngày mới giao hơi lâu.",
    "Áo đẹp, form chuẩn. Trừ 1 sao vì size S hơi rộng với người nhỏ.",
    "Chất vải tốt, màu đẹp. Hy vọng shop cải thiện khâu giao hàng.",
]

THREE_COMMENTS = [
    "Bình thường, chất vải không quá ấn tượng như mong đợi.",
    "Được giá, nhưng form hơi rộng hơn size tiêu chuẩn.",
    "Chất lượng tạm ổn. Màu thực tế nhạt hơn hình khá nhiều.",
    "Vải hơi mỏng, mặc nội thất thì ổn chứ ra đường thì hơi tiếc tiền.",
    "Đúng chất lượng trong tầm giá, không có gì đặc biệt.",
    "Mua áo lần trước ưng hơn, lần này form không đều lắm.",
]

EMOJIS = ["", "", "", "", "❤️", "🔥", "✨"]

REAL_NAMES = [
    "Nguyễn Minh Anh", "Trần Thu Hà", "Lê Quốc Bảo", "Phạm Ngọc Mai", "Hoàng Gia Huy",
    "Vũ Khánh Linh", "Đặng Tuấn Kiệt", "Bùi Phương Thảo", "Đỗ Thanh Tùng", "Hồ Mỹ Duyên",
    "Ngô Đức Huy", "Dương Bảo Ngọc", "Lý Công Minh", "Trịnh Thùy Trang", "Cao Văn Hùng",
    "Đinh Hồng Nhung", "Lương Minh Phúc", "Mai Hải Yến", "Tạ Quang Vinh", "Phan Thị Hằng",
    "Võ Anh Khoa", "Đoàn Ngọc Lan", "Tô Văn Tài", "Hứa Thanh Huyền", "Lâm Thế Vũ",
    "Châu Hồng Ánh", "Trương Quốc Cường", "Kiều Thị Hoa", "Phùng Văn Nam", "Giang Thu Hương",
    "Bạch Đăng Khoa", "Lại Minh Châu", "Hà Duy Long", "Cấn Thị Nga", "Nông Văn Dũng",
    "Vi Thùy Dương", "Sử Đức Thịnh", "Nghiêm Bích Ngọc", "Quách Văn Sơn", "Lê Thị Bích",
    "Nguyễn Đức Thành", "Trần Hải Đăng", "Phạm Nhật Minh", "Hoàng Thị Lan", "Vũ Đình Khôi",
    "Đặng Xuân Trường", "Bùi Thanh Vy", "Đỗ Trọng Nhân", "Hồ Kim Oanh", "Ngô Văn Tuấn",
]


def compose_comment(rating):
    if rating == 5:
        text = random.choice(FIVE_OPENERS) + random.choice(FIVE_DETAILS)
        if random.random() < 0.6:
            text += random.choice(FIVE_CLOSERS)
    elif rating == 4:
        text = random.choice(FOUR_COMMENTS)
    else:
        text = random.choice(THREE_COMMENTS)
    if random.random() < 0.12:
        text += " " + random.choice(EMOJIS)
    return text


SHOP_REPLIES = [
    "Cảm ơn anh/chị đã tin tưởng ủng hộ HUUGIAU. Rất vui vì sản phẩm làm hài lòng bạn!",
    "Cảm ơn đánh giá chi tiết của bạn. Shop sẽ ghi nhận góp ý để ngày càng hoàn thiện hơn.",
    "Cảm ơn bạn đã chọn HUUGIAU Studio. Hy vọng sớm gặp lại bạn ở những lần mua tiếp theo!",
    "Cảm ơn bạn! Shop luôn cố gắng tư vấn tận tình để bạn chọn được đúng size và màu ưng ý nhất.",
    "Cảm ơn bạn đã chia sẻ. Chất lượng luôn là ưu tiên số một của HUUGIAU.",
    "Cảm ơn bạn. Chúc bạn luôn xinh đẹp với set đồ mới nhé!",
    "Dạ cảm ơn anh/chị. Shop sẽ kiểm tra lại khâu đóng gói để cải thiện ngay ạ.",
    "Xin cảm ơn phản hồi chân thành của bạn. HUUGIAU sẽ cố gắng hơn nữa ở lần mua sau!",
]


class Command(BaseCommand):
    help = "Tạo dữ liệu đánh giá mẫu cho các sản phẩm có sẵn (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument("--per-product", type=int, default=4, help="Số review mỗi sản phẩm (mặc định 4).")
        parser.add_argument("--force", action="store_true", help="Xóa review cũ trước khi seed.")

    def _backfill_names(self):
        users = sorted(get_user_model().objects.filter(is_staff=False), key=lambda u: u.username)
        updated = 0
        for idx, user in enumerate(users):
            if user.get_full_name():
                continue
            full = REAL_NAMES[idx % len(REAL_NAMES)]
            first, _, last = full.rpartition(" ")
            user.first_name, user.last_name = first, last
            user.save(update_fields=["first_name", "last_name"])
            updated += 1
        return updated

    def handle(self, *args, **options):
        per_product = options["per_product"]
        if options["force"]:
            Review.objects.all().delete()

        renamed = self._backfill_names()
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
                    comment=compose_comment(rating),
                    verified_purchase=random.random() < 0.8,
                    created=timezone.now() - timedelta(days=random.randint(1, 60), hours=random.randint(0, 23)),
                )
                created += 1

        backfilled = 0
        for review in Review.objects.filter(shop_reply="").order_by("-created")[:300]:
            if random.random() < 0.55:
                review.shop_reply = random.choice(SHOP_REPLIES)
                review.save(update_fields=["shop_reply"])
                backfilled += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Đã tạo {created} đánh giá mẫu cho {len(products)} sản phẩm, "
                f"gán tên thật cho {renamed} tài khoản, shop phản hồi {backfilled} đánh giá."
            )
        )
