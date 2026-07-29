import logging
import os

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

logger = logging.getLogger(__name__)

from .activity import log_activity
from .forms import ProfileForm, RegisterForm
from .models import UserProfile
from core.ratelimit import rate_limit


def _sync_visitor_auth_state(request, user):
    visitor = getattr(request, "visitor_session", None)
    if not visitor:
        return
    visitor.user = user
    visitor.is_authenticated = bool(user)
    visitor.save(update_fields=["user", "is_authenticated", "last_seen"])


def _build_login_candidates(identifier):
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
def register_view(request):
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
def login_view(request):
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


def social_login_view(request, provider):
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
def logout_view(request):
    log_activity(request, event_type="logout", metadata={"username": request.user.username})
    _sync_visitor_auth_state(request, None)
    logout(request)
    messages.info(request, "Bạn đã đăng xuất.")
    return redirect("products:product_list")


@login_required
def profile_view(request):
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

    return render(
        request,
        "account/profile.html",
        {
            "form": form,
            "profile": profile,
            "display_name": display_name,
            "display_initials": display_initials,
        },
    )
