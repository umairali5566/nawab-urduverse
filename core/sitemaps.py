"""
Sitemaps for Nawab UrduVerse - SEO Optimization
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from novels.models import Novel, Chapter
from stories.models import Story
from poetry.models import Poetry
from quotes.models import Quote
from blog.models import BlogPost
from videos.models import Video
from .models import Author


class NovelSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8
    
    def items(self):
        return Novel.objects.filter(is_published=True)
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return obj.get_absolute_url()


class ChapterSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Chapter.objects.filter(is_published=True, novel__is_published=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class StorySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7
    
    def items(self):
        return Story.objects.filter(is_published=True)
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return obj.get_absolute_url()


class PoetrySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7
    
    def items(self):
        return Poetry.objects.filter(is_published=True)
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return obj.get_absolute_url()


class QuoteSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.6
    
    def items(self):
        return Quote.objects.filter(is_published=True)
    
    def lastmod(self, obj):
        return obj.created_at
    
    def location(self, obj):
        return obj.get_absolute_url()


class BlogSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7
    
    def items(self):
        return BlogPost.objects.filter(is_published=True)
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return obj.get_absolute_url()


class VideoSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.6
    
    def items(self):
        return Video.objects.filter(is_published=True)
    
    def lastmod(self, obj):
        return obj.created_at
    
    def location(self, obj):
        return obj.get_absolute_url()


class AuthorSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5
    
    def items(self):
        return Author.objects.filter(is_active=True)
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return obj.get_absolute_url()


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
