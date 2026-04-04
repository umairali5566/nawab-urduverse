"""
Quotes Admin Configuration for Nawab UrduVerse
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import Quote, QuoteCollection


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = [
        'background_preview', 'text_preview', 'author', 'quote_type',
        'is_published', 'is_featured', 'views_count', 'created_at'
    ]
    list_filter = ['quote_type', 'is_published', 'is_featured', 'created_at']
    search_fields = ['text', 'author__name']
    prepopulated_fields = {'slug': ('text',)}
    list_editable = ['is_published', 'is_featured']
    readonly_fields = ['background_preview', 'views_count', 'likes_count', 'shares_count', 'created_at', 'updated_at']
    filter_horizontal = ['categories']
    autocomplete_fields = ['author']

    fieldsets = (
        ('Basic Information', {
            'fields': ('text', 'slug', 'author', 'quote_type')
        }),
        ('Visual Style', {
            'fields': ('background_image', 'background_preview', 'text_color', 'background_color', 'font_size')
        }),
        ('Categories and Tags', {
            'fields': ('categories', 'tags')
        }),
        ('Publishing', {
            'fields': ('is_published', 'is_featured')
        }),
        ('Stats', {
            'fields': ('views_count', 'likes_count', 'shares_count')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def text_preview(self, obj):
        return obj.text[:80] + '...' if len(obj.text) > 80 else obj.text

    text_preview.short_description = 'Quote'

    def background_preview(self, obj):
        if obj.background_image:
            return format_html(
                '<img src="{}" style="width:72px;height:72px;object-fit:cover;border-radius:14px;" />',
                obj.background_image.url,
            )
        return 'No image'

    background_preview.short_description = 'Preview'


@admin.register(QuoteCollection)
class QuoteCollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_published', 'created_at']
    list_filter = ['is_published', 'created_at']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['quotes']
    readonly_fields = ['created_at', 'updated_at']
