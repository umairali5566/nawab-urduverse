"""
Novels Views for Nawab Urdu Academy
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.db.models import Q, Count, Avg
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator

from .models import Novel, Chapter, NovelReview
from core.models import Bookmark, Category, Comment, ContentLike, ReadingProgress
from core.services import build_seo_context, get_cross_content_suggestions, toggle_content_like, track_content_view, user_can_access_content, user_has_premium_access


class NovelListView(ListView):
    """Novel list view"""
    model = Novel
    template_name = 'novels/novel_list.html'
    context_object_name = 'novels'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Novel.objects.filter(is_published=True).select_related('author', 'category')
        
        # Filter by category
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(author__name__icontains=search)
            )
        
        # Sorting
        sort = self.request.GET.get('sort', 'latest')
        if sort == 'latest':
            queryset = queryset.order_by('-published_at', '-created_at')
        elif sort == 'popular':
            queryset = queryset.order_by('-views_count')
        elif sort == 'rating':
            queryset = queryset.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
        elif sort == 'alphabetical':
            queryset = queryset.order_by('title')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(category_type='novel', is_active=True)
        context['featured_novels'] = Novel.objects.filter(is_featured=True, is_published=True).select_related('author')[:4]
        context['latest_novels'] = Novel.objects.filter(is_published=True).select_related('author').order_by('-published_at', '-created_at')[:6]
        context['completed_novels'] = Novel.objects.filter(status='completed', is_published=True).select_related('author')[:6]
        context.update(
            build_seo_context(
                self.request,
                title=f"Urdu Novels | {settings.SITE_NAME}",
                description="Read popular and trending Urdu novels with complete chapter lists.",
                keywords=settings.SITE_KEYWORDS,
                og_type='website',
            )
        )
        return context


class NovelDetailView(DetailView):
    """Novel detail view"""
    model = Novel
    template_name = 'novels/novel_detail.html'
    context_object_name = 'novel'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Novel.objects.filter(is_published=True).select_related('author', 'category')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        novel = self.get_object()
        
        track_content_view(self.request, novel, 'novel', novel.title)
        
        # Get chapters
        context['chapters'] = Chapter.objects.filter(novel=novel, is_published=True).order_by('chapter_number')
        
        # Get reviews
        context['reviews'] = NovelReview.objects.filter(novel=novel, is_approved=True)[:10]
        context['average_rating'] = novel.reviews.filter(is_approved=True).aggregate(Avg('rating'))['rating__avg']
        
        # Check if bookmarked
        if self.request.user.is_authenticated:
            context['is_bookmarked'] = Bookmark.objects.filter(
                user=self.request.user,
                content_type='novel',
                object_id=novel.id
            ).exists()
            context['is_liked'] = ContentLike.objects.filter(
                user=self.request.user,
                content_type='novel',
                object_id=novel.id
            ).exists()
        else:
            context['is_bookmarked'] = False
            context['is_liked'] = False
        
        # Related novels - prefer same category, otherwise fallback to same author.
        related_novels = Novel.objects.filter(is_published=True).select_related('author').exclude(id=novel.id)
        if novel.category_id:
            related_novels = related_novels.filter(category=novel.category)
        elif novel.author_id:
            related_novels = related_novels.filter(author=novel.author)
        context['related_novels'] = related_novels[:4]
        context['has_premium_access'] = user_has_premium_access(self.request.user)
        context['suggested_content'] = get_cross_content_suggestions(
            author=novel.author,
            categories=[novel.category] if novel.category else [],
            exclude_type='novel',
            exclude_id=novel.id,
            limit=4,
            seed_text=f"{novel.title} {novel.description_text}",
        )

        context.update(
            build_seo_context(
                self.request,
                title=novel.meta_title or f"{novel.title} | {settings.SITE_NAME}",
                description=novel.meta_description or (novel.description_text[:160] if novel.description else settings.SITE_DESCRIPTION),
                keywords=novel.meta_keywords or settings.SITE_KEYWORDS,
                og_type='article',
                og_image=novel.cover_image.url if novel.cover_image else None,
            )
        )
        
        return context


class ChapterDetailView(DetailView):
    """Chapter detail view"""
    model = Chapter
    template_name = 'novels/chapter_detail.html'
    context_object_name = 'chapter'
    slug_url_kwarg = 'chapter_slug'
    
    def get_object(self, queryset=None):
        novel_slug = self.kwargs.get('novel_slug')
        chapter_slug = self.kwargs.get('chapter_slug')
        return get_object_or_404(Chapter, novel__slug=novel_slug, slug=chapter_slug, is_published=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chapter = self.object
        
        track_content_view(
            self.request,
            chapter,
            'chapter',
            f"{chapter.novel.title} - Chapter {chapter.chapter_number}: {chapter.title}",
        )
        
        # Get previous and next chapters
        context['previous_chapter'] = chapter.get_previous_chapter()
        context['next_chapter'] = chapter.get_next_chapter()

        # Get all chapters for navigation
        all_chapters = Chapter.objects.filter(
            novel=chapter.novel,
            is_published=True
        ).order_by('chapter_number')
        context['all_chapters'] = all_chapters
        context['chapter_count'] = all_chapters.count()
        
        # Update reading progress
        if self.request.user.is_authenticated:
            ReadingProgress.objects.update_or_create(
                user=self.request.user,
                novel=chapter.novel,
                defaults={'chapter': chapter}
            )
        
        # Get comments
        context['comments'] = Comment.objects.filter(
            content_type='novel',
            object_id=chapter.id,
            is_approved=True,
            parent=None
        )

        # Bookmark state for the parent novel
        if self.request.user.is_authenticated:
            context['is_bookmarked'] = Bookmark.objects.filter(
                user=self.request.user,
                content_type='novel',
                object_id=chapter.novel.id
            ).exists()
        else:
            context['is_bookmarked'] = False
        context['has_premium_access'] = user_can_access_content(self.request.user, chapter)
        context['requires_membership'] = not context['has_premium_access']

        context.update(
            build_seo_context(
                self.request,
                title=chapter.meta_title or f"{chapter.novel.title} Chapter {chapter.chapter_number} | {settings.SITE_NAME}",
                description=chapter.meta_description or f"Read chapter {chapter.chapter_number} of {chapter.novel.title}.",
                keywords=settings.SITE_KEYWORDS,
                og_type='article',
                og_image=chapter.novel.cover_image.url if chapter.novel.cover_image else None,
            )
        )
        
        return context


def novel_categories(request):
    """Novel categories view"""
    categories = Category.objects.filter(category_type='novel', is_active=True)
    
    context = {
        'categories': categories,
        **build_seo_context(
            request,
            title=f"Novel Categories | {settings.SITE_NAME}",
            description="Browse Urdu novel categories.",
            keywords=settings.SITE_KEYWORDS,
            og_type='website',
        ),
    }
    
    return render(request, 'novels/categories.html', context)


@login_required
def add_review(request, slug):
    """Add novel review"""
    novel = get_object_or_404(Novel, slug=slug, is_published=True)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        review_text = request.POST.get('review_text')
        
        if rating and review_text:
            review, created = NovelReview.objects.update_or_create(
                novel=novel,
                user=request.user,
                defaults={
                    'rating': rating,
                    'review_text': review_text
                }
            )
            
            return JsonResponse({
                'success': True,
                'message': 'آپ کا جائزہ شامل کر دیا گیا',
                'created': created
            })
        
        return JsonResponse({
            'success': False,
            'message': 'براہ کرم ریٹنگ اور جائزہ درج کریں'
        })
    
    return JsonResponse({'success': False, 'message': 'غلط درخواست'})


@login_required
def like_novel(request, slug):
    """Like novel"""
    novel = get_object_or_404(Novel, slug=slug, is_published=True)
    
    if request.method in {'POST', 'GET'}:
        return JsonResponse(toggle_content_like(request.user, 'novel', novel.id))
    
    return JsonResponse({'success': False, 'message': 'غلط درخواست'})


def continue_reading(request, slug):
    """Continue reading from last chapter"""
    novel = get_object_or_404(Novel, slug=slug, is_published=True)
    
    if request.user.is_authenticated:
        # Get last read chapter
        progress = ReadingProgress.objects.filter(
            user=request.user,
            novel=novel
        ).first()
        
        if progress:
            return redirect(progress.chapter.get_absolute_url())
    
    # If no progress, go to first chapter
    first_chapter = novel.get_first_chapter()
    if first_chapter:
        return redirect(first_chapter.get_absolute_url())
    
    return redirect(novel.get_absolute_url())


def legacy_chapter_redirect(request, novel_slug, chapter_slug):
    """Redirect old chapter URLs to canonical chapter route."""
    return redirect(
        'chapter_detail',
        novel_slug=novel_slug,
        chapter_slug=chapter_slug,
        permanent=True,
    )
