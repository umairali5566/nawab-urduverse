"""
Novels Admin Configuration for Nawab Urdu Academy
"""

from django.contrib import admin

from .models import Novel


@admin.register(Novel)
class NovelAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'created_at', 'is_published']
    list_filter = ['category', 'is_published']
    search_fields = ['title']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_published']
    ordering = ['-created_at']
    autocomplete_fields = ['author']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'category', 'content')
        }),
        ('Publishing', {
            'fields': ('is_published',)
        }),
    )
