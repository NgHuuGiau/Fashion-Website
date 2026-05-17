
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_alter_category_options_product_featured_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductVariant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color_name', models.CharField(max_length=50, verbose_name='MĂ u sáº¯c')),
                ('color_code', models.CharField(default='#111111', max_length=20, verbose_name='MĂ£ mĂ u')),
                ('size', models.CharField(max_length=20, verbose_name='Size')),
                ('stock', models.PositiveIntegerField(default=0, verbose_name='Tá»“n kho')),
                ('is_active', models.BooleanField(default=True, verbose_name='Hiá»ƒn thá»‹')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variants', to='products.product')),
            ],
            options={
                'ordering': ['color_name', 'size'],
                'unique_together': {('product', 'color_name', 'size')},
            },
        ),
    ]
