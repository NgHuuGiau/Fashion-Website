from django import forms



# ----------------------------------
# | KHỐI LỚP (CLASS): CHECKOUTFORM |
# ----------------------------------
class CheckoutForm(forms.Form):
    BANK_CHOICES = [
        ("", "-- Chọn ngân hàng --"),
        ("VCB", "Vietcombank"),
        ("TCB", "Techcombank"),
        ("MB", "MBBank"),
        ("ACB", "ACB"),
        ("BIDV", "BIDV"),
        ("VPB", "VPBank"),
    ]

    customer_name = forms.CharField(max_length=150, label="Họ và tên")
    customer_email = forms.EmailField(required=False, label="Email")
    phone = forms.CharField(
        max_length=20, 
        label="Số điện thoại",
        widget=forms.TextInput(attrs={
            "oninput": "this.value = this.value.replace(/[^0-9]/g, '')",
            "inputmode": "numeric"
        })
    )
    shipping_address = forms.CharField(widget=forms.Textarea(attrs={"rows": 4}), label="Địa chỉ nhận hàng")
    payment_method = forms.ChoiceField(
        choices=[
            ("cod", "Tiền mặt khi nhận hàng"),
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


    # -------------------------------
    # | HÀM XỬ LÝ (FUNCTION): CLEAN |
    # -------------------------------
    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get("payment_method")
        bank_code = cleaned_data.get("bank_code")

        if payment_method == "bank" and not bank_code:
            self.add_error("bank_code", "Vui lòng chọn ngân hàng để quét mã chuyển khoản.")

        if cleaned_data.get("coupon_code"):
            cleaned_data["coupon_code"] = cleaned_data["coupon_code"].strip().upper()

        return cleaned_data


    # -------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): CLEAN_PHONE |
    # -------------------------------------
    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        if phone:
            import re
            if not re.fullmatch(r"[0-9]{9,15}", phone):
                raise forms.ValidationError("Số điện thoại không hợp lệ, vui lòng chỉ nhập số (từ 9 đến 15 chữ số).")
        return phone
