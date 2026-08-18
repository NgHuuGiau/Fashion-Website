"""Chuyển ảnh sản phẩm upload thành WebP để web tải nhanh hơn.

``python manage.py optimize_images --dry-run`` xem danh sách mà không đổi gì.
Chuyển đổi tại chỗ: đuôi ảnh thành .webp, xóa file gốc, cập nhật đường dẫn
trong DB. Ảnh chưa tồn tại trên đĩa / ảnh URL sẽ được bỏ qua.
"""
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from PIL import Image, ImageOps


def _convert_file(src_path, quality):
    img = Image.open(src_path)
    img = ImageOps.exif_transpose(img)
    target = src_path.with_suffix(".webp")
    kwargs = {"quality": quality, "method": 6}
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        kwargs["lossless"] = True
    else:
        img = img.convert("RGB")
    img.save(target, "WEBP", **kwargs)
    src_path.unlink(missing_ok=True)
    return target


class Command(BaseCommand):
    help = "Nén ảnh sản phẩm thành WebP (giảm ~60-80% dung lượng, giữ chất lượng)."

    def add_arguments(self, parser):
        parser.add_argument("--quality", type=int, default=82, help="Chất lượng WebP (0-100).")
        parser.add_argument("--dry-run", action="store_true", help="Chỉ liệt kê, không đổi gì.")

    @staticmethod
    def _field_files():
        from products.models import Product, ProductImage

        for product in Product.objects.exclude(image="").only("image"):
            yield product, "image", product.image
        for image_obj in ProductImage.objects.exclude(image="").only("image"):
            yield image_obj, "image", image_obj.image

    def handle(self, *args, **options):
        quality = options["quality"]
        dry_run = options["dry_run"]
        media_root = Path(settings.MEDIA_ROOT)

        converted = 0
        errors = []
        for obj, field_name, field in self._field_files():
            relative_name = field.name.replace("\\", "/")
            absolute = (media_root / relative_name).resolve()
            if not absolute.is_file() or absolute.suffix.lower() == ".webp":
                continue
            self.stdout.write("{}{}".format("[DRY] " if dry_run else "", relative_name))
            if dry_run:
                converted += 1
                continue
            try:
                target = _convert_file(absolute, quality)
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{relative_name}: {exc}")
                continue
            target_rel = str(target.relative_to(media_root)).replace("\\", "/")
            setattr(obj, field_name, target_rel)
            obj.save(update_fields=[field_name])
            converted += 1

        self.stdout.write(self.style.SUCCESS(f"\nDone: {converted} file.")
                          if not errors else self.style.SUCCESS(f"Done: {converted} file, {len(errors)} lỗi."))
        for err in errors:
            self.stderr.write(err)