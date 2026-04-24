from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.urls import reverse

from blog.admin import BlogPostAdmin
from blog.models import BlogPost
from novels.admin import NovelAdmin
from novels.models import Novel
from poetry.admin import PoetryAdmin
from poetry.models import Poetry
from quotes.admin import QuoteAdmin
from quotes.models import Quote
from videos.admin import VideoAdmin
from videos.models import Video


class OptionalAuthorUploadTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.superuser = get_user_model().objects.create_superuser(
            username="dashboard-admin",
            email="dashboard-admin@example.com",
            password="safe-password-123",
        )

    def test_admin_forms_do_not_require_author(self):
        request = self.factory.get(reverse("admin:novels_novel_add"))
        request.user = self.superuser

        admin_configs = [
            (Novel, NovelAdmin),
            (Poetry, PoetryAdmin),
            (BlogPost, BlogPostAdmin),
            (Quote, QuoteAdmin),
            (Video, VideoAdmin),
        ]

        for model, admin_class in admin_configs:
            with self.subTest(model=model.__name__):
                form = admin_class(model, admin.site).get_form(request)()
                self.assertFalse(form.fields["author"].required)

    def test_dashboard_add_poetry_allows_blank_author(self):
        self.client.force_login(self.superuser)

        response = self.client.post(
            reverse("dashboard_add_poetry"),
            {"title": "Blank Author Poetry", "author": "", "content": "Some poetry lines."},
        )

        self.assertRedirects(response, reverse("dashboard_poetry_list"))
        poem = Poetry.objects.get(title="Blank Author Poetry")
        self.assertIsNone(poem.author)

    def test_dashboard_add_blog_allows_blank_author(self):
        self.client.force_login(self.superuser)

        response = self.client.post(
            reverse("dashboard_add_blog"),
            {"title": "Blank Author Blog", "author": "", "content": "Blog content body."},
        )

        self.assertRedirects(response, reverse("dashboard_blog_list"))
        post = BlogPost.objects.get(title="Blank Author Blog")
        self.assertIsNone(post.author)

    def test_dashboard_add_novel_allows_blank_author(self):
        self.client.force_login(self.superuser)

        response = self.client.post(
            reverse("dashboard_add_novel"),
            {"title": "Blank Author Novel", "author": "", "description": "Novel description."},
        )

        self.assertRedirects(response, reverse("dashboard_novel_list"))
        novel = Novel.objects.get(title="Blank Author Novel")
        self.assertIsNone(novel.author)

    def test_dashboard_add_quote_allows_blank_author(self):
        self.client.force_login(self.superuser)

        quote_text = "A quote without an author."
        response = self.client.post(
            reverse("dashboard_add_quote"),
            {"quote": quote_text, "author": "", "quote_type": "motivational"},
        )

        self.assertRedirects(response, reverse("dashboard_quote_list"))
        quote = Quote.objects.get(text=quote_text)
        self.assertIsNone(quote.author)

    def test_dashboard_add_video_allows_blank_author(self):
        self.client.force_login(self.superuser)

        response = self.client.post(
            reverse("dashboard_add_video"),
            {
                "title": "Blank Author Video",
                "author": "",
                "video_type": "poetry",
                "video_url": "https://example.com/video.mp4",
                "description": "Video description.",
            },
        )

        self.assertRedirects(response, reverse("dashboard_video_list"))
        video = Video.objects.get(title="Blank Author Video")
        self.assertIsNone(video.author)
