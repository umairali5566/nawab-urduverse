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

    content = RichTextUploadingField(verbose_name='مواد')
    excerpt = models.TextField(blank=True, verbose_name='خلاصہ')
    featured_image = models.ImageField(upload_to='stories/', blank=True, verbose_name='نمایاں تصویر')
    categories = models.ManyToManyField(Category, limit_choices_to={'category_type': 'story'}, verbose_name='زمرہ جات')
    tags = models.CharField(max_length=500, blank=True, verbose_name='ٹیگز')
    reading_time = models.PositiveIntegerField(default=0, verbose_name='پڑھنے کا وقت (منٹ)')

    class Meta(BaseContentModel.Meta):
        verbose_name = 'کہانی'
        verbose_name_plural = 'کہانیاں'

    def save(self, *args, **kwargs):
        # Calculate reading time
        if self.content:
            plain_content = strip_tags(self.content)
            word_count = len(plain_content.split())
            self.reading_time = max(1, word_count // 200)

        # Generate excerpt if not provided
        if not self.excerpt and self.content:
            plain_content = strip_tags(self.content)
            self.excerpt = plain_content[:300] + '...' if len(plain_content) > 300 else plain_content

        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('story_detail', kwargs={'slug': self.slug})
