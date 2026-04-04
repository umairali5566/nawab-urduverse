"""
Poetry Models for Nawab UrduVerse
"""

import re
from html import unescape

from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models
from django.urls import reverse
from django.utils.html import escape, strip_tags
from django.utils.safestring import mark_safe
from django.utils.text import slugify

from core.models import Author, Category


class Poetry(models.Model):
    """Poetry model"""

    POETRY_TYPES = (
        ("ghazal", "غزل"),
        ("nazm", "نظم"),
        ("shayari", "شاعری"),
        ("rubai", "رباعی"),
        ("qata", "قطعہ"),
        ("marsiya", "مرثیہ"),
        ("manqabat", "منقبت"),
        ("naat", "نعت"),
    )

    MOOD_CHOICES = (
        ("love", "محبت"),
        ("sad", "اداسی"),
        ("romantic", "رومانوی"),
        ("inspirational", "حوصلہ افزائی"),
        ("religious", "مذہبی"),
        ("patriotic", "وطن دوستی"),
        ("funny", "مزاحیہ"),
        ("philosophical", "فلسفیانہ"),
    )

    title = models.CharField(max_length=300, verbose_name="عنوان")
    slug = models.SlugField(unique=True, verbose_name="سلگ")
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="poetry", verbose_name="شاعر")
    poetry_type = models.CharField(max_length=20, choices=POETRY_TYPES, default="ghazal", verbose_name="قسم")
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES, blank=True, verbose_name="موڈ")
    content = RichTextUploadingField(verbose_name="اشعار")
    background_image = models.ImageField(upload_to="poetry/backgrounds/", blank=True, verbose_name="پس منظر")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={"category_type": "poetry"}, verbose_name="زمرہ")
    tags = models.CharField(max_length=500, blank=True, verbose_name="ٹیگز")
    is_published = models.BooleanField(default=True, verbose_name="شائع شدہ")
    is_featured = models.BooleanField(default=False, verbose_name="نمایاں")
    views_count = models.PositiveIntegerField(default=0, verbose_name="مشاہدات")
    likes_count = models.PositiveIntegerField(default=0, verbose_name="پسندیدگی")
    shares_count = models.PositiveIntegerField(default=0, verbose_name="شیئرز")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="تاریخ اشاعت")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # SEO fields
    meta_title = models.CharField(max_length=200, blank=True, verbose_name="Meta Title")
    meta_description = models.TextField(blank=True, verbose_name="Meta Description")
    meta_keywords = models.CharField(max_length=500, blank=True, verbose_name="Meta Keywords")

    class Meta:
        verbose_name = "شاعری"
        verbose_name_plural = "اشعار"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.author.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("poetry_detail", kwargs={"author_slug": self.author.slug, "slug": self.slug})

    @property
    def poet_name(self):
        return self.author.name

    @property
    def primary_category(self):
        return self.category

    @property
    def plain_text_content(self):
        """Return normalized plain text used by layout generator and TTS."""
        html = self.content or ""
        html = re.sub(r"<\s*br\s*/?\s*>", "\n", html, flags=re.IGNORECASE)
        html = re.sub(r"</p\s*>", "\n", html, flags=re.IGNORECASE)
        html = re.sub(r"<p[^>]*>", "", html, flags=re.IGNORECASE)
        text = strip_tags(html)
        text = unescape(text)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)

    def get_sher_pairs(self):
        """Group every two lines into one sher pair."""
        lines = self.plain_text_content.splitlines()
        pairs = []
        for index in range(0, len(lines), 2):
            first = lines[index]
            second = lines[index + 1] if index + 1 < len(lines) else ""
            pairs.append((first, second))
        return pairs

    @property
    def formatted_poetry_html(self):
        """Server-side poetry layout in traditional sher structure."""
        pairs = self.get_sher_pairs()
        if not pairs:
            return ""

        html_chunks = []
        for index, (first, second) in enumerate(pairs):
            chunk = [
                '<div class="sher-block">',
                f'<p class="sher-line">{escape(first)}</p>',
            ]
            if second:
                chunk.append(f'<p class="sher-line">{escape(second)}</p>')
            chunk.append("</div>")
            html_chunks.append("".join(chunk))

            if index < len(pairs) - 1:
                html_chunks.append('<div class="sher-divider" aria-hidden="true"></div>')

        return mark_safe("".join(html_chunks))


class PoetryCollection(models.Model):
    """Poetry collection/diwan model"""

    title = models.CharField(max_length=300, verbose_name="عنوان")
    slug = models.SlugField(unique=True, verbose_name="سلگ")
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="collections", verbose_name="شاعر")
    description = models.TextField(blank=True, verbose_name="تفصیل")
    cover_image = models.ImageField(upload_to="poetry/collections/", blank=True, verbose_name="سرورق")
    poems = models.ManyToManyField(Poetry, related_name="collections", verbose_name="اشعار")
    is_published = models.BooleanField(default=True, verbose_name="شائع شدہ")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "کلیہ اشعار"
        verbose_name_plural = "کلیات اشعار"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("collection_detail", kwargs={"slug": self.slug})
