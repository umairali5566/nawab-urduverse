"""
Sitemaps for Nawab Urdu Academy - SEO Optimization
"""

from django.contrib.sitemaps import Sitemap
from django.db.utils import OperationalError, ProgrammingError
from django.urls import reverse

from novels.models import Novel, Chapter
from stories.models import Story
from poetry.models import Poetry
from quotes.models import Quote
from blog.models import BlogPost
from videos.models import Video
from .models import Author


def _safe_items(queryset):
    try:
        return list(queryset)
    except (OperationalError, ProgrammingError):
        return []


class NovelSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8
    
    def items(self):
        return _safe_items(Novel.objects.filter(is_published=True))
    
    def lastmod(self, obj):
        return getattr(obj, 'updated_at', None) or getattr(obj, 'created_at', None)
    
    def location(self, obj):
        return obj.get_absolute_url()


class ChapterSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return _safe_items(Chapter.objects.filter(is_published=True, novel__is_published=True))

    def lastmod(self, obj):
        return getattr(obj, 'updated_at', None) or getattr(obj, 'created_at', None)

    def location(self, obj):
        return obj.get_absolute_url()


class StorySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7
    
    def items(self):
        return _safe_items(Story.objects.filter(is_published=True))
    
    def lastmod(self, obj):
        return getattr(obj, 'updated_at', None) or getattr(obj, 'created_at', None)
    
    def location(self, obj):
        return obj.get_absolute_url()


class PoetrySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7
    
    def items(self):
        return _safe_items(Poetry.objects.filter(is_published=True))
    
    def lastmod(self, obj):
        return getattr(obj, 'updated_at', None) or getattr(obj, 'created_at', None)
    
    def location(self, obj):
        return obj.get_absolute_url()


class QuoteSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.6
    
    def items(self):
        return _safe_items(Quote.objects.filter(is_published=True))
    
    def lastmod(self, obj):
        return obj.created_at
    
    def location(self, obj):
        return obj.get_absolute_url()


class BlogSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7
    
    def items(self):
        return _safe_items(BlogPost.objects.filter(is_published=True))
    
    def lastmod(self, obj):
        return getattr(obj, 'updated_at', None) or getattr(obj, 'created_at', None)
    
    def location(self, obj):
        return obj.get_absolute_url()


class VideoSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.6
    
    def items(self):
        return _safe_items(Video.objects.filter(is_published=True))
    
    def lastmod(self, obj):
        return obj.created_at
    
    def location(self, obj):
        return obj.get_absolute_url()


class AuthorSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5
    
    def items(self):
        return _safe_items(Author.objects.filter(is_active=True))
    
    def lastmod(self, obj):
        return getattr(obj, 'updated_at', None) or getattr(obj, 'created_at', None)
    
    def location(self, obj):
        return reverse('author_detail', kwargs={'slug': obj.slug})


class StaticViewSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5
    
    def items(self):
        return [
            'home',
            'about',
            'contact',
            'author_list',
            'privacy_policy',
            'terms_of_service',
        ]
    
    def location(self, item):
        return reverse(item)
