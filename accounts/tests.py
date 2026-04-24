from django.test import TestCase
from django.urls import reverse


class AccountRoutingTests(TestCase):
    def test_dashboard_redirects_to_accounts_login(self):
        response = self.client.get(reverse("dashboard"))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('dashboard')}",
            fetch_redirect_response=False,
        )
