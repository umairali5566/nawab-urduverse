"""
Videos Admin Configuration for Nawab Urdu Academy
"""

from django import forms
from django.contrib import admin

from .models import Video, VideoPlaylist


class VideoAdminForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['author'].required = False
        self.fields['category'].required = False


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    form = VideoAdminForm
    list_display = ['title', 'author', 'category', 'video_type', 'is_published', 'is_featured', 'views_count', 'created_at']
    list_filter = ['is_published', 'is_featured', 'category', 'video_type', 'created_at']
    search_fields = ['title', 'content', 'author__name', 'description']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_published', 'is_featured']
    ordering = ['-created_at']
    autocomplete_fields = ['author']
    readonly_fields = ['views_count', 'likes_count', 'created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'category', 'video_type')
        }),
        ('Content', {
            'fields': ('content', 'description', 'thumbnail_url'),
            'classes': ('wide',)
        }),
        ('Publishing', {
            'fields': ('is_published', 'is_featured', 'published_at')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('views_count', 'likes_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'category')


@admin.register(VideoPlaylist)
class VideoPlaylistAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_published', 'created_at']
    list_filter = ['is_published', 'created_at']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['videos']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'cover_image')
        }),
        ('Content', {
            'fields': ('videos',)
        }),
        ('Publishing', {
            'fields': ('is_published', 'created_at', 'updated_at')
        }),
    )
