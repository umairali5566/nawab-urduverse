"""
Stories Models for Nawab Urdu Academy
"""

from django.db import models
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField

from core.models import Author, BaseContentModel, Category


class Story(BaseContentModel):
    """Story model"""

    # Content fields
    content = models.TextField(verbose_name='مواد')
    featured_image = models.ImageField(upload_to='stories/featured/', blank=True, verbose_name='نمایاں تصویر')
    excerpt = models.CharField(max_length=500, blank=True, verbose_name='خلاصہ')
    reading_time = models.PositiveIntegerField(default=0, verbose_name='پڑھنے کا وقت (منٹ)')
    
    # Category
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='زمرہ')
    
    # Author with custom related_name to maintain 'stories' reverse accessor
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='stories', verbose_name='مصنف')

    class Meta:
        verbose_name = 'کہانی'
        verbose_name_plural = 'کہانیاں'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Strip HTML tags from content
        self.content = strip_tags(self.content)
        # Calculate reading time: assume average reading speed 200 words per minute
        if self.content:
            word_count = len(self.content.split())
            self.reading_time = max(1, word_count // 200)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("story_detail", kwargs={"slug": self.slug})
