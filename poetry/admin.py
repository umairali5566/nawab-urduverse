"""
Poetry Admin Configuration for Nawab Urdu Academy
"""

from django.contrib import admin
from django.forms import Textarea

from .models import Poetry


@admin.register(Poetry)
class PoetryAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'is_published', 'created_at']
    list_filter = ['category', 'is_published']
    search_fields = ['title', 'author__name']
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

    formfield_overrides = {
        Poetry._meta.get_field('content').__class__: {
            'widget': Textarea(attrs={'rows': 20, 'cols': 80}),
        },
    }
