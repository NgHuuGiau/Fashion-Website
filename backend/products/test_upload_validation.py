from io import BytesIO

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase
from PIL import Image

from .validators import validate_product_image


class ProductUploadValidationTests(SimpleTestCase):
    def _image(self, name="look.webp", image_format="WEBP"):
        stream = BytesIO()
        Image.new("RGB", (2, 2), "#d15b32").save(stream, format=image_format)
        return SimpleUploadedFile(name, stream.getvalue(), content_type="image/webp")

    def test_accepts_valid_webp(self):
        validate_product_image(self._image())

    def test_rejects_executable_extension(self):
        with self.assertRaises(ValidationError):
            validate_product_image(self._image("look.exe"))

    def test_rejects_oversized_file(self):
        upload = SimpleUploadedFile("look.jpg", b"x" * (5 * 1024 * 1024 + 1))
        with self.assertRaises(ValidationError):
            validate_product_image(upload)
