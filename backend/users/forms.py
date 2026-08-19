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
    birthday = forms.DateField(
        label="Ngày sinh",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
        help_text="Để trống nếu không muốn nhận ưu đãi sinh nhật. Bạn có thể nhận mã giảm 20% vào đúng tháng sinh nhật.",
    )

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        kwargs.setdefault("initial", {})
        if user is not None:
            kwargs["initial"].setdefault("first_name", user.first_name)
            kwargs["initial"].setdefault("last_name", user.last_name)
            kwargs["initial"].setdefault("email", user.email)
            kwargs["initial"].setdefault("phone_number", getattr(getattr(user, "profile", None), "phone_number", ""))
            kwargs["initial"].setdefault("birthday", getattr(getattr(user, "profile", None), "birthday", None))
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
            defaults={
                "phone_number": (self.cleaned_data.get("phone_number") or "").strip(),
                "birthday": self.cleaned_data.get("birthday") or None,
            },
        )
        return user


class ForgotPasswordForm(forms.Form):
    identifier = forms.CharField(
        label="Tài khoản / Email / Số điện thoại",
        max_length=150,
        widget=forms.TextInput(attrs={"placeholder": "Nhập tên đăng nhập, email hoặc số điện thoại"}),
        help_text="Hệ thống sẽ kiểm tra tài khoản có tồn tại không.",
    )

    def clean_identifier(self):
        identifier = self.cleaned_data["identifier"].strip()
        from django.contrib.auth.models import User
        from .models import UserProfile
        matched = (
            User.objects.filter(username__iexact=identifier).exists()
            or User.objects.filter(email__iexact=identifier).exists()
            or UserProfile.objects.filter(phone_number=identifier).exists()
        )
        if not matched:
            raise forms.ValidationError("Không tìm thấy tài khoản với thông tin này.")
        self.cleaned_data["_matched_user"] = self._find_user(identifier)
        return identifier

    def _find_user(self, identifier):
        from django.contrib.auth.models import User
        from .models import UserProfile
        user = User.objects.filter(username__iexact=identifier).first()
        if user:
            return user
        user = User.objects.filter(email__iexact=identifier).first()
        if user:
            return user
        profile = UserProfile.objects.filter(phone_number=identifier).first()
        if profile:
            return profile.user
        return None


class CaptchaForm(forms.Form):
    captcha = forms.CharField(
        label="Mã xác thực",
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            "placeholder": "Nhập 6 ký tự",
            "style": "text-transform: uppercase; letter-spacing: 0.3em;",
            "autocomplete": "off",
        }),
        help_text="Nhập đúng mã trong hình (không phân biệt chữ hoa/thường).",
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    def clean_captcha(self):
        value = self.cleaned_data["captcha"].strip().upper()
        expected = self.request.session.get("captcha_code", "").upper() if self.request else ""
        if not expected or value != expected:
            raise forms.ValidationError("Mã xác thực không đúng. Vui lòng thử lại.")
        return value


class ResetPasswordForm(forms.Form):
    password1 = forms.CharField(
        label="Mật khẩu mới",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text="Ít nhất 8 ký tự, có chữ hoa, chữ số, ký tự đặc biệt.",
    )
    password2 = forms.CharField(label="Nhập lại mật khẩu mới", widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}))

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


class ChangePasswordForm(forms.Form):
    """Đổi mật khẩu khi đã đăng nhập (trong hồ sơ)."""

    current_password = forms.CharField(
        label="Mật khẩu hiện tại",
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password", "placeholder": "Nhập mật khẩu hiện tại"}),
    )
    new_password1 = forms.CharField(
        label="Mật khẩu mới",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", "placeholder": "Nhập mật khẩu mới"}),
        help_text="Ít nhất 8 ký tự, có chữ hoa, chữ số, ký tự đặc biệt.",
    )
    new_password2 = forms.CharField(
        label="Nhập lại mật khẩu mới",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", "placeholder": "Nhập lại mật khẩu mới"}),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        value = self.cleaned_data.get("current_password", "")
        if self.user is not None and not self.user.check_password(value):
            raise forms.ValidationError("Mật khẩu hiện tại không đúng.")
        return value

    def clean_new_password1(self):
        password = self.cleaned_data.get("new_password1", "")
        if len(password) < 8:
            raise forms.ValidationError("Mật khẩu phải có ít nhất 8 ký tự.")
        if not any(ch.isupper() for ch in password):
            raise forms.ValidationError("Mật khẩu phải có ít nhất 1 chữ in hoa.")
        if not any(ch.isdigit() for ch in password):
            raise forms.ValidationError("Mật khẩu phải có ít nhất 1 chữ số.")
        if not any(not ch.isalnum() for ch in password):
            raise forms.ValidationError("Mật khẩu phải có ít nhất 1 ký tự đặc biệt (!@#$%^&*...).")
        if self.user is not None and self.user.check_password(password):
            raise forms.ValidationError("Mật khẩu mới không được trùng với mật khẩu hiện tại.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")
        if password1 and password2 and password1 != password2:
            self.add_error("new_password2", "Mật khẩu nhập lại không khớp.")
        return cleaned_data

    def save(self):
        self.user.set_password(self.cleaned_data["new_password1"])
        self.user.save(update_fields=["password"])
        return self.user
