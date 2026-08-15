
from django.db import migrations, models


def seed_support_faq(apps, schema_editor):
    SupportFAQ = apps.get_model("products", "SupportFAQ")
    items = [
        {
            "question": "Phí ship thế nào?",
            "keywords": "ship,giao,van chuyen,phi ship,free ship",
            "answer": "Shop freeship toàn quốc cho đơn từ 499K. Bạn có thể thêm sản phẩm vào giỏ để xem phí ship trước khi đặt.",
            "priority": 10,
        },
        {
            "question": "Có thanh toán chuyển khoản không?",
            "keywords": "thanh toan,chuyen khoan,cod,ngan hang",
            "answer": "Shop hỗ trợ COD và chuyển khoản ngân hàng. Bạn có thể chọn ở bước checkout.",
            "priority": 20,
        },
        {
            "question": "Làm sao theo dõi đơn?",
            "keywords": "don,theo doi,trang thai,ma don",
            "answer": "Nếu đã đăng nhập, bạn vào mục Đơn hàng để xem trạng thái. Sau khi đặt xong, web cũng hiển thị xác nhận ngay.",
            "priority": 30,
        },
        {
            "question": "Tư vấn size",
            "keywords": "size,kich co,rong,chat lieu,form",
            "answer": "Bạn gửi chiều cao, cân nặng và kiểu mặc mong muốn để shop gợi ý size nhanh hơn.",
            "priority": 40,
        },
        {
            "question": "Đổi trả như thế nào?",
            "keywords": "doi,tra,hoan,huy",
            "answer": "Nếu cần đổi trả, bạn liên hệ sớm sau khi nhận hàng và gửi kèm mã đơn để shop hỗ trợ nhanh.",
            "priority": 50,
        },
    ]

    for item in items:
        SupportFAQ.objects.get_or_create(question=item["question"], defaults=item)


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0004_wishlistitem"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="wishlistitem",
            options={
                "ordering": ["-created"],
                "verbose_name": "Sản phẩm yêu thích",
                "verbose_name_plural": "Sản phẩm yêu thích",
            },
        ),
        migrations.CreateModel(
            name="SupportFAQ",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("question", models.CharField(max_length=255, verbose_name="Câu hỏi")),
                ("keywords", models.CharField(blank=True, max_length=255, verbose_name="Từ khóa")),
                ("answer", models.TextField(verbose_name="Câu trả lời")),
                ("priority", models.PositiveSmallIntegerField(default=100, verbose_name="Độ ưu tiên")),
                ("is_active", models.BooleanField(default=True, verbose_name="Đang dùng")),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "FAQ hỗ trợ",
                "verbose_name_plural": "FAQ hỗ trợ",
                "ordering": ["priority", "id"],
            },
        ),
        migrations.AddIndex(
            model_name="supportfaq",
            index=models.Index(fields=["is_active", "priority"], name="products_su_is_acti_1d2b34_idx"),
        ),
        migrations.AddIndex(
            model_name="supportfaq",
            index=models.Index(fields=["question"], name="products_su_questio_05f0da_idx"),
        ),
        migrations.RunPython(seed_support_faq, migrations.RunPython.noop),
    ]
