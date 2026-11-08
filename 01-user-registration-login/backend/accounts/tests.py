from django.core.cache import cache
from rest_framework.test import APITestCase

from .models import User

REGISTER = "/api/auth/register/"
LOGIN = "/api/auth/login/"
REFRESH = "/api/auth/refresh/"
LOGOUT = "/api/auth/logout/"
ME = "/api/auth/me/"


class ApiTestCase(APITestCase):
    """Throttle counters live in the cache; start every test with a clean slate."""

    def setUp(self):
        super().setUp()
        cache.clear()


GOOD = {"email": "Rahim@Example.com", "full_name": "Rahim Uddin", "phone": "01712345678",
        "language": "bn", "password": "S7rong-pass!"}


class RegistrationTests(ApiTestCase):
    def test_register_creates_user_and_returns_tokens(self):
        res = self.client.post(REGISTER, GOOD, format="json")
        self.assertEqual(res.status_code, 201)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)
        self.assertEqual(res.data["user"]["email"], "rahim@example.com")  # lower-cased
        self.assertNotIn("password", res.data["user"])

    def test_password_is_hashed(self):
        self.client.post(REGISTER, GOOD, format="json")
        user = User.objects.get(email="rahim@example.com")
        self.assertNotEqual(user.password, GOOD["password"])
        self.assertTrue(user.check_password(GOOD["password"]))

    def test_duplicate_email_rejected_case_insensitively(self):
        self.client.post(REGISTER, GOOD, format="json")
        res = self.client.post(REGISTER, {**GOOD, "email": "RAHIM@example.com"}, format="json")
        self.assertEqual(res.status_code, 400)
        self.assertIn("email", res.data)

    def test_weak_passwords_rejected(self):
        for bad in ["short1", "12345678", "password", "rahim@example.com"]:
            res = self.client.post(REGISTER, {**GOOD, "password": bad}, format="json")
            self.assertEqual(res.status_code, 400, bad)
            self.assertTrue("password" in res.data or "non_field_errors" in res.data, bad)

    def test_required_fields(self):
        res = self.client.post(REGISTER, {}, format="json")
        self.assertEqual(res.status_code, 400)
        for field in ("email", "full_name", "password"):
            self.assertIn(field, res.data)

    def test_invalid_email_and_language(self):
        self.assertEqual(self.client.post(REGISTER, {**GOOD, "email": "nope"}, format="json").status_code, 400)
        self.assertEqual(self.client.post(REGISTER, {**GOOD, "language": "fr"}, format="json").status_code, 400)

    def test_client_cannot_make_itself_staff(self):
        res = self.client.post(REGISTER, {**GOOD, "is_staff": True, "is_superuser": True}, format="json")
        self.assertEqual(res.status_code, 201)
        user = User.objects.get(email="rahim@example.com")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)


class LoginTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(email="karim@example.com", password="S7rong-pass!", full_name="Karim")

    def test_login_success(self):
        res = self.client.post(LOGIN, {"email": "karim@example.com", "password": "S7rong-pass!"}, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertIn("access", res.data)
        self.assertEqual(res.data["user"]["email"], "karim@example.com")

    def test_login_email_is_case_insensitive(self):
        res = self.client.post(LOGIN, {"email": " KARIM@Example.com ", "password": "S7rong-pass!"}, format="json")
        self.assertEqual(res.status_code, 200)

    def test_wrong_password_and_unknown_email_look_identical(self):
        a = self.client.post(LOGIN, {"email": "karim@example.com", "password": "wrong"}, format="json")
        b = self.client.post(LOGIN, {"email": "ghost@example.com", "password": "wrong"}, format="json")
        self.assertEqual(a.status_code, 401)
        self.assertEqual(b.status_code, 401)
        self.assertEqual(a.data, b.data)

    def test_inactive_user_cannot_login(self):
        self.user.is_active = False
        self.user.save()
        res = self.client.post(LOGIN, {"email": "karim@example.com", "password": "S7rong-pass!"}, format="json")
        self.assertEqual(res.status_code, 401)


class TokenAndProfileTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        res = self.client.post(REGISTER, GOOD, format="json")
        self.access, self.refresh = res.data["access"], res.data["refresh"]

    def auth(self, token=None):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token or self.access}")

    def test_me_requires_token(self):
        self.assertEqual(self.client.get(ME).status_code, 401)

    def test_me_returns_profile(self):
        self.auth()
        res = self.client.get(ME)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["email"], "rahim@example.com")

    def test_me_can_update_profile_but_not_email_or_staff(self):
        self.auth()
        res = self.client.patch(ME, {"full_name": "R. Uddin", "email": "x@y.com", "is_staff": True}, format="json")
        self.assertEqual(res.status_code, 200)
        user = User.objects.get(pk=res.data["id"])
        self.assertEqual(user.full_name, "R. Uddin")
        self.assertEqual(user.email, "rahim@example.com")
        self.assertFalse(user.is_staff)

    def test_refresh_rotates_and_old_refresh_is_dead(self):
        res = self.client.post(REFRESH, {"refresh": self.refresh}, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)  # rotated
        again = self.client.post(REFRESH, {"refresh": self.refresh}, format="json")
        self.assertEqual(again.status_code, 401)  # blacklisted after rotation

    def test_logout_blacklists_refresh_token(self):
        self.auth()
        self.assertEqual(self.client.post(LOGOUT, {"refresh": self.refresh}, format="json").status_code, 204)
        self.client.credentials()
        self.assertEqual(self.client.post(REFRESH, {"refresh": self.refresh}, format="json").status_code, 401)

    def test_garbage_token_rejected(self):
        self.auth("not.a.token")
        self.assertEqual(self.client.get(ME).status_code, 401)


class ThrottleTests(ApiTestCase):
    def test_login_is_rate_limited(self):
        codes = [self.client.post(LOGIN, {"email": "a@b.com", "password": "x"}, format="json").status_code
                 for _ in range(12)]
        self.assertEqual(codes[0], 401)
        self.assertEqual(codes[-1], 429)


class UserModelTests(ApiTestCase):
    def test_create_user_requires_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="x", full_name="N")

    def test_create_superuser_flags(self):
        admin = User.objects.create_superuser(email="a@b.com", password="S7rong-pass!", full_name="Admin")
        self.assertTrue(admin.is_staff and admin.is_superuser)