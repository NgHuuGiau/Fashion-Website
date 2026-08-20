from django.db import migrations


FIXES = {
    10: (
        "Phí ship thế nào?",
        "Shop freeship toàn quốc cho đơn từ 499K. Bạn có thể thêm sản phẩm vào giỏ để xem phí ship trước khi đặt.",
    ),
    20: (
        "Có thanh toán chuyển khoản không?",
        "Shop hỗ trợ COD và chuyển khoản ngân hàng. Bạn có thể chọn ở bước checkout.",
    ),
    30: (
        "Làm sao theo dõi đơn?",
        "Nếu đã đăng nhập, bạn vào mục Đơn hàng để xem trạng thái. Sau khi đặt xong, web cũng hiển thị xác nhận ngay.",
    ),
    40: (
        "Tư vấn size",
        "Bạn gửi chiều cao, cân nặng và kiểu mặc mong muốn để shop gợi ý size nhanh hơn.",
    ),
    50: (
        "Đổi trả như thế nào?",
        "Nếu cần đổi trả, bạn liên hệ sớm sau khi nhận hàng và gửi kèm mã đơn để shop hỗ trợ nhanh.",
    ),
}


def repair_faq_text(apps, schema_editor):
    SupportFAQ = apps.get_model("products", "SupportFAQ")
    old_questions = {
        10: "Phi ship the nao?",
        20: "Co thanh toan chuyen khoan khong?",
        30: "Lam sao theo doi don?",
        40: "Tu van size",
        50: "Doi tra nhu the nao?",
    }
    for priority in FIXES:
        new_question, new_answer = FIXES[priority]
        SupportFAQ.objects.filter(
            priority=priority, question=old_questions[priority]
        ).update(question=new_question, answer=new_answer)


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0011_review"),
    ]

    operations = [
        migrations.RunPython(repair_faq_text, migrations.RunPython.noop),
    ]
