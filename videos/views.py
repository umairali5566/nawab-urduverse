"""
Videos Views for Nawab Urdu Academy
"""

from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.db.models import Q
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import Video, VideoPlaylist
from core.models import Bookmark, Category, ContentLike
from core.services import build_seo_context, get_cross_content_suggestions, toggle_content_like, track_content_view


class VideoListView(ListView):
    """Video list view"""
    model = Video
    template_name = 'videos/video_list.html'
    context_object_name = 'videos'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Video.objects.filter(is_published=True).select_related('author')
        
        # Filter by type
        video_type = self.request.GET.get('type')
        if video_type:
            queryset = queryset.filter(video_type=video_type)
        
        # Filter by category
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(content__icontains=search) |
                Q(author__name__icontains=search)
            )
        
        # Sorting
        sort = self.request.GET.get('sort', 'latest')
        if sort == 'latest':
            queryset = queryset.order_by('-created_at')
        elif sort == 'popular':
            queryset = queryset.order_by('-views_count')
        
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['video_types'] = Video.VIDEO_TYPES
            context['categories'] = Category.objects.filter(category_type='video', is_active=True)
            context['featured_videos'] = Video.objects.filter(is_featured=True, is_published=True).select_related('author')[:4]
            context['poetry_videos'] = Video.objects.filter(video_type='poetry', is_published=True).select_related('author')[:6]
            context['story_videos'] = Video.objects.filter(video_type='story', is_published=True).select_related('author')[:6]
        except Exception as e:
            # Log error in production but don't crash
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error loading video context data: {e}")
            context['video_types'] = Video.VIDEO_TYPES
            context['categories'] = Category.objects.none()
            context['featured_videos'] = []
            context['poetry_videos'] = []
            context['story_videos'] = []
        
        context.update(
            build_seo_context(
                self.request,
                title=f"Urdu Videos | {settings.SITE_NAME}",
                description="Watch Urdu literature and poetry videos.",
                keywords=settings.SITE_KEYWORDS,
                og_type='website',
            )
        )
        return context


class VideoDetailView(DetailView):
    """Video detail view"""
    model = Video
    template_name = 'videos/video_detail.html'
    context_object_name = 'video'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Video.objects.filter(is_published=True).select_related('author')
    
    def get_context_data(self, **kwargs):
        import logging
        context = super().get_context_data(**kwargs)
        logger = logging.getLogger(__name__)
        
        try:
            video = self.get_object()
            track_content_view(self.request, video, 'video', video.title)

            if self.request.user.is_authenticated:
                context['is_bookmarked'] = Bookmark.objects.filter(
                    user=self.request.user,
                    content_type='video',
                    object_id=video.id
                ).exists()
                context['is_liked'] = ContentLike.objects.filter(
                    user=self.request.user,
                    content_type='video',
                    object_id=video.id
                ).exists()
            else:
                context['is_bookmarked'] = False
                context['is_liked'] = False

            # Related videos
            context['related_videos'] = Video.objects.filter(
                video_type=video.video_type,
                is_published=True
            ).select_related('author').exclude(id=video.id)[:4]
            
            context['suggested_content'] = get_cross_content_suggestions(
                author=video.author,
                categories=video.categories,
                exclude_type='video',
                exclude_id=video.id,
                limit=4,
                seed_text=f"{video.title} {video.description}",
            ) or []

            context.update(
                build_seo_context(
                    self.request,
                    title=video.meta_title or f"{video.title} | {settings.SITE_NAME}",
                    description=video.meta_description or (video.description[:160] if video.description else settings.SITE_DESCRIPTION),
                    keywords=settings.SITE_KEYWORDS,
                    og_type='video.other',
                    og_image=video.get_thumbnail_url(),
                )
            )
        except Exception as e:
            logger.error(f"Error loading video detail context: {e}", exc_info=True)
            context['related_videos'] = []
            context['suggested_content'] = []
            context['is_bookmarked'] = False
            context['is_liked'] = False
        
        return context


class PlaylistListView(ListView):
    """Playlist list view"""
    model = VideoPlaylist
    template_name = 'videos/playlist_list.html'
    context_object_name = 'playlists'
    paginate_by = 12
    
    def get_queryset(self):
        return VideoPlaylist.objects.filter(is_published=True)


class PlaylistDetailView(DetailView):
    """Playlist detail view"""
    model = VideoPlaylist
    template_name = 'videos/playlist_detail.html'
    context_object_name = 'playlist'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        playlist = self.get_object()
        context['videos'] = playlist.videos.filter(is_published=True)
        return context


def videos_by_type(request, video_type):
    """Videos by type view"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        videos = Video.objects.filter(video_type=video_type, is_published=True)
        video_type_display = dict(Video.VIDEO_TYPES).get(video_type, video_type)
    except Exception as e:
        logger.error(f"Error loading videos by type: {e}")
        videos = Video.objects.none()
        video_type_display = video_type
    
    context = {
        'videos': videos,
        'video_type': video_type,
        'video_type_display': video_type_display,
        **build_seo_context(
            request,
            title=f"{video_type_display} Videos | {settings.SITE_NAME}",
            description="Browse Urdu videos by type.",
            keywords=settings.SITE_KEYWORDS,
            og_type='website',
        ),
    }
    
    return render(request, 'videos/videos_by_type.html', context)


@login_required
def like_video(request, slug):
    """Like video"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        video = get_object_or_404(Video, slug=slug, is_published=True)
        
        if request.method in {'POST', 'GET'}:
            return JsonResponse(toggle_content_like(request.user, 'video', video.id))
    except Exception as e:
        logger.error(f"Error liking video: {e}")
        return JsonResponse({'success': False, 'message': 'خرابی واقع ہوئی'})
    
    return JsonResponse({'success': False, 'message': 'غلط درخواست'})
