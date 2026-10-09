from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("orders", "0026_push_sizeguide_reviewmedia")]

    operations = [
        migrations.AddField(
            model_name="order",
            name="shipping_ward_name",
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name="order",
            name="shipping_province_name",
            field=models.CharField(blank=True, max_length=150),
        ),
    ]
