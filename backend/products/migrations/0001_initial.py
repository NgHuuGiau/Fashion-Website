
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='TĂªn danh má»¥c')),
                ('slug', models.SlugField(unique=True)),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='TĂªn sáº£n pháº©m')),
                ('slug', models.SlugField(max_length=200)),
                ('image', models.ImageField(blank=True, upload_to='products/%Y/%m/%d', verbose_name='áº¢nh sáº£n pháº©m')),
                ('description', models.TextField(blank=True, verbose_name='MĂ´ táº£')),
                ('price', models.DecimalField(decimal_places=0, max_digits=10, verbose_name='GiĂ¡ tiá»n')),
                ('stock', models.IntegerField(default=0, verbose_name='Sá»‘ lÆ°á»£ng kho')),
                ('available', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='products.category')),
            ],
            options={
                'ordering': ('-created',),
            },
        ),
    ]
