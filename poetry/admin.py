"""
Poetry Admin Configuration for Nawab Urdu Academy
"""

from django.contrib import admin
from django.forms import Textarea

from .models import Poetry


@admin.register(Poetry)
class PoetryAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'is_published', 'created_at']
    list_filter = ['category', 'is_published', 'created_at']
    search_fields = ['title', 'author__name', 'content']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_published']
    ordering = ['-created_at']
    autocomplete_fields = ['author']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'category')
        }),
        ('Content', {
            'fields': ('content',),
            'classes': ('wide',)
        }),
        ('Publishing', {
            'fields': ('is_published', 'published_at')
        }),
        ('Statistics', {
            'fields': ('views_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    formfield_overrides = {
        Poetry._meta.get_field('content').__class__: {
            'widget': Textarea(attrs={'rows': 20, 'cols': 80}),
        },
    }

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'category')
