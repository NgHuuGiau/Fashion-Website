from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from .activity import log_activity
from .forms import RegisterForm
from .models import UserProfile


def _sync_visitor_auth_state(request, user):
    visitor = getattr(request, "visitor_session", None)
    if not visitor:
        return
    visitor.user = user
    visitor.is_authenticated = bool(user)
    visitor.save(update_fields=["user", "is_authenticated", "last_seen"])


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


def login_view(request):
    if request.user.is_authenticated:
        return redirect("products:product_list")

    if request.method == "POST":
        identifier = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        login_candidates = [identifier] if identifier else []

        if identifier:
            matched_usernames = list(
                User.objects.filter(email__iexact=identifier).values_list("username", flat=True)[:5]
            )
            matched_usernames.extend(
                UserProfile.objects.filter(phone_number=identifier).values_list("user__username", flat=True)[:5]
            )
            for candidate in matched_usernames:
                if candidate and candidate not in login_candidates:
                    login_candidates.append(candidate)

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
            return redirect(next_url)

        messages.error(request, "Sai tên đăng nhập, email, số điện thoại hoặc mật khẩu.")

    return render(request, "auth/login.html")


@login_required
def logout_view(request):
    log_activity(request, event_type="logout", metadata={"username": request.user.username})
    _sync_visitor_auth_state(request, None)
    logout(request)
    messages.info(request, "Bạn đã đăng xuất.")
    return redirect("products:product_list")


@login_required
def profile_view(request):
    return render(request, "account/profile.html")
