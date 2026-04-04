"""
Blog Views for Nawab Urdu Academy
"""

from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.db.models import Q
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import BlogPost, BlogCategory
from core.models import Bookmark, Category, Comment, ContentLike
from core.services import build_seo_context, get_cross_content_suggestions, toggle_content_like, track_content_view


class BlogListView(ListView):
    """Blog list view"""
    model = BlogPost
    template_name = 'blog/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = BlogPost.objects.filter(is_published=True).select_related('author').prefetch_related('categories')
        
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
            queryset = queryset.order_by('-published_at', '-created_at')
        elif sort == 'popular':
            queryset = queryset.order_by('-views_count')
        elif sort == 'alphabetical':
            queryset = queryset.order_by('title')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(category_type='blog', is_active=True)
        context['featured_posts'] = BlogPost.objects.filter(is_featured=True, is_published=True).select_related('author')[:4]
        context['popular_posts'] = BlogPost.objects.filter(is_published=True).select_related('author').order_by('-views_count')[:6]
        context.update(
            build_seo_context(
                self.request,
                title=f"Urdu Blog | {settings.SITE_NAME}",
                description="Read trending and popular Urdu blog posts.",
                keywords=settings.SITE_KEYWORDS,
                og_type='website',
            )
        )
        return context


class BlogDetailView(DetailView):
    """Blog detail view"""
    model = BlogPost
    template_name = 'blog/blog_detail.html'
    context_object_name = 'post'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True).select_related('author').prefetch_related('categories')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        
        track_content_view(self.request, post, 'blog', post.title)
        
        # Check if bookmarked
        if self.request.user.is_authenticated:
            context['is_bookmarked'] = Bookmark.objects.filter(
                user=self.request.user,
                content_type='blog',
                object_id=post.id
            ).exists()
            context['is_liked'] = ContentLike.objects.filter(
                user=self.request.user,
                content_type='blog',
                object_id=post.id
            ).exists()
        else:
            context['is_bookmarked'] = False
            context['is_liked'] = False
        
        # Get comments
        context['comments'] = Comment.objects.filter(
            content_type='blog',
            object_id=post.id,
            is_approved=True,
            parent=None
        )
        
        # Related posts - same categories, exclude current, limit 4
        context['related_posts'] = BlogPost.objects.filter(
            categories__in=post.categories.all(),
            is_published=True
        ).exclude(id=post.id).distinct()[:4]
        context['suggested_content'] = get_cross_content_suggestions(
            author=post.author,
            categories=post.categories.all(),
            exclude_type='blog',
            exclude_id=post.id,
            limit=4,
            seed_text=f"{post.title} {post.excerpt or post.content}",
        )

        context.update(
            build_seo_context(
                self.request,
                title=post.meta_title or f"{post.title} | {settings.SITE_NAME}",
                description=post.meta_description or (post.excerpt[:160] if post.excerpt else settings.SITE_DESCRIPTION),
                keywords=post.meta_keywords or settings.SITE_KEYWORDS,
                og_type='article',
                og_image=post.featured_image.url if post.featured_image else None,
                canonical_url=post.canonical_url or None,
            )
        )
        
        return context


@login_required
def like_post(request, slug):
    """Like blog post"""
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    
    if request.method in {'POST', 'GET'}:
        return JsonResponse(toggle_content_like(request.user, 'blog', post.id))
    
    return JsonResponse({'success': False, 'message': 'غلط درخواست'})
