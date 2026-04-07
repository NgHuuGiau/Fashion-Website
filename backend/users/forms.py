import re

from django import forms
from django.contrib.auth.models import User

from .models import UserProfile



# ----------------------------------
# | KHỐI LỚP (CLASS): REGISTERFORM |
# ----------------------------------
class RegisterForm(forms.ModelForm):
    username = forms.CharField(
        label="Tên đăng nhập",
        max_length=150,
        help_text="",
    )
    phone_number = forms.CharField(
        label="Số điện thoại",
        required=False,
        max_length=20,
        help_text="Nhập email hoặc số điện thoại (ít nhất 1 mục).",
        widget=forms.TextInput(attrs={
            "oninput": "this.value = this.value.replace(/[^0-9]/g, '')",
            "inputmode": "numeric"
        }),
    )
    password1 = forms.CharField(
        label="Mật khẩu",
        widget=forms.PasswordInput,
        help_text=(
            "Mật khẩu phải đáp ứng các yêu cầu sau:"
            "<ul class='password-requirements'>"
            "<li>Ít nhất 8 ký tự</li>"
            "<li>Có ít nhất 1 chữ in hoa (A–Z)</li>"
            "<li>Có ít nhất 1 chữ số (0–9)</li>"
            "<li>Có ít nhất 1 ký tự đặc biệt (!@#$%^&*...)</li>"
            "</ul>"
        ),
    )
    password2 = forms.CharField(label="Nhập lại mật khẩu", widget=forms.PasswordInput)


    # --------------------------
    # | KHỐI LỚP (CLASS): META |
    # --------------------------
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")
        labels = {
            "username": "Tên đăng nhập",
            "first_name": "Họ",
            "last_name": "Tên",
            "email": "Email",
        }


    # ----------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): CLEAN_USERNAME |
    # ----------------------------------------
    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Tên đăng nhập đã tồn tại.")
        return username


    # --------------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): CLEAN_PHONE_NUMBER |
    # --------------------------------------------
    def clean_phone_number(self):
        phone = (self.cleaned_data.get("phone_number") or "").strip()
        if not phone:
            return ""

        if not re.fullmatch(r"[0-9]{9,15}", phone):
            raise forms.ValidationError("Số điện thoại không hợp lệ. Chỉ gồm ký tự số (9-15 số).")
        return phone


    # -----------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): CLEAN_PASSWORD1 |
    # -----------------------------------------
    def clean_password1(self):
        password = self.cleaned_data.get("password1", "")

        if len(password) < 8:
            raise forms.ValidationError("Mật khẩu phải có ít nhất 8 ký tự.")
        if not any(ch.isupper() for ch in password):
            raise forms.ValidationError("Mật khẩu phải có ít nhất 1 chữ in hoa.")
        if not any(ch.isdigit() for ch in password):
            raise forms.ValidationError("Mật khẩu phải có ít nhất 1 chữ số.")
        if not any(not ch.isalnum() for ch in password):
            raise forms.ValidationError("Mật khẩu phải có ít nhất 1 ký tự đặc biệt (!@#$%^&*...).")

        return password


    # -------------------------------
    # | HÀM XỬ LÝ (FUNCTION): CLEAN |
    # -------------------------------
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        email = (cleaned_data.get("email") or "").strip()
        phone_number = (cleaned_data.get("phone_number") or "").strip()

        if not email and not phone_number:
            msg = "Cần nhập ít nhất Email hoặc Số điện thoại."
            self.add_error("email", msg)
            self.add_error("phone_number", msg)

        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Mật khẩu nhập lại không khớp.")
        return cleaned_data


    # ------------------------------
    # | HÀM XỬ LÝ (FUNCTION): SAVE |
    # ------------------------------
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = (self.cleaned_data.get("email") or "").strip()
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            UserProfile.objects.update_or_create(
                user=user,
                defaults={"phone_number": self.cleaned_data.get("phone_number", "").strip()},
            )
        return user
