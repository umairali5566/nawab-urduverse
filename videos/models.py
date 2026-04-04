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
    
    VIDEO_TYPES = (
        ('poetry', 'شاعری'),
        ('story', 'کہانی'),
        ('novel', 'ناول'),
        ('interview', 'انٹرویو'),
        ('documentary', 'دستاویزی'),
        ('other', 'دیگر'),
    )
    
    PLATFORM_CHOICES = (
        ('youtube', 'یوٹیوب'),
        ('vimeo', 'ویمیو'),
        ('dailymotion', 'ڈیلی موشن'),
        ('facebook', 'فیس بک'),
        ('local', 'مقامی'),
    )
    
    title = models.CharField(max_length=300, verbose_name='عنوان')
    slug = models.SlugField(unique=True, verbose_name='سلگ')
    description = models.TextField(blank=True, verbose_name='تفصیل')
    video_type = models.CharField(max_length=20, choices=VIDEO_TYPES, default='poetry', verbose_name='ویڈیو کی قسم')
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default='youtube', verbose_name='پلیٹ فارم')
    video_id = models.CharField(max_length=100, blank=True, verbose_name='ویڈیو آئی ڈی')
    video_url = models.URLField(blank=True, verbose_name='ویڈیو یو آر ایل')
    youtube_link = models.URLField(blank=True, verbose_name='یوٹیوب لنک')
    video_file = models.FileField(upload_to='videos/uploads/', blank=True, verbose_name='ویڈیو فائل')
    thumbnail = models.ImageField(upload_to='videos/thumbnails/', blank=True, verbose_name='تھمب نیل')
    duration = models.CharField(max_length=20, blank=True, verbose_name='دورانیہ')
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='videos', verbose_name='مصنف', null=True, blank=True)
    categories = models.ManyToManyField(Category, limit_choices_to={'category_type': 'video'}, verbose_name='زمرہ جات')
    tags = models.CharField(max_length=500, blank=True, verbose_name='ٹیگز')
    is_published = models.BooleanField(default=True, verbose_name='شائع شدہ')
    is_featured = models.BooleanField(default=False, verbose_name='نمایاں')
    views_count = models.PositiveIntegerField(default=0, verbose_name='مشاہدات')
    likes_count = models.PositiveIntegerField(default=0, verbose_name='پسندیدگی')
    shares_count = models.PositiveIntegerField(default=0, verbose_name='شیئرز')
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='شائع ہونے کی تاریخ')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # SEO Fields
    meta_title = models.CharField(max_length=200, blank=True, verbose_name='میٹا عنوان')
    meta_description = models.TextField(blank=True, verbose_name='میٹا تفصیل')
    
    class Meta:
        verbose_name = 'ویڈیو'
        verbose_name_plural = 'ویڈیوز'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

    def clean(self):
        if not any([self.video_file, self.youtube_link, self.video_url, self.video_id]):
            raise ValidationError('Upload a video file or provide a YouTube/video link.')
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        if self.video_file:
            self.platform = 'local'
            self.video_id = self.video_id or slugify(self.title)[:100] or 'local-video'
            self.video_url = ''
            self.youtube_link = ''
        else:
            source_url = self.youtube_link or self.video_url
            if source_url:
                platform, extracted_id = self._extract_platform_video_id(source_url)
                if platform:
                    self.platform = platform
                if extracted_id:
                    self.video_id = extracted_id
                self.video_url = source_url
                if self.platform == 'youtube':
                    self.youtube_link = source_url

            if not self.video_url and self.video_id:
                if self.platform == 'youtube':
                    self.video_url = f'https://www.youtube.com/watch?v={self.video_id}'
                    self.youtube_link = self.video_url
                elif self.platform == 'vimeo':
                    self.video_url = f'https://vimeo.com/{self.video_id}'
                elif self.platform == 'dailymotion':
                    self.video_url = f'https://www.dailymotion.com/video/{self.video_id}'
                elif self.platform == 'facebook':
                    self.video_url = self.video_url or self.youtube_link

        if not self.video_id:
            self.video_id = slugify(self.title)[:100] or 'video-item'
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('video_detail', kwargs={'slug': self.slug})
    
    def get_embed_url(self):
        """Get embed URL for the video"""
        if self.video_file:
            return self.video_file.url
        if self.platform == 'youtube':
            return f'https://www.youtube.com/embed/{self.video_id}'
        elif self.platform == 'vimeo':
            return f'https://player.vimeo.com/video/{self.video_id}'
        elif self.platform == 'dailymotion':
            return f'https://www.dailymotion.com/embed/video/{self.video_id}'
        return self.video_url
    
    def get_thumbnail_url(self):
        """Get thumbnail URL"""
        if self.thumbnail:
            return self.thumbnail.url
        elif self.platform == 'youtube':
            return f'https://img.youtube.com/vi/{self.video_id}/maxresdefault.jpg'
        return None

    @property
    def views(self):
        return self.views_count

    @property
    def author_name(self):
        return self.author.name if self.author else ''

    @staticmethod
    def _extract_platform_video_id(source_url):
        parsed = urlparse(source_url)
        host = (parsed.netloc or '').lower()
        path = parsed.path.strip('/')
        query = parse_qs(parsed.query)

        if 'youtu.be' in host:
            return 'youtube', path
        if 'youtube.com' in host:
            if 'watch' in path:
                return 'youtube', query.get('v', [''])[0]
            if path.startswith('shorts/'):
                return 'youtube', path.split('/', 1)[1]
            if path.startswith('embed/'):
                return 'youtube', path.split('/', 1)[1]
            return 'youtube', query.get('v', [''])[0]
        if 'vimeo.com' in host:
            return 'vimeo', path.split('/')[0]
        if 'dailymotion.com' in host:
            video_path = path.split('/')
            return 'dailymotion', video_path[-1] if video_path else ''
        if 'facebook.com' in host or 'fb.watch' in host:
            return 'facebook', path or parsed.netloc
        return '', ''


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
