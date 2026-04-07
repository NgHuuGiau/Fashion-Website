from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import UserActivity, UserProfile, VisitorSession



# --------------------------------------
# | KHỐI LỚP (CLASS): USERAUTHFLOWTEST |
# --------------------------------------
class UserAuthFlowTest(TestCase):

    # -------------------------------
    # | HÀM XỬ LÝ (FUNCTION): SETUP |
    # -------------------------------
    def setUp(self):
        self.existing = User.objects.create_user(
            username="existing",
            email="existing@test.com",
            password="StrongPass123!",
        )


    # ---------------------------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): TEST_REGISTER_LOGIN_LOGOUT_FLOW |
    # ---------------------------------------------------------
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


    # ----------------------------------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): TEST_REGISTER_WITH_PHONE_ONLY_IS_VALID |
    # ----------------------------------------------------------------
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


    # ---------------------------------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): TEST_REGISTER_REQUIRES_EMAIL_OR_PHONE |
    # ---------------------------------------------------------------
    def test_register_requires_email_or_phone(self):
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
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cần nhập ít nhất Email hoặc Số điện thoại")


    # ----------------------------------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): TEST_REGISTER_PASSWORD_POLICY_ENFORCED |
    # ----------------------------------------------------------------
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


    # ----------------------------------------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): TEST_REGISTER_DUPLICATE_USERNAME_SHOWS_ERROR |
    # ----------------------------------------------------------------------
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


    # ---------------------------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): TEST_REGISTER_PASSWORD_MISMATCH |
    # ---------------------------------------------------------
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


    # --------------------------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): TEST_LOGIN_INVALID_CREDENTIALS |
    # --------------------------------------------------------
    def test_login_invalid_credentials(self):
        response = self.client.post(
            reverse("users:login"),
            {"username": "existing", "password": "wrong"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sai tên đăng nhập hoặc mật khẩu")


    # ------------------------------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): TEST_LOGIN_RESPECTS_NEXT_PARAMETER |
    # ------------------------------------------------------------
    def test_login_respects_next_parameter(self):
        response = self.client.post(
            f"{reverse('users:login')}?next={reverse('orders:checkout')}",
            {"username": "existing", "password": "StrongPass123!"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:checkout"))


    # -----------------------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): TEST_PROFILE_REQUIRES_LOGIN |
    # -----------------------------------------------------
    def test_profile_requires_login(self):
        response = self.client.get(reverse("users:profile"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("users:login"), response.url)


    # ------------------------------------------------------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): TEST_AUTHENTICATED_USER_REDIRECTED_FROM_LOGIN_AND_REGISTER |
    # ------------------------------------------------------------------------------------
    def test_authenticated_user_redirected_from_login_and_register(self):
        self.client.login(username="existing", password="StrongPass123!")
        login_page = self.client.get(reverse("users:login"))
        register_page = self.client.get(reverse("users:register"))

        self.assertEqual(login_page.status_code, 302)
        self.assertEqual(register_page.status_code, 302)
        self.assertEqual(login_page.url, reverse("products:product_list"))
        self.assertEqual(register_page.url, reverse("products:product_list"))



# ---------------------------------------------
# | KHỐI LỚP (CLASS): USERTRACKINGSTORAGETEST |
# ---------------------------------------------
class UserTrackingStorageTest(TestCase):

    # ----------------------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): TEST_GUEST_VISIT_IS_STORED |
    # ----------------------------------------------------
    def test_guest_visit_is_stored(self):
        self.client.get(reverse("products:product_list"))
        self.assertGreater(VisitorSession.objects.count(), 0)
        self.assertGreater(UserActivity.objects.filter(event_type="page_view").count(), 0)


    # -----------------------------------------------------------------------------------
    # | HÀM XỬ LÝ (FUNCTION): TEST_REGISTER_IS_STORED_AND_VISITOR_BECOMES_AUTHENTICATED |
    # -----------------------------------------------------------------------------------
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
