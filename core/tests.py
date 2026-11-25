from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

User = get_user_model()


class RegisterAndLoginTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            "username": "maya",
            "email": "maya@example.com",
            "password": "correct-horse-9",
        }

    def test_register_new_user(self):
        response = self.client.post("/api/register/", self.user_data, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["username"], "maya")
        self.assertIn("id", response.data)
        self.assertTrue(User.objects.filter(username="maya").exists())

    def test_register_duplicate_username(self):
        User.objects.create_user(**self.user_data)

        response = self.client.post("/api/register/", self.user_data, format="json")

        self.assertEqual(response.status_code, 400)

    def test_register_short_password(self):
        response = self.client.post(
            "/api/register/",
            {**self.user_data, "password": "short"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.filter(username="maya").exists())

    def test_login_correct_password(self):
        User.objects.create_user(**self.user_data)

        response = self.client.post(
            "/api/token/",
            {"username": "maya", "password": "correct-horse-9"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_wrong_password(self):
        User.objects.create_user(**self.user_data)

        response = self.client.post(
            "/api/token/",
            {"username": "maya", "password": "wrong-password"},
            format="json",
        )

        self.assertEqual(response.status_code, 401)


    # --- Week 4 Day 3: token refresh -------------------------------------------

    def test_refresh_with_valid_token_returns_new_access(self):
        User.objects.create_user(**self.user_data)
        login = self.client.post(
            "/api/token/",
            {"username": "maya", "password": "correct-horse-9"},
            format="json",
        )

        response = self.client.post(
            "/api/token/refresh/", {"refresh": login.data["refresh"]}, format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)

    def test_refresh_with_invalid_token_is_401(self):
        response = self.client.post(
            "/api/token/refresh/", {"refresh": "not-a-real-token"}, format="json"
        )

        self.assertEqual(response.status_code, 401)

    # --- Week 4 Day 3: a real token unlocks ask_ai ------------------------------

    def test_ask_ai_with_bearer_token_is_allowed(self):
        User.objects.create_user(**self.user_data)
        login = self.client.post(
            "/api/token/",
            {"username": "maya", "password": "correct-horse-9"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

        fake = {"answer": "river-stone-19 [1]", "sources": []}
        with patch("blog.api.views.ask", return_value=fake):  # no Voyage/OpenAI
            response = self.client.post(
                "/api/posts/ask_ai/", {"question": "staging password?"}, format="json"
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, fake)
