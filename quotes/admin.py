"""
Quotes Admin Configuration for Nawab Urdu Academy
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import Quote, QuoteCollection


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'quote_type', 'is_featured', 'is_published', 'created_at']
    list_filter = ['is_published', 'category', 'quote_type', 'is_featured', 'created_at']
    search_fields = ['title', 'text', 'author__name']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_published']
    ordering = ['-created_at']
    autocomplete_fields = ['author']
    filter_horizontal = ['categories']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'category', 'text')
        }),
        ('Classification', {
            'fields': ('quote_type', 'categories', 'is_featured')
        }),
        ('Design & SEO', {
            'fields': ('background_image', 'text_color', 'background_color', 'font_size', 'meta_title', 'meta_description')
        }),
        ('Publishing', {
            'fields': ('is_published', 'published_at')
        }),
        ('Engagement', {
            'fields': ('views_count', 'likes_count', 'shares_count')
        }),
    )
    readonly_fields = ('views_count', 'likes_count', 'shares_count')


@admin.register(QuoteCollection)
class QuoteCollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_published', 'created_at']
    list_filter = ['is_published', 'created_at']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['quotes']
    readonly_fields = ['created_at', 'updated_at']
