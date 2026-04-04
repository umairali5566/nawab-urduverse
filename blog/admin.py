"""
Blog Admin Configuration for Nawab Urdu Academy
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import BlogCategory, BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = [
        'thumbnail_preview', 'title', 'author', 'status', 'is_published', 'is_featured',
        'views_count', 'likes_count', 'shares_count', 'reading_time', 'published_at'
    ]
    list_filter = ['status', 'is_published', 'is_featured', 'categories', 'created_at']
    search_fields = ['title', 'content', 'excerpt', 'author__name']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_published', 'is_featured', 'status']
    readonly_fields = ['thumbnail_preview', 'views_count', 'likes_count', 'shares_count', 'reading_time', 'created_at', 'updated_at']
    filter_horizontal = ['categories']
    date_hierarchy = 'published_at'
    autocomplete_fields = ['author']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'excerpt', 'content', 'featured_image', 'thumbnail_preview')
        }),
        ('Categories and Tags', {
            'fields': ('categories', 'tags')
        }),
        ('Publishing', {
            'fields': ('status', 'is_published', 'is_featured', 'published_at')
        }),
        ('Stats', {
            'fields': ('views_count', 'likes_count', 'shares_count', 'reading_time')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'canonical_url'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def thumbnail_preview(self, obj):
        if obj.featured_image:
            return format_html(
                '<img src="{}" style="width:72px;height:52px;object-fit:cover;border-radius:10px;" />',
                obj.featured_image.url,
            )
        return 'No image'

    thumbnail_preview.short_description = 'Preview'


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']
