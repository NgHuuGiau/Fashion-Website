import re

from django import forms

from .constants import BANK_CHOICES


class CheckoutForm(forms.Form):
    customer_name = forms.CharField(max_length=150, label="Họ và tên")
    customer_email = forms.EmailField(required=False, label="Email")
    phone = forms.CharField(
        max_length=20,
        label="Số điện thoại",
        widget=forms.TextInput(
            attrs={
                "oninput": "this.value = this.value.replace(/[^0-9]/g, '')",
                "inputmode": "numeric",
            }
        ),
    )
    shipping_address = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 4}),
        label="Địa chỉ nhận hàng",
    )
    payment_method = forms.ChoiceField(
        choices=[
            ("cod", "Thanh toán tiền mặt khi nhận hàng"),
            ("bank", "Chuyển khoản ngân hàng"),
        ],
        label="Phương thức thanh toán",
    )
    bank_code = forms.ChoiceField(
        choices=BANK_CHOICES,
        required=False,
        label="Ngân hàng chuyển khoản",
    )
    coupon_code = forms.CharField(
        required=False,
        max_length=30,
        label="Mã giảm giá",
        help_text="Ví dụ: GIAM10, FREESHIP",
    )
    note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        label="Ghi chú",
    )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("payment_method") == "bank" and not cleaned_data.get("bank_code"):
            self.add_error("bank_code", "Vui lòng chọn ngân hàng để quét mã chuyển khoản.")

        if cleaned_data.get("coupon_code"):
            cleaned_data["coupon_code"] = cleaned_data["coupon_code"].strip().upper()

        return cleaned_data

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        if phone and not re.fullmatch(r"[0-9]{9,15}", phone):
            raise forms.ValidationError("Số điện thoại không hợp lệ, vui lòng chỉ nhập từ 9 đến 15 chữ số.")
        return phone
