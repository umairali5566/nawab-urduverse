"""
Novels Models for Nawab Urdu Academy
"""

from django.db import models
from django.db.models.signals import post_delete
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.text import slugify
from django.dispatch import receiver

from core.models import Author, Category


class Novel(models.Model):
    """Novel model"""

    title = models.CharField(max_length=300, verbose_name='عنوان')
    slug = models.SlugField(unique=True, verbose_name='سلگ')
    content = models.TextField(verbose_name='مواد')
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name='novels',
        null=True,
        blank=True,
        verbose_name='مصنف',
    )
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='زمرہ')
    total_chapters = models.PositiveIntegerField(default=0, verbose_name='کل ابواب')
    is_published = models.BooleanField(default=True, verbose_name='شائع شدہ')
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='شائع ہونے کی تاریخ')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'ناول'
        verbose_name_plural = 'ناولز'
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

    def update_chapter_count(self):
        """Update the total chapters count."""
        self.total_chapters = self.chapters.filter(is_published=True).count()
        self.save(update_fields=['total_chapters'])

    def get_absolute_url(self):
        return reverse('novel_detail', kwargs={'slug': self.slug})


class Chapter(models.Model):
    """Chapter model for novels"""
    
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name='chapters', verbose_name='ناول')
    chapter_number = models.PositiveIntegerField(verbose_name='باب نمبر')
    title = models.CharField(max_length=300, verbose_name='عنوان')
    slug = models.SlugField(verbose_name='سلگ')
    content = models.TextField(verbose_name='مواد')
    is_published = models.BooleanField(default=True, verbose_name='شائع شدہ')
    is_premium = models.BooleanField(default=False, verbose_name='پریمیم')
    views_count = models.PositiveIntegerField(default=0, verbose_name='مشاہدات')
    word_count = models.PositiveIntegerField(default=0, verbose_name='الفاظ کی تعداد')
    reading_time = models.PositiveIntegerField(default=0, verbose_name='پڑھنے کا وقت (منٹ)')
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='شائع ہونے کی تاریخ')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # SEO Fields
    meta_title = models.CharField(max_length=200, blank=True, verbose_name='میٹا عنوان')
    meta_description = models.TextField(blank=True, verbose_name='میٹا تفصیل')
    
    class Meta:
        verbose_name = 'باب'
        verbose_name_plural = 'ابواب'
        ordering = ['chapter_number']
        unique_together = ['novel', 'chapter_number']
    
    def __str__(self):
        return f'{self.novel.title} - باب {self.chapter_number}: {self.title}'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f'chapter-{self.chapter_number}-{self.title}', allow_unicode=True)
        
        if self.content:
            self.word_count = len(self.content.split())
            self.reading_time = max(1, self.word_count // 200)
        
        super().save(*args, **kwargs)
        
        self.novel.update_chapter_count()
    
    def get_absolute_url(self):
        return reverse('chapter_detail', kwargs={
            'novel_slug': self.novel.slug,
            'chapter_slug': self.slug
        })
    
    def get_previous_chapter(self):
        return Chapter.objects.filter(
            novel=self.novel,
            chapter_number__lt=self.chapter_number,
            is_published=True
        ).order_by('-chapter_number').first()
    
    def get_next_chapter(self):
        return Chapter.objects.filter(
            novel=self.novel,
            chapter_number__gt=self.chapter_number,
            is_published=True
        ).order_by('chapter_number').first()


@receiver(post_delete, sender=Chapter)
def update_chapter_count_after_delete(sender, instance, **kwargs):
    """Keep Novel.total_chapters synced when chapters are deleted."""
    if not instance.novel_id:
        return
    total = Chapter.objects.filter(novel_id=instance.novel_id, is_published=True).count()
    Novel.objects.filter(pk=instance.novel_id).update(total_chapters=total)


class NovelReview(models.Model):
    """Novel reviews and ratings"""
    
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name='reviews', verbose_name='ناول')
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, verbose_name='صارف')
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name='ریٹنگ')
    review_text = models.TextField(verbose_name='جائزہ')
    is_approved = models.BooleanField(default=True, verbose_name='منظور شدہ')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'جائزہ'
        verbose_name_plural = 'جائزے'
        ordering = ['-created_at']
        unique_together = ['novel', 'user']
    
    def __str__(self):
        return f'{self.user.username} - {self.novel.title} ({self.rating} ستارے)'
