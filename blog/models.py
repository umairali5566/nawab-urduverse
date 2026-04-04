"""
Blog Models for Nawab Urdu Academy
"""

from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.html import strip_tags
from ckeditor_uploader.fields import RichTextUploadingField

from core.models import Author, Category


class BlogPost(models.Model):
    """Blog post model"""
    
    POST_STATUS = (
        ('draft', 'ڈرافٹ'),
        ('published', 'شائع شدہ'),
        ('archived', 'محفوظ شدہ'),
    )
    
    title = models.CharField(max_length=300, verbose_name='عنوان')
    slug = models.SlugField(unique=True, verbose_name='سلگ')
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='blog_posts', verbose_name='مصنف')
    excerpt = models.TextField(blank=True, verbose_name='خلاصہ')
    content = RichTextUploadingField(verbose_name='مواد')
    featured_image = models.ImageField(upload_to='blog/', blank=True, verbose_name='نمایاں تصویر')
    categories = models.ManyToManyField(Category, limit_choices_to={'category_type': 'blog'}, verbose_name='زمرہ جات')
    tags = models.CharField(max_length=500, blank=True, verbose_name='ٹیگز')
    status = models.CharField(max_length=20, choices=POST_STATUS, default='draft', verbose_name='حالت')
    is_published = models.BooleanField(default=False, verbose_name='شائع شدہ')
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
    canonical_url = models.URLField(blank=True, verbose_name='کینونیکل یو آر ایل')
    
    class Meta:
        verbose_name = 'بلاگ پوسٹ'
        verbose_name_plural = 'بلاگ پوسٹس'
        ordering = ['-published_at', '-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

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
        return reverse('blog_detail', kwargs={'slug': self.slug})
    
    def get_related_posts(self):
        """Get related blog posts"""
        return BlogPost.objects.filter(
            categories__in=self.categories.all(),
            is_published=True
        ).exclude(id=self.id).distinct()[:4]

    @property
    def thumbnail(self):
        return self.featured_image

    @property
    def author_name(self):
        return self.author.name


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
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
