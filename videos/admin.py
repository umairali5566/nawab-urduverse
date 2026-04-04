"""
Videos Admin Configuration for Nawab Urdu Academy
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import Video, VideoPlaylist


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = [
        'thumbnail_preview', 'title', 'video_type', 'platform', 'is_published',
        'is_featured', 'views_count', 'likes_count', 'shares_count', 'created_at'
    ]
    list_filter = ['video_type', 'platform', 'is_published', 'is_featured', 'created_at']
    search_fields = ['title', 'description', 'author__name', 'youtube_link', 'video_url']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_published', 'is_featured']
    readonly_fields = ['thumbnail_preview', 'video_source_preview', 'views_count', 'likes_count', 'shares_count', 'created_at', 'updated_at']
    filter_horizontal = ['categories']
    autocomplete_fields = ['author']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'video_type', 'author')
        }),
        ('Video Source', {
            'fields': ('platform', 'video_id', 'video_url', 'youtube_link', 'video_file', 'video_source_preview')
        }),
        ('Media', {
            'fields': ('thumbnail', 'thumbnail_preview', 'duration')
        }),
        ('Categories and Tags', {
            'fields': ('categories', 'tags')
        }),
        ('Publishing', {
            'fields': ('is_published', 'is_featured', 'published_at')
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

    def thumbnail_preview(self, obj):
        thumb_url = obj.get_thumbnail_url() if obj.pk else ''
        if thumb_url:
            return format_html(
                '<img src="{}" style="width:72px;height:52px;object-fit:cover;border-radius:10px;" />',
                thumb_url,
            )
        return 'No image'

    thumbnail_preview.short_description = 'Thumbnail'

    def video_source_preview(self, obj):
        if obj.video_file:
            return format_html(
                '<video src="{}" controls style="width:220px;border-radius:12px;"></video>',
                obj.video_file.url,
            )
        if obj.get_embed_url() and obj.platform != 'local':
            return format_html('<a href="{}" target="_blank">Open video source</a>', obj.video_url or obj.youtube_link)
        return 'No video preview'

    video_source_preview.short_description = 'Source preview'


@admin.register(VideoPlaylist)
class VideoPlaylistAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_published', 'created_at']
    list_filter = ['is_published', 'created_at']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['videos']
    readonly_fields = ['created_at', 'updated_at']
