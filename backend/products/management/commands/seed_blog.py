from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from products.models import BlogPost

POSTS = [
    {
        "title": "5 công thức phối đồ streetwear cho ngày đi làm bận rộn",
        "slug": "5-cong-thuc-phoi-do-streetwear-di-lam",
        "excerpt": "Không cần suy nghĩ nhiều — 5 bộ đồ gọn, dễ mặc, đủ điểm nhấn cho một tuần không lặp lại.",
        "body": """Streetwear không có nghĩa là luộm thuộm. Với 5 công thức dưới đây, bạn có thể đứng dậy khỏi giường, khoác đại một bộ và vẫn trông chỉn chu.

1. Áo thun trắng + quần tây ống đứng + giày sneaker trắng — an toàn tuyệt đối, lên đồ trong 2 phút.
2. Hoodie xám + quần cargo + giày bốt — chất đường phố nhưng vẫn tôn dáng.
3. Sơ mi oversize + quần jeans đen + giày loafer — lai giữa lịch lãm và thoải mái.
4. Áo polo + quần short dài + sneaker — công thức cho những ngày nắng.
5. Áo sweater + quần ống rộng + giày chunky — chuẩn "quiet luxury" giá phải chăng.

Mẹo chung: giữ bảng màu dưới 3 tông, chọn vải dày dặn giữ form, và để giày làm điểm nhấn. Đó là lý do HUUGIAU thiết kế theo hướng gọn và dễ phối — mỗi item trong tủ đều mặc được với nhau.""",
    },
    {
        "title": "Cách nhận biết denim chuẩn: chọn jeans không bao giờ hối hận",
        "slug": "cach-nhan-biet-denim-chuan",
        "excerpt": "Dày bao nhiêu là vừa? Làm sao biết vải tốt? Hướng dẫn chọn quần jeans thông minh trước khi xuống tiền.",
        "body": """Một chiếc quần jeans tốt không chỉ đẹp — nó phải bền, giữ form và lên màu đẹp theo thời gian.

Độ dày (oz): denim 10–13oz là khoảng lý tưởng cho khí hậu nhiệt đới — đủ dày để đứng form, đủ mỏng để không bí. Dưới 9oz dễ bai, trên 15oz nặng và khó mặc ở Việt Nam.

Cảm giác vải: vuốt ngược chiều — vải bông tốt có cảm giác hơi ráp nhưng chắc, không trơn bóng như vải pha polyester rẻ tiền.

Đường may: kiểm tra đường may cạp và ống — chỉ may đều, không đứt sợi. Cúc kim loại nguyên chất không bị hoen nhanh.

Form: mặc thử rồi ngồi xuống, cúi người — quần tốt không gò bó ở hông và đùi.

Tại HUUGIAU, mỗi mẫu quần đều qua kiểm tra size và chất liệu trước khi bán. Chọn đúng lần đầu, mặc lâu dài.""",
    },
    {
        "title": "Xu hướng thời trang 2026: ít hơn nhưng chất hơn",
        "slug": "xu-huong-thoi-trang-2026-it-hon-nhung-chat-hon",
        "excerpt": "Quiet luxury, màu trung tính và tủ đồ capsule — vì sao mùa này nên mua ít nhưng mua đúng.",
        "body": """Năm nay không phải là năm của những món đồ gây sốc. Xu hướng chính là "ít hơn nhưng chất hơn".

Quiet luxury: các item cắt may chuẩn, không logo to, dựa vào chất vải và form dáng để tỏa sáng. Một chiếc áo cotton dày 260gsm mặc đẹp hơn hẳn chiếc áo in hoạ tiết rẻ tiền.

Bảng màu trung tính: đen, trắng, kem, xám, denim — dễ phối, dễ lặp lại mà không bao giờ lỗi thời.

Tủ đồ capsule: 15–20 item mặc được với nhau thành hàng chục bộ khác nhau. Đây là triết lý HUUGIAU theo đuổi từ ngày đầu — gọn, dễ mặc, đủ điểm nhấn.

Trước khi mua một món đồ mới, tự hỏi: nó mặc được với ít nhất 3 món đang có trong tủ không? Nếu không, hãy để nó lại kệ.""",
    },
    {
        "title": "Hướng dẫn bảo quản vải cotton để áo không bai, không xù",
        "slug": "bao-quan-vai-cotton-khong-bai",
        "excerpt": "Giặt đúng cách là cách rẻ nhất để kéo dài tuổi thọ áo thun yêu thích của bạn.",
        "body": """Áo cotton dày dặn vẫn có thể bai, xù và mất màu nếu chăm sóc sai. Vài mẹo nhỏ:

Giặt ngược mặt: bảo vệ bề mặt vải và hoạ tiết in khỏi ma sát trong máy giặt.

Nước mát dưới 30 độ: nước nóng làm co và phai màu nhanh. Không ngâm quá 15 phút.

Không dùng thuốc tẩy clo: nó phá huỷ sợi bông. Ưu tiên nước giặt dịu nhẹ.

Phân loại màu: tránh giặt chung đồ tối màu với đồ sáng trong lần đầu.

Phơi bóng râm: nắng gắt trực tiếp làm vải khô giòn và phai màu. Lật mặt trái khi phơi.

Ủi nhiệt độ vừa: đặt vải mỏng lên trên hoặc ủi mặt trái để tránh bóng vải.

Làm đúng các bước trên, chiếc áo 200 nghìn có thể mặc đẹp sau vài năm — đúng tinh thần "mua ít, mua chất".""",
    },
]

DEFAULT_COVER = "https://images.unsplash.com/photo-1523381210434-271e8be1f52b?auto=format&fit=crop&w=1200&q=70"


class Command(BaseCommand):
    help = "Tạo dữ liệu lookbook mẫu (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force", action="store_true", help="Xóa bài cũ trước khi seed."
        )

    def handle(self, *args, **options):
        if options["force"]:
            BlogPost.objects.all().delete()
        created = 0
        for idx, item in enumerate(POSTS):
            post, was_created = BlogPost.objects.get_or_create(
                slug=item["slug"],
                defaults={
                    "title": item["title"],
                    "excerpt": item["excerpt"],
                    "body": item["body"],
                    "cover_image_url": DEFAULT_COVER,
                    "created": timezone.now() - timedelta(days=len(POSTS) - idx),
                },
            )
            created += int(was_created)
        self.stdout.write(self.style.SUCCESS(f"Đã tạo {created} bài viết lookbook."))
