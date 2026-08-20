from django.core.management.base import BaseCommand

from products.models import Product

TEMPLATES = {
    "ao": {
        "opening": [
            "Chất liệu cotton 240gsm dày dặn, mặc lên tôn dáng, không xù, không bai. Form chuẩn, đường may kỹ từng chi tiết, cổ áo giữ form tốt sau nhiều lần giặt.",
            "Vải cotton compact cao cấp, bề mặt mịn, thấm hút tốt. Form oversize thoải mái, dễ dàng phối với quần jeans, cargo hay quần tây.",
            "Chất nỉ cotton pha poly ổn định, giữ ấm vừa phải, không bí. Thiết kế tối giản, logo thêu tỉ mỉ, phù hợp cả đi làm lẫn đi chơi.",
        ],
        "closing": [
            "Màu lên chuẩn sau giặt, chống phai. Sản xuất tại Việt Nam, kiểm định chất lượng trước khi đóng gói.",
            "Phù hợp nhiều dáng người từ 55-80kg. Đã qua kiểm tra co giãn và độ bền màu trước khi xuất xưởng.",
            "Thiết kế localwear gọn gàng, dễ kết hợp cùng phụ kiện như nón bucket, túi đeo chéo. Hàng may sẵn, giao nhanh toàn quốc.",
        ],
    },
    "quan": {
        "opening": [
            "Vải denim 13oz đứng form, không bai rũ sau thời gian dài mặc. Đường may đôi chắc chắn, túi bố trí tiện dụng.",
            "Chất vải twill pha spandex co giãn nhẹ, thoải mái khi ngồi lâu hay đi lại. Cạp cao tôn dáng, ống đứng dễ phối giày.",
            "Denim wash nhẹ màu tự nhiên, lên màu chuẩn từng mùa. Form baggy rộng vừa phải, không quá luộm thuộm.",
        ],
        "closing": [
            "Khóa kéo YKK trơn tru, đinh tán chắc chắn. Sản xuất tại xưởng đối tác lâu năm tại Việt Nam.",
            "Giặt nước lạnh giúp giữ màu lâu hơn. Kèm hướng dẫn bảo quản chi tiết trong từng đơn hàng.",
            "Phù hợp phối cùng áo thun, hoodie hoặc sơ mi oversize. Hàng có sẵn, đổi size miễn phí trong 7 ngày.",
        ],
    },
    "phu-kien": {
        "opening": [
            "Chất liệu chính hãng cao cấp, chi tiết gia công tỉ mỉ, nhẹ và bền theo thời gian sử dụng.",
            "Thiết kế tối giản theo phong cách localwear, dễ dàng kết hợp với nhiều bộ trang phục khác nhau.",
            "Chất liệu thân thiện, chống nước nhẹ, phù hợp sử dụng hằng ngày trong mọi thời tiết.",
        ],
        "closing": [
            "Đóng gói hộp cứng sang trọng, phù hợp làm quà tặng. Bảo hành 6 tháng lỗi kỹ thuật.",
            "Kiểm tra kỹ trước khi giao, kèm phiếu bảo hành. Đổi trả trong 7 ngày nếu lỗi từ nhà sản xuất.",
            "Sản xuất giới hạn theo lô, số lượng có hạn. Đặt trước để chắc chắn có hàng.",
        ],
    },
}

DEFAULT_OPENING = [
    "Sản phẩm được chọn lọc kỹ về chất liệu và form dáng, đúng tinh thần localwear gọn - dễ mặc - đủ điểm nhấn.",
]
DEFAULT_CLOSING = [
    "Kiểm tra chất lượng trước khi giao, hỗ trợ đổi trả trong 7 ngày.",
]


class Command(BaseCommand):
    help = "Điền mô tả riêng cho từng sản phẩm còn thiếu mô tả."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force", action="store_true", help="Ghi đè cả sản phẩm đã có mô tả."
        )

    def handle(self, *args, **options):
        qs = (
            Product.objects.all()
            if options["force"]
            else Product.objects.filter(description__exact="")
        )
        updated = 0
        for product in qs:
            tpl = TEMPLATES.get(product.category.slug, None)
            if tpl:
                opening = tpl["opening"][product.id % len(tpl["opening"])]
                closing = tpl["closing"][product.id % len(tpl["closing"])]
            else:
                opening = DEFAULT_OPENING[0]
                closing = DEFAULT_CLOSING[0]
            product.description = (
                f"{opening}\n\n"
                f"{closing}\n\n"
                f"HUUGIAU Atelier · Streetwear local — thiết kế và sản xuất tại Việt Nam."
            )
            product.save(update_fields=["description", "updated"])
            updated += 1
        self.stdout.write(self.style.SUCCESS(f"Đã điền mô tả cho {updated} sản phẩm."))
