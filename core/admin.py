"""
Core Admin Configuration for Nawab Urdu Academy
"""

from django.contrib import admin

from .models import Category, Author


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_published', 'created_at']
    list_filter = ['is_published']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_published']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug')
        }),
        ('Settings', {
            'fields': ('is_published',)
        }),
    )



