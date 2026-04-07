from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .activity import log_activity
from .forms import RegisterForm



# --------------------------------------------------
# | HÀM XỬ LÝ (FUNCTION): _SYNC_VISITOR_AUTH_STATE |
# --------------------------------------------------
def _sync_visitor_auth_state(request, user):
    visitor = getattr(request, "visitor_session", None)
    if not visitor:
        return
    visitor.user = user
    visitor.is_authenticated = bool(user)
    visitor.save(update_fields=["user", "is_authenticated", "last_seen"])



# ---------------------------------------
# | HÀM XỬ LÝ (FUNCTION): REGISTER_VIEW |
# ---------------------------------------
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



# ------------------------------------
# | HÀM XỬ LÝ (FUNCTION): LOGIN_VIEW |
# ------------------------------------
def login_view(request):
    if request.user.is_authenticated:
        return redirect("products:product_list")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            _sync_visitor_auth_state(request, user)
            log_activity(request, event_type="login", metadata={"username": user.username})
            messages.success(request, "Đăng nhập thành công.")
            next_url = request.GET.get("next") or request.POST.get("next") or "products:product_list"
            return redirect(next_url)

        messages.error(request, "Sai tên đăng nhập hoặc mật khẩu.")

    return render(request, "auth/login.html")


@login_required

# -------------------------------------
# | HÀM XỬ LÝ (FUNCTION): LOGOUT_VIEW |
# -------------------------------------
def logout_view(request):
    log_activity(request, event_type="logout", metadata={"username": request.user.username})
    _sync_visitor_auth_state(request, None)
    logout(request)
    messages.info(request, "Bạn đã đăng xuất.")
    return redirect("products:product_list")


@login_required

# --------------------------------------
# | HÀM XỬ LÝ (FUNCTION): PROFILE_VIEW |
# --------------------------------------
def profile_view(request):
    return render(request, "account/profile.html")
