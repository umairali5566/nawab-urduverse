from django.test import TestCase
from django.urls import reverse

from core.models import Author
from poetry.models import Poetry


class HomePageRenderingTests(TestCase):
    def test_homepage_renders_with_poetry_in_mixed_trending(self):
        author = Author.objects.create(name="Allama Iqbal", slug="allama-iqbal")
        Poetry.objects.create(
            title="Shakwa",
            slug="shakwa",
            author=author,
            content="<p>لب پہ آتی ہے دعا بن کے تمنا میری</p><p>زندگی شمع کی صورت ہو خدایا میری</p>",
            is_published=True,
            views_count=120,
            likes_count=45,
            shares_count=12,
        )

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Shakwa")

    def test_homepage_includes_pwa_manifest_link(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'rel="manifest" href="/static/manifest.json"', html=False)

    def test_service_worker_endpoint_allows_root_scope(self):
        response = self.client.get("/static/sw.js")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Service-Worker-Allowed"], "/")
        self.assertIn("application/javascript", response["Content-Type"])
