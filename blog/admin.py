"""
Blog Admin Configuration for Nawab Urdu Academy
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import BlogCategory, BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'is_published', 'created_at']
    list_filter = ['is_published', 'category', 'created_at']
    search_fields = ['title', 'content', 'author__name']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_published']
    ordering = ['-created_at']
    autocomplete_fields = ['author']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'category', 'featured_image', 'content')
        }),
        ('Publishing', {
            'fields': ('is_published', 'published_at')
        }),
    )


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']
