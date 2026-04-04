from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import resolve, reverse

from core.models import Author, Category, ReadingProgress
from novels import views
from novels.models import Chapter, Novel


class NovelChapterFlowTests(TestCase):
    def setUp(self):
        self.author = Author.objects.create(name="Test Author", slug="test-author")
        self.category = Category.objects.create(
            name="Test Novel Category",
            slug="test-novel-category",
            category_type="novel",
        )
        self.novel = Novel.objects.create(
            title="Test Novel",
            slug="test-novel",
            author=self.author,
            description="<p>Novel description</p>",
            cover_image="novels/covers/test.jpg",
            category=self.category,
            is_published=True,
        )

        self.chapter1 = Chapter.objects.create(
            novel=self.novel,
            chapter_number=1,
            title="First Chapter",
            content="<p>Chapter one content.</p>",
            is_published=True,
        )
        self.chapter2 = Chapter.objects.create(
            novel=self.novel,
            chapter_number=2,
            title="Second Chapter",
            content="<p>Chapter two content.</p>",
            is_published=True,
        )
        self.chapter3 = Chapter.objects.create(
            novel=self.novel,
            chapter_number=3,
            title="Third Chapter",
            content="<p>Chapter three content.</p>",
            is_published=True,
        )

    def test_continue_reading_route_not_shadowed_by_chapter_route(self):
        url = reverse("continue_reading", kwargs={"slug": self.novel.slug})
        match = resolve(url)
        self.assertEqual(match.func, views.continue_reading)

        response = self.client.get(url)
        self.assertRedirects(
            response,
            self.chapter1.get_absolute_url(),
            fetch_redirect_response=False,
        )

    def test_continue_reading_redirects_to_user_progress(self):
        user = get_user_model().objects.create_user(
            username="reader1",
            email="reader1@example.com",
            password="safe-password-123",
        )
        ReadingProgress.objects.create(
            user=user,
            novel=self.novel,
            chapter=self.chapter2,
            progress_percent=60,
        )

        self.client.force_login(user)
        url = reverse("continue_reading", kwargs={"slug": self.novel.slug})
        response = self.client.get(url)
        self.assertRedirects(
            response,
            self.chapter2.get_absolute_url(),
            fetch_redirect_response=False,
        )

    def test_chapter_detail_context_includes_previous_and_next(self):
        response = self.client.get(self.chapter2.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["previous_chapter"].pk, self.chapter1.pk)
        self.assertEqual(response.context["next_chapter"].pk, self.chapter3.pk)
        self.assertEqual(response.context["chapter_count"], 3)

    def test_legacy_chapter_url_redirects_to_canonical_url(self):
        legacy_url = f"/novels/{self.novel.slug}/{self.chapter2.slug}/"
        response = self.client.get(legacy_url)
        self.assertRedirects(
            response,
            self.chapter2.get_absolute_url(),
            status_code=301,
            fetch_redirect_response=False,
        )

    def test_novel_detail_lists_chapters_in_chapter_number_order(self):
        response = self.client.get(self.novel.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        chapter_numbers = [chapter.chapter_number for chapter in response.context["chapters"]]
        self.assertEqual(chapter_numbers, [1, 2, 3])
