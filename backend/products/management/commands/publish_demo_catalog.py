"""Bật một phần catalog demo (tồn kho + biến thể) để test giao diện như shop thật."""

from django.core.management.base import BaseCommand

from core.demo_data import refuse_demo_seed_in_production
from products.models import Product, ProductVariant

SIZES = {
    "ao": ["S", "M", "L"],
    "quan": ["29", "30", "31"],
    "phu-kien": ["F"],
}


class Command(BaseCommand):
    help = "Publish N sản phẩm đầu tiên: available=True, tồn kho và biến thể."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=24)
        parser.add_argument("--stock", type=int, default=20)

    def handle(self, *args, **options):
        refuse_demo_seed_in_production()
        count = options["count"]
        stock = options["stock"]

        products = list(Product.objects.order_by("id")[:count])
        if not products:
            raise SystemExit("Chưa có sản phẩm. Chạy: python manage.py seed_all")

        for index, product in enumerate(products):
            category_slug = product.category.slug if product.category else ""
            sizes = SIZES.get(category_slug, SIZES["ao"])
            for size in sizes:
                ProductVariant.objects.update_or_create(
                    product=product,
                    color_name="Đen",
                    size=size,
                    defaults={"stock": stock, "is_active": True},
                )
            total = stock * len(sizes)
            product.stock = total
            product.available = True
            product.featured = index < 4
            product.save(update_fields=["stock", "available", "featured"])

        self.stdout.write(
            self.style.SUCCESS(
                f"Đã publish {len(products)} sản phẩm, {stock}/size. "
                "Ảnh: chạy thêm `manage.py seed_demo_photos` nếu còn trống."
            )
        )
