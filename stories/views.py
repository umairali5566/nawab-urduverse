"""
Stories Views for Nawab Urdu Academy
"""

from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.db.models import Q
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import Story
from core.models import Bookmark, Category, Comment, ContentLike
from core.services import build_seo_context, get_cross_content_suggestions, toggle_content_like, track_content_view


class StoryListView(ListView):
    """Story list view"""
    model = Story
    template_name = 'stories/story_list.html'
    context_object_name = 'stories'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Story.objects.filter(is_published=True)
        
        # Filter by category
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(categories__slug=category)
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search) |
                Q(author__name__icontains=search)
            )
        
        # Sorting
        sort = self.request.GET.get('sort', 'latest')
        if sort == 'latest':
            queryset = queryset.order_by('-created_at')
        elif sort == 'popular':
            queryset = queryset.order_by('-views_count')
        elif sort == 'alphabetical':
            queryset = queryset.order_by('title')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(category_type='story', is_active=True)
        context['featured_stories'] = Story.objects.filter(is_featured=True, is_published=True)[:4]
        context['trending_stories'] = Story.objects.filter(is_published=True).order_by('-views_count')[:6]
        context.update(
            build_seo_context(
                self.request,
                title=f"Urdu Stories | {settings.SITE_NAME}",
                description="Discover popular and trending Urdu stories.",
                keywords=settings.SITE_KEYWORDS,
                og_type='website',
            )
        )
        return context


class StoryDetailView(DetailView):
    """Story detail view"""
    model = Story
    template_name = 'stories/story_detail.html'
    context_object_name = 'story'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        story = self.get_object()
        
        track_content_view(self.request, story, 'story', story.title)
        
        # Check if bookmarked
        if self.request.user.is_authenticated:
            context['is_bookmarked'] = Bookmark.objects.filter(
                user=self.request.user,
                content_type='story',
                object_id=story.id
            ).exists()
            context['is_liked'] = ContentLike.objects.filter(
                user=self.request.user,
                content_type='story',
                object_id=story.id
            ).exists()
        else:
            context['is_bookmarked'] = False
            context['is_liked'] = False
        
        # Get comments
        context['comments'] = Comment.objects.filter(
            content_type='story',
            object_id=story.id,
            is_approved=True,
            parent=None
        )
        
        # Related stories - same categories, exclude current, limit 4
        context['related_stories'] = Story.objects.filter(
            categories__in=story.categories.all(),
            is_published=True
        ).exclude(id=story.id).distinct()[:4]
        context['suggested_content'] = get_cross_content_suggestions(
            author=story.author,
            categories=story.categories.all(),
            exclude_type='story',
            exclude_id=story.id,
            limit=4,
            seed_text=f"{story.title} {story.excerpt or story.content}",
        )

        context.update(
            build_seo_context(
                self.request,
                title=story.meta_title or f"{story.title} | {settings.SITE_NAME}",
                description=story.meta_description or (story.excerpt[:160] if story.excerpt else settings.SITE_DESCRIPTION),
                keywords=story.meta_keywords or settings.SITE_KEYWORDS,
                og_type='article',
                og_image=story.featured_image.url if story.featured_image else None,
            )
        )
        
        return context


def story_categories(request):
    """Story categories view"""
    categories = Category.objects.filter(category_type='story', is_active=True)
    
    context = {
        'categories': categories,
        **build_seo_context(
            request,
            title=f"Story Categories | {settings.SITE_NAME}",
            description="Browse Urdu story categories.",
            keywords=settings.SITE_KEYWORDS,
            og_type='website',
        ),
    }
    
    return render(request, 'stories/categories.html', context)


@login_required
def like_story(request, slug):
    """Like story"""
    story = get_object_or_404(Story, slug=slug, is_published=True)
    
    if request.method in {'POST', 'GET'}:
        return JsonResponse(toggle_content_like(request.user, 'story', story.id))
    
    return JsonResponse({'success': False, 'message': 'غلط درخواست'})
