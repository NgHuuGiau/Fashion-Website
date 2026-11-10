from django.db import migrations, models

import products.validators


class Migration(migrations.Migration):
    dependencies = [("products", "0020_product_product_stock_non_negative_and_more")]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="image",
            field=models.ImageField(
                blank=True,
                upload_to="products/%Y/%m/%d",
                validators=[products.validators.validate_product_image],
                verbose_name="Ảnh sản phẩm",
            ),
        ),
        migrations.AlterField(
            model_name="productimage",
            name="image",
            field=models.ImageField(
                upload_to="products/gallery/%Y/%m/%d",
                validators=[products.validators.validate_product_image],
                verbose_name="Ảnh gallery",
            ),
        ),
        migrations.AlterField(
            model_name="review",
            name="image",
            field=models.ImageField(
                blank=True,
                upload_to="reviews/%Y/%m/%d",
                validators=[products.validators.validate_product_image],
                verbose_name="Ảnh kèm đánh giá",
            ),
        ),
    ]
