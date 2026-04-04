"""
Stories Admin Configuration for Nawab Urdu Academy
"""

from django.contrib import admin
from .models import Story


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'author', 'is_published', 'is_featured',
        'views_count', 'likes_count', 'shares_count', 'reading_time', 'created_at'
    ]
    list_filter = ['is_published', 'is_featured', 'categories', 'created_at']
    search_fields = ['title', 'content', 'author__name']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_published', 'is_featured']
    readonly_fields = ['views_count', 'likes_count', 'shares_count', 'reading_time', 'created_at', 'updated_at']
    filter_horizontal = ['categories']
    
    fieldsets = (
        ('بنیادی معلومات', {
            'fields': ('title', 'slug', 'author', 'content', 'excerpt', 'featured_image')
        }),
        ('زمرہ جات اور ٹیگز', {
            'fields': ('categories', 'tags')
        }),
        ('اشاعت', {
            'fields': ('is_published', 'is_featured', 'published_at')
        }),
        ('شماریات', {
            'fields': ('views_count', 'likes_count', 'shares_count', 'reading_time')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('تاریخ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
