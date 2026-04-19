"""
Quotes Models for Nawab Urdu Academy
"""

from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.html import strip_tags

from core.models import Author, Category


class Quote(models.Model):
    """Quote model"""
    
    # Class attribute for quote type choices
    QUOTE_TYPES = (
        ('general', 'عام'),
        ('islamic', 'اسلامی'),
        ('motivational', 'ح副总 / مشوق'),
        ('poetic', 'شاعری'),
        ('romantic', 'رومانی'),
        ('philosophical', 'فلسفیانہ'),
        ('wisdom', 'حکمت'),
        ('friendship', 'دوستی'),
        ('life', 'زندگی'),
        ('success', 'کامیابی'),
    )

    title = models.CharField(max_length=300, verbose_name='عنوان')
    slug = models.SlugField(unique=True, verbose_name='سلگ')
    text = models.TextField(verbose_name='مواد')
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='quotes', verbose_name='مصنف')
    
    # Many-to-many relationship with categories
    categories = models.ManyToManyField(
        Category, 
        related_name='quote_categories', 
        blank=True, 
        verbose_name='زمرہ جات'
    )
    
    # Keep existing category FK for backward compatibility
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name='زمرہ'
    )
    
    quote_type = models.CharField(
        max_length=20, 
        choices=QUOTE_TYPES, 
        default='general', 
        verbose_name='قسم'
    )
    
    is_featured = models.BooleanField(default=False, verbose_name='نمایں')
    is_published = models.BooleanField(default=True, verbose_name='شائع شدہ')
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='شائع ہونے کی تاریخ')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Engagement counters
    views_count = models.PositiveIntegerField(default=0, verbose_name='مشاہدات')
    likes_count = models.PositiveIntegerField(default=0, verbose_name='پسندیدگی')
    shares_count = models.PositiveIntegerField(default=0, verbose_name='شیئرز')
    
    # SEO fields
    meta_title = models.CharField(max_length=200, blank=True, default='', verbose_name='میٹا عنوان')
    meta_description = models.TextField(blank=True, default='', verbose_name='میٹا تفصیل')
    
    # Design customization fields
    background_image = models.ImageField(
        upload_to='quotes/backgrounds/', 
        blank=True, 
        null=True, 
        verbose_name='پس منظر کی تصویر'
    )
    text_color = models.CharField(
        max_length=20, 
        blank=True, 
        default='#000000', 
        verbose_name='متن کا رنگ'
    )
    background_color = models.CharField(
        max_length=20, 
        blank=True, 
        default='#FFFFFF', 
        verbose_name='پس منظر کا رنگ'
    )
    font_size = models.PositiveIntegerField(
        default=18, 
        verbose_name='فونٹ سائز'
    )

    class Meta:
        verbose_name = 'اقتباس'
        verbose_name_plural = 'اقتباسات'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        # Strip HTML tags from text
        self.text = strip_tags(self.text)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('quote_detail', kwargs={'slug': self.slug})


class QuoteCollection(models.Model):
    """Quote collection model"""
    
    title = models.CharField(max_length=200, verbose_name='عنوان')
    slug = models.SlugField(unique=True, verbose_name='سلگ')
    description = models.TextField(blank=True, verbose_name='تفصیل')
    cover_image = models.ImageField(upload_to='quotes/collections/', blank=True, null=True, verbose_name='سرورق')
    quotes = models.ManyToManyField(Quote, related_name='collections', verbose_name='اقتباسات')
    is_published = models.BooleanField(default=True, verbose_name='شائع شدہ')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'اقتباسات کا مجموعہ'
        verbose_name_plural = 'اقتباسات کے مجموعے'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('quote_collection_detail', kwargs={'slug': self.slug})
