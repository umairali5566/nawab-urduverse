"""
Quotes Models for Nawab Urdu Academy
"""

from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from core.models import Author, BaseContentModel, Category


class Quote(BaseContentModel):
    """Quote model"""

    QUOTE_TYPES = (
        ('islamic', 'اسلامی'),
        ('motivational', 'حوصلہ افزائی'),
        ('love', 'محبت'),
        ('life', 'زندگی'),
        ('friendship', 'دوستی'),
        ('success', 'کامیابی'),
        ('wisdom', 'دانش'),
        ('funny', 'مزاحیہ'),
        ('sad', 'اداسی'),
        ('poetry', 'شاعری'),
    )

    title = models.CharField(max_length=300, blank=True, default='', verbose_name='عنوان')
    text = models.TextField(verbose_name='اقتباس')
    quote_type = models.CharField(max_length=20, choices=QUOTE_TYPES, default='motivational', verbose_name='اقتباس کی قسم')
    background_image = models.ImageField(upload_to='quotes/backgrounds/', blank=True, verbose_name='پس منظر کی تصویر')
    text_color = models.CharField(max_length=7, default='#FFFFFF', verbose_name='متن کا رنگ')
    background_color = models.CharField(max_length=7, default='#1a1a2e', verbose_name='پس منظر کا رنگ')
    font_size = models.PositiveSmallIntegerField(default=24, verbose_name='فونٹ سائز')
    categories = models.ManyToManyField(Category, limit_choices_to={'category_type': 'quote'}, verbose_name='زمرہ جات')
    tags = models.CharField(max_length=500, blank=True, verbose_name='ٹیگز')

    class Meta(BaseContentModel.Meta):
        verbose_name = 'اقتباس'
        verbose_name_plural = 'اقتباسات'

    def __str__(self):
        return self.text[:100] + '...' if len(self.text) > 100 else self.text

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.text[:50])
            self.slug = base_slug
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('quote_detail', kwargs={'slug': self.slug})
    
    def get_share_text(self):
        """Get text for social sharing"""
        return f'"{self.text}" - {self.author.name}'

    @property
    def author_name(self):
        return self.author.name


class QuoteCollection(models.Model):
    """Quote collection model"""
    
    title = models.CharField(max_length=200, verbose_name='عنوان')
    slug = models.SlugField(unique=True, verbose_name='سلگ')
    description = models.TextField(blank=True, verbose_name='تفصیل')
    cover_image = models.ImageField(upload_to='quotes/collections/', blank=True, verbose_name='سرورق')
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
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('quote_collection_detail', kwargs={'slug': self.slug})
