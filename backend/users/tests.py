from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import UserActivity, UserProfile, VisitorSession



class UserAuthFlowTest(TestCase):

    def setUp(self):
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
