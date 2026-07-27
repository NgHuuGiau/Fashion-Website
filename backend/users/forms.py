import re

from django import forms
from django.contrib.auth.models import User

from .models import UserProfile


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
        widget=forms.TextInput(
            attrs={
                "oninput": "this.value = this.value.replace(/[^0-9]/g, '')",
                "inputmode": "numeric",
            }
        ),
    )
    password1 = forms.CharField(
        label="Mật khẩu",
        widget=forms.PasswordInput,
        help_text=(
            "Mật khẩu phải đáp ứng các yêu cầu sau:"
            "<ul class='password-requirements'>"
            "<li>Ít nhất 8 ký tự</li>"
            "<li>Có ít nhất 1 chữ in hoa (A-Z)</li>"
            "<li>Có ít nhất 1 chữ số (0-9)</li>"
            "<li>Có ít nhất 1 ký tự đặc biệt (!@#$%^&*...)</li>"
            "</ul>"
        ),
    )
    password2 = forms.CharField(label="Nhập lại mật khẩu", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")
        labels = {
            "username": "Tên đăng nhập",
            "first_name": "Họ",
            "last_name": "Tên",
            "email": "Email",
        }

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Tên đăng nhập đã tồn tại.")
        return username

    def clean_phone_number(self):
        phone = (self.cleaned_data.get("phone_number") or "").strip()
        if not phone:
            return ""

        if not re.fullmatch(r"[0-9]{9,15}", phone):
            raise forms.ValidationError("Số điện thoại không hợp lệ. Chỉ gồm ký tự số từ 9 đến 15 số.")
        return phone

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

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Mật khẩu nhập lại không khớp.")
        return cleaned_data

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


class ProfileForm(forms.Form):
    first_name = forms.CharField(label="Họ", max_length=150, required=False)
    last_name = forms.CharField(label="Tên", max_length=150, required=False)
    email = forms.EmailField(label="Email", required=False)
    phone_number = forms.CharField(
        label="Số điện thoại",
        required=False,
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "oninput": "this.value = this.value.replace(/[^0-9]/g, '')",
                "inputmode": "numeric",
            }
        ),
    )

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        kwargs.setdefault("initial", {})
        if user is not None:
            kwargs["initial"].setdefault("first_name", user.first_name)
            kwargs["initial"].setdefault("last_name", user.last_name)
            kwargs["initial"].setdefault("email", user.email)
            kwargs["initial"].setdefault("phone_number", getattr(getattr(user, "profile", None), "phone_number", ""))
        super().__init__(*args, **kwargs)

    def clean_phone_number(self):
        phone = (self.cleaned_data.get("phone_number") or "").strip()
        if not phone:
            return ""
        if not re.fullmatch(r"[0-9]{9,15}", phone):
            raise forms.ValidationError("Số điện thoại không hợp lệ. Chỉ gồm 9 đến 15 chữ số.")
        return phone

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def save(self):
        if self.user is None:
            raise ValueError("ProfileForm requires a user instance.")

        user = self.user
        user.first_name = (self.cleaned_data.get("first_name") or "").strip()
        user.last_name = (self.cleaned_data.get("last_name") or "").strip()
        user.email = (self.cleaned_data.get("email") or "").strip()
        user.save(update_fields=["first_name", "last_name", "email"])

        UserProfile.objects.update_or_create(
            user=user,
            defaults={"phone_number": (self.cleaned_data.get("phone_number") or "").strip()},
        )
        return user
