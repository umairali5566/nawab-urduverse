"""
Novels Admin Configuration for Nawab Urdu Academy
"""

from django.contrib import admin

from .models import Chapter, Novel, NovelReview


@admin.register(Novel)
class NovelAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'total_chapters', 'is_published', 'created_at']
    list_filter = ['category', 'is_published', 'created_at']
    search_fields = ['title', 'author__name', 'content']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_published']
    ordering = ['-created_at']
    autocomplete_fields = ['author']
    readonly_fields = ['total_chapters', 'created_at']

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
            'fields': ('total_chapters', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'category')


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ['title', 'novel', 'chapter_number', 'author', 'is_published', 'is_premium', 'views_count', 'created_at']
    list_filter = ['is_published', 'is_premium', 'created_at']
    search_fields = ['title', 'novel__title', 'content']
    list_editable = ['is_published', 'is_premium']
    ordering = ['novel', 'chapter_number']
    autocomplete_fields = ['novel']
    readonly_fields = ['views_count', 'word_count', 'reading_time', 'created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('novel', 'chapter_number', 'title', 'slug')
        }),
        ('Content', {
            'fields': ('content',),
            'classes': ('wide',)
        }),
        ('Publishing', {
            'fields': ('is_published', 'is_premium', 'published_at')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('views_count', 'word_count', 'reading_time', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('novel__author')

    def author(self, obj):
        return obj.novel.author.name
    author.short_description = 'Author'


@admin.register(NovelReview)
class NovelReviewAdmin(admin.ModelAdmin):
    list_display = ['novel', 'user', 'rating', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['novel__title', 'user__username', 'review_text']
    list_editable = ['is_approved']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('novel', 'user', 'rating')
        }),
        ('Review', {
            'fields': ('review_text',),
            'classes': ('wide',)
        }),
        ('Moderation', {
            'fields': ('is_approved', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('novel', 'user')
