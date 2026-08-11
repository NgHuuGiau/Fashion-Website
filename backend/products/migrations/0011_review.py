import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0010_add_db_indexes_and_composites'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveSmallIntegerField(choices=[(1, '1 sao'), (2, '2 sao'), (3, '3 sao'), (4, '4 sao'), (5, '5 sao')], db_index=True, verbose_name='Số sao')),
                ('comment', models.TextField(blank=True, verbose_name='Nội dung đánh giá')),
                ('is_published', models.BooleanField(db_index=True, default=True, verbose_name='Hiển thị')),
                ('verified_purchase', models.BooleanField(db_index=True, default=False, verbose_name='Đã mua hàng')),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='products.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Đánh giá sản phẩm',
                'verbose_name_plural': 'Đánh giá sản phẩm',
                'ordering': ['-created'],
                'indexes': [models.Index(fields=['product', 'is_published', '-created'], name='products_re_product_491447_idx')],
                'unique_together': {('product', 'user')},
            },
        ),
    ]
