
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['name'], 'verbose_name': 'Danh má»¥c', 'verbose_name_plural': 'Danh má»¥c'},
        ),
        migrations.AddField(
            model_name='product',
            name='featured',
            field=models.BooleanField(default=False, verbose_name='Ná»•i báº­t'),
        ),
        migrations.AddField(
            model_name='product',
            name='image_url',
            field=models.URLField(blank=True, verbose_name='URL áº£nh'),
        ),
        migrations.AlterField(
            model_name='product',
            name='available',
            field=models.BooleanField(default=True, verbose_name='Äang bĂ¡n'),
        ),
        migrations.AlterField(
            model_name='product',
            name='stock',
            field=models.PositiveIntegerField(default=0, verbose_name='Sá»‘ lÆ°á»£ng kho'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['id', 'slug'], name='products_pr_id_a08e3c_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['name'], name='products_pr_name_9ff0a3_idx'),
        ),
    ]
