"""
Stories Models for Nawab UrduVerse
"""

from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField

from core.models import Author, Category


class Story(models.Model):
    """Story model"""
    
    title = models.CharField(max_length=300, verbose_name='عنوان')
    slug = models.SlugField(unique=True, verbose_name='سلگ')
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='stories', verbose_name='مصنف')
    content = RichTextUploadingField(verbose_name='مواد')
    excerpt = models.TextField(blank=True, verbose_name='خلاصہ')
    featured_image = models.ImageField(upload_to='stories/', blank=True, verbose_name='نمایاں تصویر')
    categories = models.ManyToManyField(Category, limit_choices_to={'category_type': 'story'}, verbose_name='زمرہ جات')
    tags = models.CharField(max_length=500, blank=True, verbose_name='ٹیگز')
    is_published = models.BooleanField(default=True, verbose_name='شائع شدہ')
    is_featured = models.BooleanField(default=False, verbose_name='نمایاں')
    views_count = models.PositiveIntegerField(default=0, verbose_name='مشاہدات')
    likes_count = models.PositiveIntegerField(default=0, verbose_name='پسندیدگی')
    shares_count = models.PositiveIntegerField(default=0, verbose_name='شیئرز')
    reading_time = models.PositiveIntegerField(default=0, verbose_name='پڑھنے کا وقت (منٹ)')
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='شائع ہونے کی تاریخ')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # SEO Fields
    meta_title = models.CharField(max_length=200, blank=True, verbose_name='میٹا عنوان')
    meta_description = models.TextField(blank=True, verbose_name='میٹا تفصیل')
    meta_keywords = models.CharField(max_length=500, blank=True, verbose_name='میٹا کی ورڈز')
    
    class Meta:
        verbose_name = 'کہانی'
        verbose_name_plural = 'کہانیاں'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Calculate reading time
        if self.content:
            word_count = len(self.content.split())
            self.reading_time = max(1, word_count // 200)
        
        # Generate excerpt if not provided
        if not self.excerpt and self.content:
            self.excerpt = self.content[:300] + '...' if len(self.content) > 300 else self.content
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('story_detail', kwargs={'slug': self.slug})
