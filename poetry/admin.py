"""
Poetry Admin Configuration for Nawab UrduVerse
"""

from django.contrib import admin
from django.forms import Textarea

from .models import Poetry


@admin.register(Poetry)
class PoetryAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'poetry_type', 'is_featured', 'is_published', 'views_count', 'likes_count']
    list_filter = ['category', 'poetry_type', 'mood', 'is_featured', 'is_published']
    search_fields = ['title', 'author__name']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_published', 'is_featured']
    ordering = ['-created_at']
    autocomplete_fields = ['author']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'poetry_type', 'mood', 'category', 'content')
        }),
        ('Media', {
            'fields': ('background_image',)
        }),
        ('Publishing', {
            'fields': ('is_published', 'is_featured', 'published_at')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
    )

    formfield_overrides = {
        Poetry._meta.get_field('content').__class__: {
            'widget': Textarea(attrs={'rows': 20, 'cols': 80}),
        },
    }
