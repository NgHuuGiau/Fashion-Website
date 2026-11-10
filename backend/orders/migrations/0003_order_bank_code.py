from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0002_orderitem_selected_color_orderitem_selected_size_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="bank_code",
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
