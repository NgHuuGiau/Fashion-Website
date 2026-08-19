import logging
import os

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils import timezone
from django.views.decorators.http import require_POST

from .activity import log_activity
from .captcha import generate_captcha_code, generate_captcha_image
from .forms import ForgotPasswordForm, CaptchaForm, ResetPasswordForm, ProfileForm, RegisterForm, ChangePasswordForm
from .models import UserAddress, UserProfile
from core.ratelimit import rate_limit

logger = logging.getLogger(__name__)


def _sync_visitor_auth_state(request: HttpRequest, user) -> None:
    visitor = getattr(request, "visitor_session", None)
    if not visitor:
        return
    visitor.user = user
    visitor.is_authenticated = bool(user)
    visitor.save(update_fields=["user", "is_authenticated", "last_seen"])


def _build_login_candidates(identifier: str) -> list:
    if not identifier:
        return []

    login_candidates = [identifier]
    matched_usernames = list(User.objects.filter(email__iexact=identifier).values_list("username", flat=True)[:5])
    matched_usernames.extend(
        UserProfile.objects.filter(phone_number=identifier).values_list("user__username", flat=True)[:5]
    )
    for candidate in matched_usernames:
        if candidate and candidate not in login_candidates:
            login_candidates.append(candidate)
    return login_candidates


@rate_limit("register", max_requests=5, window=300, error_msg="Bạn đã đăng ký quá nhiều lần. Vui lòng thử lại sau 5 phút.")
def register_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("products:product_list")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            _sync_visitor_auth_state(request, user)
            log_activity(
                request,
                event_type="register",
                metadata={
                    "username": user.username,
                    "email": user.email,
                    "phone_number": getattr(user.profile, "phone_number", ""),
                },
                status_code=201,
            )
            messages.success(request, "Tạo tài khoản thành công.")
            return redirect("products:product_list")
    else:
        form = RegisterForm()

    return render(request, "auth/register.html", {"form": form})


@rate_limit("login", max_requests=10, window=300, error_msg="Quá nhiều lần đăng nhập. Vui lòng thử lại sau 5 phút.")
def login_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("products:product_list")

    if request.method == "POST":
        identifier = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        login_candidates = _build_login_candidates(identifier)

        user = None
        for candidate in login_candidates:
            user = authenticate(request, username=candidate, password=password)
            if user is not None:
                break

        if user is not None:
            login(request, user)
            _sync_visitor_auth_state(request, user)
            log_activity(request, event_type="login", metadata={"username": user.username})
            messages.success(request, "Đăng nhập thành công.")
            next_url = request.GET.get("next") or request.POST.get("next") or "products:product_list"
            if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                next_url = reverse("products:product_list")
            return redirect(next_url)

        logger.warning(
            "Failed login attempt. identifier=%s ip=%s",
            identifier[:20] if identifier else "(empty)",
            request.META.get("REMOTE_ADDR"),
        )
        messages.error(request, "Sai tên đăng nhập, email, số điện thoại hoặc mật khẩu.")

    return render(request, "auth/login.html")


SOCIAL_LOGIN_PROVIDERS = {
    "google": "GOOGLE_OAUTH_URL",
    "facebook": "FACEBOOK_OAUTH_URL",
    "apple": "APPLE_OAUTH_URL",
}


def social_login_view(request: HttpRequest, provider: str) -> HttpResponse:
    provider_key = (provider or "").strip().lower()
    if provider_key not in SOCIAL_LOGIN_PROVIDERS:
        messages.error(request, "Phương thức đăng nhập không hợp lệ.")
        return redirect("users:login")

    login_url = os.getenv(SOCIAL_LOGIN_PROVIDERS[provider_key], "").strip()
    if not login_url:
        messages.info(request, f"Đăng nhập {provider_key} chưa được bật trong cấu hình.")
        fallback = request.GET.get("next") or ""
        if not url_has_allowed_host_and_scheme(fallback, allowed_hosts={request.get_host()}):
            fallback = reverse("users:login")
        return redirect(fallback)

    next_url = request.GET.get("next") or request.POST.get("next") or ""
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        joiner = "&" if "?" in login_url else "?"
        login_url = f"{login_url}{joiner}next={next_url}"
    return redirect(login_url)


@login_required
def logout_view(request: HttpRequest) -> HttpResponse:
    log_activity(request, event_type="logout", metadata={"username": request.user.username})
    _sync_visitor_auth_state(request, None)
    logout(request)
    messages.info(request, "Bạn đã đăng xuất.")
    return redirect("products:product_list")


@login_required
def profile_view(request: HttpRequest) -> HttpResponse:
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    display_name = (request.user.get_full_name() or request.user.username).strip() or request.user.username
    name_parts = [part for part in display_name.split() if part]
    display_initials = "".join(part[0] for part in name_parts[:2]).upper() if name_parts else request.user.username[:2].upper()

    if request.method == "POST":
        form = ProfileForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Đã lưu thông tin tài khoản.")
            return redirect("users:profile")
    else:
        form = ProfileForm(user=request.user)

    addresses = list(UserAddress.objects.filter(user=request.user))
    hbd_active = bool(profile.birthday and profile.is_birthday_month())
    expiry_warning = (
        profile.points_expire_at
        and profile.points > 0
        and profile.points_expire_at
        and profile.points_expire_at >= timezone.localdate()
    )

    return render(
        request,
        "account/profile.html",
        {
            "form": form,
            "profile": profile,
            "display_name": display_name,
            "display_initials": display_initials,
            "addresses": addresses,
            "hbd_active": hbd_active,
            "expiry_warning": expiry_warning,
        },
    )


@login_required
@require_POST
def address_add(request: HttpRequest) -> HttpResponse:
    recipient_name = (request.POST.get("recipient_name") or "").strip()
    phone = (request.POST.get("phone") or "").strip()
    address = (request.POST.get("address") or "").strip()
    label = (request.POST.get("label") or "").strip()[:40]
    is_default = request.POST.get("is_default") == "on"

    if not recipient_name or not phone or not address:
        messages.error(request, "Vui lòng điền đầy đủ tên người nhận, số điện thoại và địa chỉ.")
        return redirect("users:profile")

    if not UserAddress.objects.filter(user=request.user).exists():
        is_default = True
    UserAddress.objects.create(
        user=request.user,
        label=label,
        recipient_name=recipient_name,
        phone=phone,
        address=address,
        is_default=is_default,
    )
    messages.success(request, "Đã lưu địa chỉ giao hàng.")
    return redirect("users:profile")


@login_required
@require_POST
def address_delete(request: HttpRequest, address_id) -> HttpResponse:
    address = get_object_or_404(UserAddress, id=address_id, user=request.user)
    address.delete()
    messages.success(request, "Đã xóa địa chỉ.")
    return redirect("users:profile")


@login_required
@require_POST
def address_set_default(request: HttpRequest, address_id) -> HttpResponse:
    address = get_object_or_404(UserAddress, id=address_id, user=request.user)
    UserAddress.objects.filter(user=request.user, is_default=True).update(is_default=False)
    address.is_default = True
    address.save(update_fields=["is_default"])
    messages.success(request, "Đã đặt địa chỉ mặc định.")
    return redirect("users:profile")


@login_required
def change_password_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)
            log_activity(request, event_type="change_password", metadata={"username": request.user.username})
            messages.success(request, "Đổi mật khẩu thành công.")
            return redirect("users:profile")
    else:
        form = ChangePasswordForm(user=request.user)

    return render(request, "account/change_password.html", {"password_form": form})


@rate_limit("forgot_password", max_requests=50, window=300, error_msg="Quá nhiều yêu cầu. Vui lòng thử lại sau 5 phút.")
def forgot_password_view(request: HttpRequest) -> HttpResponse:
    """Bước 1: Nhập tài khoản (username/email/phone) để kiểm tra tồn tại."""
    if request.user.is_authenticated:
        return redirect("products:product_list")

    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data["_matched_user"]
            request.session["reset_user_id"] = user.id
            return redirect("users:forgot_password_captcha")
    else:
        form = ForgotPasswordForm()

    return render(request, "auth/forgot_password.html", {"form": form})


def captcha_image_view(request: HttpRequest) -> HttpResponse:
    """Trả về ảnh CAPTCHA PNG."""
    code = generate_captcha_code()
    request.session["captcha_code"] = code
    img_data = generate_captcha_image(code)
    return HttpResponse(img_data, content_type="image/png")


@rate_limit("forgot_password_captcha", max_requests=50, window=300, error_msg="Quá nhiều lần thử. Vui lòng thử lại sau 5 phút.")
def forgot_password_captcha_view(request: HttpRequest) -> HttpResponse:
    """Bước 2: Xác thực CAPTCHA."""
    if "reset_user_id" not in request.session:
        return redirect("users:forgot_password")

    if request.method == "POST":
        form = CaptchaForm(request.POST)
        form.request = request
        if form.is_valid():
            return redirect("users:reset_password")
    else:
        form = CaptchaForm()

    return render(request, "auth/forgot_password_captcha.html", {"form": form})


@rate_limit("reset_password", max_requests=50, window=300, error_msg="Quá nhiều yêu cầu. Vui lòng thử lại sau 5 phút.")
def reset_password_view(request: HttpRequest) -> HttpResponse:
    """Bước 3: Đặt mật khẩu mới."""
    if "reset_user_id" not in request.session:
        return redirect("users:forgot_password")

    user_id = request.session["reset_user_id"]
    from django.contrib.auth.models import User
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data["password1"])
            user.save(update_fields=["password"])
            # Clear session
            request.session.pop("reset_user_id", None)
            request.session.pop("captcha_code", None)
            messages.success(request, "Đổi mật khẩu thành công. Vui lòng đăng nhập.")
            return redirect("users:login")
    else:
        form = ResetPasswordForm()

    return render(request, "auth/reset_password.html", {"form": form, "username": user.username})
