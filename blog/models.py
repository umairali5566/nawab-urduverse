"""
Blog Models for Nawab Urdu Academy
"""

from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.html import strip_tags
from ckeditor_uploader.fields import RichTextUploadingField

from core.models import Author, BaseContentModel, Category


class BlogPost(models.Model):
    """Blog post model"""

    title = models.CharField(max_length=300, verbose_name='عنوان')
    slug = models.SlugField(unique=True, verbose_name='سلگ')
    content = models.TextField(verbose_name='مواد')
    featured_image = models.ImageField(upload_to='blog/featured/', blank=True, null=True, verbose_name='نمایاں تصویر')
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='blog_posts', verbose_name='مصنف')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='زمرہ')
    is_published = models.BooleanField(default=True, verbose_name='شائع شدہ')
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='شائع ہونے کی تاریخ')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'بلاگ پوسٹ'
        verbose_name_plural = 'بلاگ پوسٹس'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        # Strip HTML tags from content
        self.content = strip_tags(self.content)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog_detail", kwargs={"slug": self.slug})


class BlogCategory(models.Model):
    """Blog category model (additional to main Category)"""
    
    name = models.CharField(max_length=100, verbose_name='نام')
    slug = models.SlugField(unique=True, verbose_name='سلگ')
    description = models.TextField(blank=True, verbose_name='تفصیل')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'بلاگ زمرہ'
        verbose_name_plural = 'بلاگ زمرہ جات'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)
