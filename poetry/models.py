"""
Poetry Models for Nawab Urdu Academy
"""


from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.text import slugify

from core.models import Author, Category


class Poetry(models.Model):
    """Poetry model"""

    title = models.CharField(max_length=300, verbose_name='عنوان')
    slug = models.SlugField(unique=True, verbose_name='سلگ')
    content = models.TextField(verbose_name='مواد')
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='poetry', verbose_name='مصنف')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='زمرہ')
    is_published = models.BooleanField(default=True, verbose_name='شائع شدہ')
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='شائع ہونے کی تاریخ')
    views_count = models.PositiveIntegerField(default=0, verbose_name='مشاہدات')
    likes_count = models.PositiveIntegerField(default=0, verbose_name='پسندیدگی')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "شاعری"
        verbose_name_plural = "اشعار"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        # Strip HTML tags from content
        self.content = strip_tags(self.content)
        # Normalize Urdu text (simple for now, can expand)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("poetry_detail", kwargs={"slug": self.slug})


class PoetryCollection(models.Model):
    """Poetry collection/diwan model"""

    title = models.CharField(max_length=300, verbose_name="عنوان")
    slug = models.SlugField(unique=True, verbose_name="سلگ")
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="collections", verbose_name="شاعر")
    description = models.TextField(blank=True, verbose_name="تفصیل")
    cover_image = models.ImageField(upload_to="poetry/collections/", blank=True, null=True, verbose_name="سرورق")
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
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("collection_detail", kwargs={"slug": self.slug})
