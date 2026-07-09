from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("dang-ky/", views.register_view, name="register"),
    path("dang-nhap/", views.login_view, name="login"),
    path("dang-nhap/<slug:provider>/", views.social_login_view, name="social_login"),
    path("dang-xuat/", views.logout_view, name="logout"),
    path("tai-khoan/", views.profile_view, name="profile"),
]
