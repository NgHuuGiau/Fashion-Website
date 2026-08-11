from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from .forms import (
    CaptchaForm,
    ChangePasswordForm,
    ForgotPasswordForm,
    ProfileForm,
    RegisterForm,
    ResetPasswordForm,
)
from .models import UserActivity, UserProfile, VisitorSession



class UserAuthFlowTest(TestCase):

    def setUp(self):
        cache.clear()
        self.existing = User.objects.create_user(
            username="existing",
            email="existing@test.com",
            password="StrongPass123!",
        )


    def test_register_login_logout_flow(self):
        register_response = self.client.post(
            reverse("users:register"),
            {
                "username": "newuser",
                "first_name": "Nguyen",
                "last_name": "A",
                "email": "newuser@test.com",
                "phone_number": "",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )
        self.assertEqual(register_response.status_code, 302)
        self.assertTrue(User.objects.filter(username="newuser").exists())
        self.assertEqual(User.objects.get(username="newuser").profile.phone_number, "")

        self.client.logout()

        login_response = self.client.post(
            reverse("users:login"),
            {"username": "newuser", "password": "StrongPass123!"},
        )
        self.assertEqual(login_response.status_code, 302)

        profile_response = self.client.get(reverse("users:profile"))
        self.assertEqual(profile_response.status_code, 200)

        logout_response = self.client.get(reverse("users:logout"))
        self.assertEqual(logout_response.status_code, 302)


    def test_register_with_phone_only_is_valid(self):
        response = self.client.post(
            reverse("users:register"),
            {
                "username": "phoneonly",
                "first_name": "Nguyen",
                "last_name": "Phone",
                "email": "",
                "phone_number": "0912345678",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="phoneonly")
        self.assertEqual(user.profile.phone_number, "0912345678")


    def test_register_without_email_or_phone_is_valid(self):
        response = self.client.post(
            reverse("users:register"),
            {
                "username": "nopoint",
                "first_name": "Nguyen",
                "last_name": "No",
                "email": "",
                "phone_number": "",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="nopoint").exists())


    def test_register_password_policy_enforced(self):
        response = self.client.post(
            reverse("users:register"),
            {
                "username": "weakpass",
                "first_name": "Nguyen",
                "last_name": "Weak",
                "email": "weak@test.com",
                "phone_number": "",
                "password1": "abc12345",
                "password2": "abc12345",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mật khẩu phải có ít nhất 1 chữ in hoa")


    def test_register_duplicate_username_shows_error(self):
        response = self.client.post(
            reverse("users:register"),
            {
                "username": "existing",
                "first_name": "Nguyen",
                "last_name": "B",
                "email": "duplicate@test.com",
                "phone_number": "",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tên đăng nhập đã tồn tại")


    def test_register_password_mismatch(self):
        response = self.client.post(
            reverse("users:register"),
            {
                "username": "mismatch",
                "first_name": "Nguyen",
                "last_name": "C",
                "email": "mismatch@test.com",
                "phone_number": "",
                "password1": "StrongPass123!",
                "password2": "WrongPass123!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mật khẩu nhập lại không khớp")


    def test_login_invalid_credentials(self):
        response = self.client.post(
            reverse("users:login"),
            {"username": "existing", "password": "wrong"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sai tên đăng nhập, email, số điện thoại hoặc mật khẩu")


    def test_login_with_email(self):
        response = self.client.post(
            reverse("users:login"),
            {"username": "existing@test.com", "password": "StrongPass123!"},
        )
        self.assertEqual(response.status_code, 302)


    def test_login_with_phone_number(self):
        UserProfile.objects.update_or_create(user=self.existing, defaults={"phone_number": "0911222333"})
        response = self.client.post(
            reverse("users:login"),
            {"username": "0911222333", "password": "StrongPass123!"},
        )
        self.assertEqual(response.status_code, 302)


    def test_login_respects_next_parameter(self):
        response = self.client.post(
            f"{reverse('users:login')}?next={reverse('orders:checkout')}",
            {"username": "existing", "password": "StrongPass123!"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:checkout"))


    def test_profile_requires_login(self):
        response = self.client.get(reverse("users:profile"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("users:login"), response.url)


    def test_authenticated_user_redirected_from_login_and_register(self):
        self.client.login(username="existing", password="StrongPass123!")
        login_page = self.client.get(reverse("users:login"))
        register_page = self.client.get(reverse("users:register"))

        self.assertEqual(login_page.status_code, 302)
        self.assertEqual(register_page.status_code, 302)
        self.assertEqual(login_page.url, reverse("products:product_list"))
        self.assertEqual(register_page.url, reverse("products:product_list"))



class UserTrackingStorageTest(TestCase):

    def setUp(self):
        cache.clear()

    def test_guest_visit_is_stored(self):
        self.client.get(reverse("products:product_list"))
        self.assertGreater(VisitorSession.objects.count(), 0)
        self.assertGreater(UserActivity.objects.filter(event_type="page_view").count(), 0)


    def test_register_is_stored_and_visitor_becomes_authenticated(self):
        self.client.post(
            reverse("users:register"),
            {
                "username": "trackuser",
                "first_name": "Track",
                "last_name": "User",
                "email": "track@test.com",
                "phone_number": "0911111111",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )

        self.assertTrue(UserActivity.objects.filter(event_type="register").exists())
        self.assertTrue(UserProfile.objects.filter(user__username="trackuser", phone_number="0911111111").exists())
        visitor = VisitorSession.objects.order_by("-id").first()
        self.assertIsNotNone(visitor)
        self.assertTrue(visitor.is_authenticated)


class ProfileViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="profileuser", password="StrongPass123!")

    def test_profile_page_renders(self):
        self.client.login(username="profileuser", password="StrongPass123!")
        response = self.client.get(reverse("users:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/profile.html")
        self.assertIn("form", response.context)
        self.assertIn("display_name", response.context)

    def test_profile_update_success(self):
        self.client.login(username="profileuser", password="StrongPass123!")
        response = self.client.post(
            reverse("users:profile"),
            {
                "first_name": "Nguyen",
                "last_name": "Van A",
                "email": "nguyenvana@test.com",
                "phone_number": "0912345678",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Nguyen")
        self.assertEqual(self.user.last_name, "Van A")
        self.assertEqual(self.user.email, "nguyenvana@test.com")

    def test_profile_update_invalid_phone(self):
        self.client.login(username="profileuser", password="StrongPass123!")
        response = self.client.post(
            reverse("users:profile"),
            {
                "first_name": "Nguyen",
                "last_name": "Van A",
                "phone_number": "abc123",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Số điện thoại không hợp lệ")


class CaptchaImageTest(TestCase):

    def setUp(self):
        cache.clear()

    def test_captcha_image_returns_png(self):
        response = self.client.get(reverse("users:captcha_image"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/png")
        self.assertTrue(response.content.startswith(b"\x89PNG"))
        self.assertIn("captcha_code", self.client.session)

    def test_generate_captcha_code_length_and_charset(self):
        from .captcha import generate_captcha_code
        code = generate_captcha_code()
        self.assertEqual(len(code), 6)
        self.assertTrue(code.isalnum())

    def test_generate_captcha_image_returns_bytes(self):
        from .captcha import generate_captcha_image
        data = generate_captcha_image("ABC123")
        self.assertIsInstance(data, bytes)
        self.assertTrue(data.startswith(b"\x89PNG"))


class ForgotPasswordResetFlowTest(TestCase):

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            username="resetme",
            email="resetme@test.com",
            password="OldPassword123!",
        )
        UserProfile.objects.update_or_create(user=self.user, defaults={"phone_number": "0999888777"})

    def test_forgot_password_get_renders(self):
        response = self.client.get(reverse("users:forgot_password"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    def test_forgot_password_authenticated_redirects(self):
        self.client.login(username="resetme", password="OldPassword123!")
        response = self.client.get(reverse("users:forgot_password"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("products:product_list"))

    def test_forgot_password_post_valid_by_username(self):
        response = self.client.post(reverse("users:forgot_password"), {"identifier": "resetme"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("users:forgot_password_captcha"))
        self.assertEqual(self.client.session["reset_user_id"], self.user.id)

    def test_forgot_password_post_valid_by_email(self):
        response = self.client.post(reverse("users:forgot_password"), {"identifier": "RESETME@test.com"})
        self.assertEqual(response.status_code, 302)

    def test_forgot_password_post_valid_by_phone(self):
        response = self.client.post(reverse("users:forgot_password"), {"identifier": "0999888777"})
        self.assertEqual(response.status_code, 302)

    def test_forgot_password_post_not_found(self):
        response = self.client.post(reverse("users:forgot_password"), {"identifier": "no-such-user"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Không tìm thấy tài khoản")

    def test_forgot_password_captcha_requires_session(self):
        response = self.client.get(reverse("users:forgot_password_captcha"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("users:forgot_password"))

    def test_forgot_password_captcha_get_renders(self):
        self._prime_reset_session()
        response = self.client.get(reverse("users:forgot_password_captcha"))
        self.assertEqual(response.status_code, 200)

    def test_forgot_password_captcha_post_valid(self):
        self._prime_reset_session()
        response = self.client.post(reverse("users:forgot_password_captcha"), {"captcha": "abc123"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("users:reset_password"))

    def test_forgot_password_captcha_post_invalid(self):
        self._prime_reset_session()
        response = self.client.post(reverse("users:forgot_password_captcha"), {"captcha": "ZZZZZZ"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mã xác thực không đúng")

    def test_reset_password_requires_session(self):
        response = self.client.get(reverse("users:reset_password"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("users:forgot_password"))

    def test_reset_password_post_success(self):
        self._prime_reset_session()
        response = self.client.post(
            reverse("users:reset_password"),
            {"password1": "BrandNew123!", "password2": "BrandNew123!"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("users:login"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("BrandNew123!"))
        self.assertNotIn("reset_user_id", self.client.session)

    def test_reset_password_post_password_mismatch(self):
        self._prime_reset_session()
        response = self.client.post(
            reverse("users:reset_password"),
            {"password1": "BrandNew123!", "password2": "Different123!"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mật khẩu nhập lại không khớp")

    def _prime_reset_session(self):
        session = self.client.session
        session["reset_user_id"] = self.user.id
        session["captcha_code"] = "ABC123"
        session.save()


class SocialLoginConfigTest(TestCase):

    def tearDown(self):
        import os
        for key in ("GOOGLE_OAUTH_URL", "FACEBOOK_OAUTH_URL", "APPLE_OAUTH_URL"):
            os.environ.pop(key, None)

    def test_social_login_configured_redirects(self):
        import os
        os.environ["GOOGLE_OAUTH_URL"] = "https://example.com/oauth/google"
        response = self.client.get(reverse("users:social_login", kwargs={"provider": "google"}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("https://example.com/oauth/google"))

    def test_social_login_appends_next_for_safe_url(self):
        import os
        os.environ["GOOGLE_OAUTH_URL"] = "https://example.com/oauth/google"
        response = self.client.get(
            reverse("users:social_login", kwargs={"provider": "google"}),
            {"next": reverse("orders:checkout")},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("next=", response.url)

    def test_social_login_rejects_open_redirect_in_next(self):
        import os
        os.environ["GOOGLE_OAUTH_URL"] = "https://example.com/oauth/google"
        response = self.client.get(
            reverse("users:social_login", kwargs={"provider": "google"}),
            {"next": "https://evil.example.com"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertNotIn("evil.example.com", response.url)


class ChangePasswordFlowTest(TestCase):

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(username="changer", password="OldPassword123!")

    def test_change_password_requires_login(self):
        response = self.client.get(reverse("users:change_password"))
        self.assertEqual(response.status_code, 302)

    def test_change_password_get_renders(self):
        self.client.login(username="changer", password="OldPassword123!")
        response = self.client.get(reverse("users:change_password"))
        self.assertEqual(response.status_code, 200)

    def test_change_password_post_success(self):
        self.client.login(username="changer", password="OldPassword123!")
        response = self.client.post(
            reverse("users:change_password"),
            {"current_password": "OldPassword123!", "new_password1": "NewPassword123!", "new_password2": "NewPassword123!"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("users:profile"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewPassword123!"))

    def test_change_password_wrong_current(self):
        self.client.login(username="changer", password="OldPassword123!")
        response = self.client.post(
            reverse("users:change_password"),
            {"current_password": "wrong", "new_password1": "NewPassword123!", "new_password2": "NewPassword123!"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mật khẩu hiện tại không đúng")


class FormValidationTest(TestCase):

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(username="formuser", email="form@test.com", password="StrongPass123!")
        UserProfile.objects.update_or_create(user=self.user, defaults={"phone_number": "0911222333"})

    def test_register_form_invalid_phone(self):
        form = RegisterForm(data={
            "username": "x1", "email": "", "phone_number": "abc",
            "password1": "StrongPass123!", "password2": "StrongPass123!",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("Số điện thoại không hợp lệ", str(form.errors["phone_number"]))

    def test_register_form_password_too_short(self):
        form = RegisterForm(data={
            "username": "x2", "phone_number": "", "email": "x2@test.com",
            "password1": "Short1!", "password2": "Short1!",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("ít nhất 8 ký tự", str(form.errors["password1"]))

    def test_register_form_password_requires_uppercase(self):
        form = RegisterForm(data={
            "username": "x3", "phone_number": "", "email": "x3@test.com",
            "password1": "lowercase123!", "password2": "lowercase123!",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("chữ in hoa", str(form.errors["password1"]))

    def test_register_form_password_requires_digit(self):
        form = RegisterForm(data={
            "username": "x4", "phone_number": "", "email": "x4@test.com",
            "password1": "Uppercaseonly!", "password2": "Uppercaseonly!",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("chữ số", str(form.errors["password1"]))

    def test_register_form_password_requires_special(self):
        form = RegisterForm(data={
            "username": "x5", "phone_number": "", "email": "x5@test.com",
            "password1": "NoSpecial123", "password2": "NoSpecial123",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("ký tự đặc biệt", str(form.errors["password1"]))

    def test_profile_form_update(self):
        form = ProfileForm(
            data={"first_name": "New", "last_name": "Name", "email": "", "phone_number": "0911222333"},
            user=self.user,
        )
        self.assertTrue(form.is_valid())
        form.save()
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "New")

    def test_profile_form_invalid_phone(self):
        form = ProfileForm(data={"phone_number": "abc"}, user=self.user)
        self.assertFalse(form.is_valid())

    def test_profile_form_save_requires_user(self):
        with self.assertRaises(ValueError):
            ProfileForm(data={}).save()

    def test_forgot_password_form_not_found(self):
        form = ForgotPasswordForm(data={"identifier": "missing-account"})
        self.assertFalse(form.is_valid())
        self.assertIn("Không tìm thấy tài khoản", str(form.errors["identifier"]))

    def test_forgot_password_form_found_by_email(self):
        form = ForgotPasswordForm(data={"identifier": "form@test.com"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["_matched_user"].id, self.user.id)

    def test_captcha_form_wrong_code(self):
        from django.test import RequestFactory
        request = RequestFactory().get("/")
        request.session = {"captcha_code": "ABC123"}
        form = CaptchaForm(data={"captcha": "XYZ999"}, request=request)
        self.assertFalse(form.is_valid())

    def test_captcha_form_without_request_fails(self):
        form = CaptchaForm(data={"captcha": "ABC123"})
        self.assertFalse(form.is_valid())

    def test_reset_password_form_mismatch(self):
        form = ResetPasswordForm(data={"password1": "StrongPass123!", "password2": "OtherPass123!"})
        self.assertFalse(form.is_valid())

    def test_change_password_new_matches_current_rejected(self):
        form = ChangePasswordForm(
            data={"current_password": "StrongPass123!", "new_password1": "StrongPass123!", "new_password2": "StrongPass123!"},
            user=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("không được trùng", str(form.errors["new_password1"]))


class MiddlewareVisitorTest(TestCase):

    def setUp(self):
        cache.clear()

    def test_x_forwarded_for_external_ip_used_and_updated(self):
        response = self.client.get(reverse("products:product_list"), HTTP_X_FORWARDED_FOR="8.8.8.8")
        self.assertEqual(response.status_code, 200)
        visitor = VisitorSession.objects.order_by("-id").first()
        self.assertEqual(visitor.ip_address, "8.8.8.8")

        self.client.get(reverse("products:product_list"), HTTP_X_FORWARDED_FOR="9.9.9.9")
        visitor.refresh_from_db()
        self.assertEqual(visitor.ip_address, "9.9.9.9")

    def test_user_agent_captured_and_updated(self):
        self.client.get(reverse("products:product_list"), HTTP_USER_AGENT="TestAgent-1")
        visitor = VisitorSession.objects.order_by("-id").first()
        self.assertEqual(visitor.user_agent, "TestAgent-1")

        self.client.get(reverse("products:product_list"), HTTP_USER_AGENT="TestAgent-2")
        visitor.refresh_from_db()
        self.assertEqual(visitor.user_agent, "TestAgent-2")

    def test_post_records_action_event(self):
        self.client.post(reverse("users:login"), {"username": "nobody", "password": "nope"})
        self.assertTrue(UserActivity.objects.filter(event_type="action").exists())

    def test_login_updates_visitor_user_and_auth_state(self):
        from django.contrib.auth.models import AnonymousUser
        from django.contrib.sessions.backends.db import SessionStore
        from django.http import HttpResponse
        from django.test import RequestFactory
        from .middleware import VisitorTrackingMiddleware

        user = User.objects.create_user(username="mwuser", password="StrongPass123!")
        factory = RequestFactory()

        def get_response(request):
            return HttpResponse("ok")

        middleware = VisitorTrackingMiddleware(get_response)

        session = SessionStore()
        session.create()
        session.save()

        guest_req = factory.get("/")
        guest_req.session = session
        guest_req.user = AnonymousUser()
        middleware(guest_req)
        visitor = VisitorSession.objects.get(session_key=session.session_key)
        self.assertFalse(visitor.is_authenticated)

        auth_req = factory.get("/")
        auth_req.session = session
        auth_req.user = user
        middleware(auth_req)

        visitor.refresh_from_db()
        self.assertTrue(visitor.is_authenticated)
        self.assertEqual(visitor.user_id, user.id)


class RoleSyncTest(TestCase):

    def test_role_from_user_mapping(self):
        from .role_sync import role_from_user

        admin = User.objects.create_user(
            username="role_admin", password="StrongPass123!", is_superuser=True, is_staff=True
        )
        staff = User.objects.create_user(
            username="role_staff", password="StrongPass123!", is_staff=True
        )
        customer = User.objects.create_user(
            username="role_customer", password="StrongPass123!"
        )
        self.assertEqual(role_from_user(admin), 0)
        self.assertEqual(role_from_user(staff), 1)
        self.assertEqual(role_from_user(customer), 2)

    def test_sync_does_not_need_legacy_table(self):
        from .role_sync import write_role_to_legacy

        user = User.objects.create_user(username="no_legacy", password="StrongPass123!")
        write_role_to_legacy(user)
        self.assertTrue(User.objects.filter(pk=user.pk).exists())


class PermissionsTest(TestCase):

    def setUp(self):
        self.admin = User.objects.create_user(
            username="perm_admin", password="StrongPass123!", is_superuser=True, is_staff=True
        )
        self.staff = User.objects.create_user(
            username="perm_staff", password="StrongPass123!", is_staff=True
        )
        self.customer = User.objects.create_user(
            username="perm_customer", password="StrongPass123!"
        )

    def test_role_of_mapping(self):
        from .permissions import role_of, ROLE_ADMIN, ROLE_STAFF, ROLE_USER

        self.assertEqual(role_of(self.admin), ROLE_ADMIN)
        self.assertEqual(role_of(self.staff), ROLE_STAFF)
        self.assertEqual(role_of(self.customer), ROLE_USER)

    def test_admin_has_full_access(self):
        from .permissions import (
            can_delete_product,
            can_manage_coupons,
            can_manage_inventory,
            can_manage_orders,
            can_manage_products,
            can_manage_users,
            is_admin,
            is_staff_member,
        )

        self.assertTrue(is_admin(self.admin))
        self.assertTrue(is_staff_member(self.admin))
        self.assertTrue(can_manage_orders(self.admin))
        self.assertTrue(can_manage_inventory(self.admin))
        self.assertTrue(can_manage_products(self.admin))
        self.assertTrue(can_delete_product(self.admin))
        self.assertTrue(can_manage_coupons(self.admin))
        self.assertTrue(can_manage_users(self.admin))

    def test_staff_restricted_access(self):
        from .permissions import (
            can_delete_product,
            can_manage_coupons,
            can_manage_inventory,
            can_manage_orders,
            can_manage_products,
            can_manage_users,
            is_admin,
            is_staff_member,
        )

        self.assertFalse(is_admin(self.staff))
        self.assertTrue(is_staff_member(self.staff))
        self.assertTrue(can_manage_orders(self.staff))
        self.assertTrue(can_manage_inventory(self.staff))
        self.assertTrue(can_manage_products(self.staff))
        self.assertFalse(can_delete_product(self.staff))
        self.assertFalse(can_manage_coupons(self.staff))
        self.assertFalse(can_manage_users(self.staff))

    def test_customer_has_no_access(self):
        from .permissions import (
            can_manage_inventory,
            can_manage_orders,
            is_admin,
            is_staff_member,
        )

        self.assertFalse(is_admin(self.customer))
        self.assertFalse(is_staff_member(self.customer))
        self.assertFalse(can_manage_orders(self.customer))
        self.assertFalse(can_manage_inventory(self.customer))

