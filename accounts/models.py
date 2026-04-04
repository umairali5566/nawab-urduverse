"""
Accounts Models for Nawab UrduVerse
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    """Custom User model"""
    
    GENDER_CHOICES = (
        ('male', 'مرد'),
        ('female', 'خاتون'),
        ('other', 'دیگر'),
    )
    
    email = models.EmailField(unique=True, verbose_name='ای میل')
    display_name = models.CharField(max_length=100, blank=True, verbose_name='ظاہری نام')
    bio = models.TextField(blank=True, verbose_name='سوانح حیات')
    avatar = models.ImageField(upload_to='avatars/', blank=True, verbose_name='اوتار')
    phone = models.CharField(max_length=20, blank=True, verbose_name='فون نمبر')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, verbose_name='جنس')
    birth_date = models.DateField(null=True, blank=True, verbose_name='تاریخ پیدائش')
    city = models.CharField(max_length=100, blank=True, verbose_name='شہر')
    country = models.CharField(max_length=100, blank=True, verbose_name='ملک')
    website = models.URLField(blank=True, verbose_name='ویب سائٹ')
    facebook = models.URLField(blank=True, verbose_name='فیس بک')
    twitter = models.URLField(blank=True, verbose_name='ٹویٹر')
    instagram = models.URLField(blank=True, verbose_name='انسٹاگرام')
    is_author = models.BooleanField(default=False, verbose_name='مصنف')
    is_verified = models.BooleanField(default=False, verbose_name='تصدیق شدہ')
    dark_mode = models.BooleanField(default=False, verbose_name='ڈارک موڈ')
    email_notifications = models.BooleanField(default=True, verbose_name='ای میل نوٹیفکیشنز')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'صارف'
        verbose_name_plural = 'صارفین'
        verbose_name_plural = 'صارفین'
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.display_name or self.username
    
    def get_absolute_url(self):
        return reverse('profile', kwargs={'username': self.username})
    
    def get_full_name(self):
        return self.display_name or f"{self.first_name} {self.last_name}".strip() or self.username
    
    def get_bookmarks_count(self):
        from core.models import Bookmark
        return Bookmark.objects.filter(user=self).count()
    
    def get_comments_count(self):
        from core.models import Comment
        return Comment.objects.filter(user=self).count()


    def get_likes_count(self):
        from core.models import ContentLike
        return ContentLike.objects.filter(user=self).count()

    def get_unread_notifications_count(self):
        from core.models import Notification
        return Notification.objects.filter(user=self, is_read=False).count()

    def has_active_membership(self):
        membership = getattr(self, 'membership', None)
        return bool(membership and membership.is_active_membership)


class UserActivity(models.Model):
    """Track user activities"""
    
    ACTIVITY_TYPES = (
        ('login', 'لاگ ان'),
        ('logout', 'لاگ آؤٹ'),
        ('view', 'مشاہدہ'),
        ('bookmark', 'بک مارک'),
        ('comment', 'تبصرہ'),
        ('share', 'شیئر'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='صارف')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES, verbose_name='سرگرمی کی قسم')
    description = models.CharField(max_length=255, blank=True, verbose_name='تفصیل')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='آئی پی ایڈریس')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'صارف کی سرگرمی'
        verbose_name_plural = 'صارفین کی سرگرمیاں'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.username} - {self.activity_type}'
