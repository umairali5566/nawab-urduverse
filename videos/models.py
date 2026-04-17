"""
Videos Models for Nawab Urdu Academy
"""

from urllib.parse import parse_qs, urlparse

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from core.models import Author, Category


class Video(models.Model):
    """Video model"""

    title = models.CharField(max_length=300, verbose_name='عنوان')
    slug = models.SlugField(unique=True, verbose_name='سلگ')
    content = models.TextField(verbose_name='مواد')  # Description
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='videos', verbose_name='مصنف')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='زمرہ')
    is_published = models.BooleanField(default=True, verbose_name='شائع شدہ')
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='شائع ہونے کی تاریخ')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'ویڈیو'
        verbose_name_plural = 'ویڈیوز'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        # Strip HTML tags from content
        self.content = strip_tags(self.content)
        super().save(*args, **kwargs)


class VideoPlaylist(models.Model):
    """Video playlist model"""
    
    title = models.CharField(max_length=200, verbose_name='عنوان')
    slug = models.SlugField(unique=True, verbose_name='سلگ')
    description = models.TextField(blank=True, verbose_name='تفصیل')
    cover_image = models.ImageField(upload_to='videos/playlists/', blank=True, verbose_name='سرورق')
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
