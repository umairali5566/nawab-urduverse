"""
Core Admin Configuration for Nawab Urdu Academy
"""

from django.contrib import admin

from .models import Category, Author, Story, Content


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'is_active']
    list_filter = ['category_type', 'is_active']
    search_fields = ['name', 'name_english']
    prepopulated_fields = {'slug': ('name_english',)}


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug')
        }),
        ('Settings', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'content_type', 'author', 'category', 'is_published', 'created_at']
    list_filter = ['content_type', 'is_published', 'category']
    search_fields = ['title', 'text', 'author__name']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['-created_at']


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'is_published', 'views_count', 'created_at']
    list_filter = ['is_published', 'category', 'created_at']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_published']
    ordering = ['-created_at']
