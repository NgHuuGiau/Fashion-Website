from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("dang-ky/", views.register_view, name="register"),
    path("dang-nhap/", views.login_view, name="login"),
    path("dang-nhap/<slug:provider>/", views.social_login_view, name="social_login"),
    path("dang-xuat/", views.logout_view, name="logout"),
    path("tai-khoan/", views.profile_view, name="profile"),
    path("tai-khoan/gioi-thieu/", views.referral_view, name="referral"),
    path("tai-khoan/doi-mat-khau/", views.change_password_view, name="change_password"),
    path("tai-khoan/dia-chi/them/", views.address_add, name="address_add"),
    path(
        "tai-khoan/dia-chi/<int:address_id>/xoa/",
        views.address_delete,
        name="address_delete",
    ),
    path(
        "tai-khoan/dia-chi/<int:address_id>/mac-dinh/",
        views.address_set_default,
        name="address_set_default",
    ),
    path("quen-mat-khau/", views.forgot_password_view, name="forgot_password"),
    path(
        "quen-mat-khau/captcha/",
        views.forgot_password_captcha_view,
        name="forgot_password_captcha",
    ),
    path(
        "quen-mat-khau/captcha/image/", views.captcha_image_view, name="captcha_image"
    ),
    path("quen-mat-khau/dat-lai/", views.reset_password_view, name="reset_password"),
]
