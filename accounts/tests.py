from django.test import TestCase
from django.urls import reverse

from .models import User


class AccountRoutingTests(TestCase):
    def test_dashboard_redirects_to_accounts_login(self):
        response = self.client.get(reverse("dashboard"))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('dashboard')}",
            fetch_redirect_response=False,
        )

    def test_login_accepts_email_as_username(self):
        user = User.objects.create_user(
            username="urdureader",
            email="reader@example.com",
            password="StrongPass123",
        )

        response = self.client.post(
            reverse("login"),
            {"username": user.email, "password": "StrongPass123"},
            follow=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/accounts/dashboard/"))
        self.assertTrue(self.client.session.get("_auth_user_id") == str(user.pk))
