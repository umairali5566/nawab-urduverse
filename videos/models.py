"""
Videos Models for Nawab Urdu Academy
"""

from urllib.parse import parse_qs, urlparse

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.html import strip_tags

from core.models import Author, Category


class Video(models.Model):
    """Video model"""

    VIDEO_TYPES = (
        ('tutorial', 'درسی ویڈیو'),
        ('poetry', 'شاعری'),
        ('story', 'کہانی'),
        ('music', 'موسیقی'),
        ('interview', 'انٹرویو'),
        ('other', 'دیگر'),
    )

    title = models.CharField(max_length=300, verbose_name='عنوان')
    slug = models.SlugField(unique=True, verbose_name='سلگ')
    content = models.TextField(verbose_name='مواد')  # Description
    description = models.TextField(blank=True, verbose_name='تفصیل')
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='videos', verbose_name='مصنف')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='زمرہ')
    video_type = models.CharField(max_length=20, choices=VIDEO_TYPES, default='other', verbose_name='قسم')
    is_published = models.BooleanField(default=True, verbose_name='شائع شدہ')
    is_featured = models.BooleanField(default=False, verbose_name='نمایاں')
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='شائع ہونے کی تاریخ')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views_count = models.PositiveIntegerField(default=0, verbose_name='مشاہدات')
    likes_count = models.PositiveIntegerField(default=0, verbose_name='پسندیدگی')
    thumbnail_url = models.URLField(blank=True, verbose_name='تھمب نیل URL')
    meta_title = models.CharField(max_length=200, blank=True, verbose_name='میٹا عنوان')
    meta_description = models.TextField(blank=True, verbose_name='میٹا تفصیل')
    meta_keywords = models.CharField(max_length=500, blank=True, verbose_name='میٹا کیورڈز')

    class Meta:
        verbose_name = 'ویڈیو'
        verbose_name_plural = 'ویڈیوز'
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
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("video_detail", kwargs={"slug": self.slug})
    
    def get_thumbnail_url(self):
        """Get thumbnail URL from video"""
        if self.thumbnail_url:
            return self.thumbnail_url
        # Try to extract from YouTube if available
        if 'youtube.com' in self.content or 'youtu.be' in self.content:
            return 'https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg'
        return ''
    
    @property
    def categories(self):
        """Return category as a list for template compatibility"""
        return [self.category] if self.category else []


class VideoPlaylist(models.Model):
    """Video playlist model"""
    
    title = models.CharField(max_length=200, verbose_name='عنوان')
    slug = models.SlugField(unique=True, verbose_name='سلگ')
    description = models.TextField(blank=True, verbose_name='تفصیل')
    cover_image = models.ImageField(upload_to='videos/playlists/', blank=True, null=True, verbose_name='سرورق')
    videos = models.ManyToManyField(Video, related_name='playlists', verbose_name='ویڈیوز')
    is_published = models.BooleanField(default=True, verbose_name='شائع شدہ')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'پلے لسٹ'
        verbose_name_plural = 'پلے لسٹس'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('playlist_detail', kwargs={'slug': self.slug})
