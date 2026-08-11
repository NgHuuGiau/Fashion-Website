import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_add_db_indexes_and_composites'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='coupon',
            name='max_uses_per_user',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Giới hạn mỗi người'),
        ),
        migrations.CreateModel(
            name='CouponRedemption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('used_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('coupon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='redemptions', to='orders.coupon')),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='coupon_redemptions', to='orders.order')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='coupon_redemptions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Lượt dùng mã giảm giá',
                'verbose_name_plural': 'Lượt dùng mã giảm giá',
                'ordering': ['-used_at'],
            },
        ),
    ]
