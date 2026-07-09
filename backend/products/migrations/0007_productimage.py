
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_rename_supportfaq_indexes'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='products/gallery/%Y/%m/%d', verbose_name='Ảnh gallery')),
                ('sort_order', models.PositiveSmallIntegerField(default=0, verbose_name='Thứ tự')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gallery_images', to='products.product')),
            ],
            options={
                'verbose_name': 'Ảnh sản phẩm',
                'verbose_name_plural': 'Ảnh sản phẩm',
                'ordering': ['sort_order', 'id'],
            },
        ),
    ]
