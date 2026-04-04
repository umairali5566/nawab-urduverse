"""
Core Models for Nawab UrduVerse
"""

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from django.utils.html import strip_tags

from ckeditor_uploader.fields import RichTextUploadingField


ENGAGEMENT_CONTENT_TYPES = (
    ('novel', 'ناول'),
    ('story', 'کہانی'),
    ('poetry', 'شاعری'),
    ('quote', 'اقتباس'),
    ('blog', 'بلاگ'),
    ('video', 'ویڈیو'),
)


class Category(models.Model):
    """Category model for all content types"""
    
    CATEGORY_TYPES = (
        ('novel', 'ناول'),
        ('story', 'کہانی'),
        ('poetry', 'شاعری'),
        ('quote', 'اقتباس'),
        ('blog', 'بلاگ'),
        ('video', 'ویڈیو'),
    )
    
    name = models.CharField(max_length=100, verbose_name='نام')
    name_english = models.CharField(max_length=100, blank=True, verbose_name='انگریزی نام')
    slug = models.SlugField(unique=True, verbose_name='سلگ')
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES, verbose_name='قسم')
    description = models.TextField(blank=True, verbose_name='تفصیل')
    image = models.ImageField(upload_to='categories/', blank=True, verbose_name='تصویر')
    color = models.CharField(max_length=7, default='#6c757d', verbose_name='رنگ')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'زمرہ'
        verbose_name_plural = 'زمرہ جات'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_english or self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})


class Tag(models.Model):
    """Tag model for content"""
    
    name = models.CharField(max_length=50, verbose_name='نام')
    slug = models.SlugField(unique=True, verbose_name='سلگ')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'ٹیگ'
        verbose_name_plural = 'ٹیگز'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Author(models.Model):
    """Author model for writers and poets"""

    name = models.CharField(max_length=200, verbose_name='نام')
    slug = models.SlugField(unique=True, verbose_name='سلگ')
    is_featured = models.BooleanField(default=False, verbose_name='نمایاں')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'مصنف'
        verbose_name_plural = 'مصنفین'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('author_detail', kwargs={'slug': self.slug})

    @property
    def published_content_total(self):
        related_sets = (
            getattr(self, 'poetry', None),
            getattr(self, 'blog_posts', None),
            getattr(self, 'videos', None),
            getattr(self, 'novels', None),
            getattr(self, 'quotes', None),
            getattr(self, 'stories', None),
        )
        total = 0
        for related in related_sets:
            if related is None:
                continue
            queryset = related.all()
            if hasattr(queryset.model, 'is_published'):
                queryset = queryset.filter(is_published=True)
            total += queryset.count()
        return total



class Story(models.Model):
    """Story model"""

    title = models.CharField(max_length=300, verbose_name='عنوان')
    slug = models.SlugField(unique=True, verbose_name='سلگ')
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='core_stories', verbose_name='مصنف')
    content = RichTextUploadingField(verbose_name='مواد')
    cover_image = models.ImageField(upload_to='stories/covers/', blank=True, verbose_name='سرورق کی تصویر')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'category_type': 'story'}, related_name='core_story_set', verbose_name='زمرہ')
    is_published = models.BooleanField(default=True, verbose_name='شائع شدہ')
    views_count = models.PositiveIntegerField(default=0, verbose_name='مشاہدات')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'کہانی'
        verbose_name_plural = 'کہانیاں'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('story_detail', kwargs={'slug': self.slug})


class Comment(models.Model):
    """Comment model for all content types"""
    
    CONTENT_TYPES = (
        ('novel', 'ناول'),
        ('story', 'کہانی'),
        ('poetry', 'شاعری'),
        ('quote', 'اقتباس'),
        ('blog', 'بلاگ'),
        ('video', 'ویڈیو'),
    )
    
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, verbose_name='صارف')
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES, verbose_name='مواد کی قسم')
    object_id = models.PositiveIntegerField(verbose_name='آبجیکٹ آئی ڈی')
    text = models.TextField(verbose_name='تبصرہ')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name='والدین')
    is_approved = models.BooleanField(default=True, verbose_name='منظور شدہ')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'تبصرہ'
        verbose_name_plural = 'تبصرے'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.username} - {self.content_type}'


class Bookmark(models.Model):
    """Bookmark model for users to save content"""
    
    CONTENT_TYPES = (
        ('novel', 'ناول'),
        ('story', 'کہانی'),
        ('poetry', 'شاعری'),
        ('quote', 'اقتباس'),
        ('blog', 'بلاگ'),
        ('video', 'ویڈیو'),
    )
    
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, verbose_name='صارف')
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES, verbose_name='مواد کی قسم')
    object_id = models.PositiveIntegerField(verbose_name='آبجیکٹ آئی ڈی')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'بک مارک'
        verbose_name_plural = 'بک مارکس'
        unique_together = ['user', 'content_type', 'object_id']
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.username} - {self.content_type}'


class ReadingProgress(models.Model):
    """Track user reading progress for novels"""
    
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, verbose_name='صارف')
    novel = models.ForeignKey('novels.Novel', on_delete=models.CASCADE, verbose_name='ناول')
    chapter = models.ForeignKey('novels.Chapter', on_delete=models.CASCADE, verbose_name='باب')
    progress_percent = models.PositiveIntegerField(default=0, verbose_name='پیش رفت فیصد')
    last_read_at = models.DateTimeField(auto_now=True, verbose_name='آخری مطالعہ')
    
    class Meta:
        verbose_name = 'مطالعہ کی پیش رفت'
        verbose_name_plural = 'مطالعہ کی پیش رفت'
        ordering = ['-last_read_at']
    
    def __str__(self):
        return f'{self.user.username} - {self.novel.title}'


class SiteSetting(models.Model):
    """Site settings model"""
    
    key = models.CharField(max_length=100, unique=True, verbose_name='کلید')
    value = models.TextField(verbose_name='قدر')
    description = models.CharField(max_length=255, blank=True, verbose_name='تفصیل')
    
    class Meta:
        verbose_name = 'سائٹ سیٹنگ'
        verbose_name_plural = 'سائٹ سیٹنگز'
    
    def __str__(self):
        return self.key


class NewsletterSubscriber(models.Model):
    """Newsletter subscribers"""
    
    email = models.EmailField(unique=True, verbose_name='ای میل')
    name = models.CharField(max_length=100, blank=True, verbose_name='نام')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    subscribed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'نیوز لیٹر سبسکرائبر'
        verbose_name_plural = 'نیوز لیٹر سبسکرائبرز'
        ordering = ['-subscribed_at']
    
    def __str__(self):
        return self.email


class ContactMessage(models.Model):
    """Contact form messages"""
    
    name = models.CharField(max_length=200, verbose_name='نام')
    email = models.EmailField(verbose_name='ای میل')
    subject = models.CharField(max_length=200, verbose_name='موضوع')
    message = models.TextField(verbose_name='پیغام')
    is_read = models.BooleanField(default=False, verbose_name='پڑھا گیا')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'رابطہ پیغام'
        verbose_name_plural = 'رابطہ پیغامات'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.name} - {self.subject}'




class ContentLike(models.Model):
    """Generic like model shared across all content types."""

    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, verbose_name='صارف')
    content_type = models.CharField(max_length=20, choices=ENGAGEMENT_CONTENT_TYPES, verbose_name='مواد کی قسم')
    object_id = models.PositiveIntegerField(verbose_name='آبجیکٹ آئی ڈی')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'پسند'
        verbose_name_plural = 'پسندیدگیاں'
        ordering = ['-created_at']
        unique_together = ['user', 'content_type', 'object_id']

    def __str__(self):
        return f'{self.user} liked {self.content_type}:{self.object_id}'


class Notification(models.Model):
    """User notifications for engagement and account events."""

    NOTIFICATION_TYPES = (
        ('like', 'لائک'),
        ('comment', 'تبصرہ'),
        ('follow', 'فالو'),
        ('membership', 'ممبرشپ'),
        ('system', 'سسٹم'),
    )

    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='صارف',
    )
    actor = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='triggered_notifications',
        verbose_name='ایکٹر',
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, verbose_name='قسم')
    title = models.CharField(max_length=120, verbose_name='عنوان')
    message = models.CharField(max_length=255, verbose_name='پیغام')
    link = models.CharField(max_length=255, blank=True, verbose_name='لنک')
    content_type = models.CharField(
        max_length=20,
        choices=ENGAGEMENT_CONTENT_TYPES,
        blank=True,
        verbose_name='مواد کی قسم',
    )
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name='آبجیکٹ آئی ڈی')
    is_read = models.BooleanField(default=False, verbose_name='پڑھ لیا گیا')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'نوٹیفکیشن'
        verbose_name_plural = 'نوٹیفکیشنز'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} - {self.title}'


class PremiumPlan(models.Model):
    """Premium membership plans for monetization."""

    name = models.CharField(max_length=100, verbose_name='منصوبہ')
    slug = models.SlugField(unique=True, verbose_name='سلگ')
    description = models.TextField(blank=True, verbose_name='تفصیل')
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='قیمت')
    billing_cycle_days = models.PositiveIntegerField(default=30, verbose_name='بلنگ دن')
    features = models.TextField(blank=True, verbose_name='خصوصیات')
    highlight_text = models.CharField(max_length=80, blank=True, verbose_name='ہائی لائٹ')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'پریمیم پلان'
        verbose_name_plural = 'پریمیم پلانز'
        ordering = ['price', 'billing_cycle_days']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def feature_list(self):
        return [item.strip() for item in (self.features or '').splitlines() if item.strip()]


class UserMembership(models.Model):
    """Membership state for premium access."""

    STATUS_CHOICES = (
        ('free', 'فری'),
        ('active', 'فعال'),
        ('expired', 'ختم شدہ'),
        ('cancelled', 'منسوخ'),
    )

    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='membership',
        verbose_name='صارف',
    )
    plan = models.ForeignKey(
        PremiumPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='memberships',
        verbose_name='پلان',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='free', verbose_name='حالت')
    starts_at = models.DateTimeField(null=True, blank=True, verbose_name='آغاز')
    ends_at = models.DateTimeField(null=True, blank=True, verbose_name='اختتام')
    auto_renew = models.BooleanField(default=False, verbose_name='خودکار تجدید')
    notes = models.CharField(max_length=255, blank=True, verbose_name='نوٹس')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'صارف ممبرشپ'
        verbose_name_plural = 'صارف ممبرشپس'
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.user} - {self.status}'

    @property
    def is_active_membership(self):
        if self.status != 'active':
            return False
        if self.ends_at and self.ends_at <= timezone.now():
            return False
        return True
