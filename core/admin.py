"""
Core Admin Configuration for Nawab Urdu Academy
"""

from django.contrib import admin

from .models import Category, Author, SiteTheme, Logo


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', 'author_type', 'is_featured', 'is_published', 'created_at']
    list_filter = ['author_type', 'is_featured', 'is_published']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_published', 'is_featured']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'author_type', 'bio')
        }),
        ('Content Counts', {
            'fields': (
                ('ghazal_count', 'nazm_count', 'sher_count'),
                ('ebook_count', 'top20_poetry_count', 'pictorial_poetry_count'),
                ('quotes_count', 'videos_count', 'qita_count'),
                ('rubai_count', 'qissa_count', 'gallery_count', 'blog_count'),
            ),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('is_published', 'is_featured')
        }),
    )


@admin.register(SiteTheme)
class SiteThemeAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'primary_color', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']
    list_editable = ['is_active']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'is_active')
        }),
        ('Colors', {
            'fields': ('primary_color', 'background_color', 'text_color')
        }),
        ('Typography', {
            'fields': ('font_family',)
        }),
    )


@admin.register(Logo)
class LogoAdmin(admin.ModelAdmin):
    list_display = ['alt_text', 'is_active', 'updated_at']
    list_filter = ['is_active']
    search_fields = ['alt_text']
    list_editable = ['is_active']

    fieldsets = (
        ('Logo Details', {
            'fields': ('image', 'alt_text', 'is_active')
        }),
    )
