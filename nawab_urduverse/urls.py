"""
Nawab Urdu Academy - URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from ai_features import views as ai_views
from core import views as core_views
from poetry import views as poetry_views
from core.sitemaps import (
    NovelSitemap, ChapterSitemap, StorySitemap, PoetrySitemap,
    QuoteSitemap, BlogSitemap, VideoSitemap,
    AuthorSitemap, StaticViewSitemap
)
from nawab_urduverse import views

sitemaps = {
    'novels': NovelSitemap,
    'chapters': ChapterSitemap,
    'stories': StorySitemap,
    'poetry': PoetrySitemap,
    'quotes': QuoteSitemap,
    'blog': BlogSitemap,
    'videos': VideoSitemap,
    'authors': AuthorSitemap,
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('static/sw.js', core_views.service_worker, name='service_worker'),
    path('', include('core.urls')),
    path('home/', views.home, name='home'),
    path('ai-studio/', poetry_views.ai_studio, name='ai_studio'),
    path('ai/', include('ai_features.urls')),
    path('accounts/', include('accounts.urls')),
    path('novels/', include('novels.urls')),
    path('stories/', include('stories.urls')),
    path('poetry/', include('poetry.urls')),
    path('quotes/', include('quotes.urls')),
    path('blog/', include('blog.urls')),
    path('videos/', include('videos.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('dashboard/', include('dashboard.urls')),
    path('admin-upload/', views.admin_upload, name='admin_upload'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
