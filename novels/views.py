"""
Novels Views for Nawab Urdu Academy
"""

from django.contrib.auth.decorators import login_required
from django.http import HttpResponsePermanentRedirect, JsonResponse
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView, ListView

from core.models import ContentLike, ReadingProgress
from core.services import toggle_content_like
from .models import Chapter, Novel


class NovelListView(ListView):
    """Novel list view"""

    model = Novel
    template_name = "novels/novel_list.html"
    context_object_name = "novels"
    paginate_by = 10

    def get_queryset(self):
        queryset = Novel.objects.filter(is_published=True).select_related('author', 'category').annotate(
            published_chapters=Count('chapters', filter=Q(chapters__is_published=True))
        )

        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search) |
                Q(author__name__icontains=search)
            )

        sort = self.request.GET.get('sort', 'latest').strip().lower()
        if sort == 'title':
            queryset = queryset.order_by('title')
        elif sort == 'chapters':
            queryset = queryset.order_by('-published_chapters', '-created_at')
        else:
            queryset = queryset.order_by('-published_at', '-created_at')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '').strip()
        context['sort_value'] = self.request.GET.get('sort', 'latest').strip().lower() or 'latest'
        context['featured_novels'] = Novel.objects.filter(
            is_published=True
        ).select_related('author', 'category').order_by('-created_at')[:3]
        return context


class NovelDetailView(DetailView):
    """Novel detail view"""

    model = Novel
    template_name = "novels/novel_detail.html"
    context_object_name = "novel"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Novel.objects.filter(is_published=True).select_related('author', 'category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chapters'] = self.object.chapters.filter(is_published=True).order_by('chapter_number')
        context['chapter_count'] = self.object.total_chapters

        if self.request.user.is_authenticated:
            context['is_liked'] = ContentLike.objects.filter(
                user=self.request.user,
                content_type='novel',
                object_id=self.object.id,
            ).exists()
        else:
            context['is_liked'] = False

        return context


class ChapterDetailView(DetailView):
    """Chapter detail view"""

    model = Chapter
    template_name = "novels/chapter_detail.html"
    context_object_name = "chapter"

    def get_queryset(self):
        return Chapter.objects.filter(is_published=True).select_related('novel__author', 'novel__category')

    def get_object(self):
        novel_slug = self.kwargs['novel_slug']
        chapter_number = self.kwargs['chapter_number']
        novel = get_object_or_404(Novel, slug=novel_slug, is_published=True)
        return get_object_or_404(
            Chapter,
            novel=novel,
            chapter_number=chapter_number,
            is_published=True,
        )

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if kwargs.get('chapter_slug') != self.object.slug:
            return HttpResponsePermanentRedirect(self.object.get_absolute_url())
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chapter = self.object
        context['novel'] = chapter.novel
        context['previous_chapter'] = chapter.get_previous_chapter()
        context['next_chapter'] = chapter.get_next_chapter()
        context['chapter_count'] = chapter.novel.total_chapters
        return context


def legacy_chapter_redirect(request, novel_slug, chapter_slug):
    """Redirect legacy chapter URLs to the canonical chapter route."""
    novel = get_object_or_404(Novel, slug=novel_slug, is_published=True)
    chapter = get_object_or_404(
        Chapter,
        novel=novel,
        slug=chapter_slug,
        is_published=True,
    )
    return redirect(chapter.get_absolute_url(), permanent=True)


def continue_reading(request, slug):
    """Continue reading from where user left off"""
    novel = get_object_or_404(Novel, slug=slug, is_published=True)

    if request.user.is_authenticated:
        progress = ReadingProgress.objects.filter(user=request.user, novel=novel).first()
        if progress and progress.chapter:
            return redirect(progress.chapter.get_absolute_url())

    # No progress, start from first chapter
    first_chapter = novel.chapters.filter(is_published=True).order_by('chapter_number').first()
    if first_chapter:
        return redirect(first_chapter.get_absolute_url())

    # No chapters, redirect to novel detail
    return redirect(novel.get_absolute_url())


@login_required
def like_novel(request, slug):
    """Like novel"""
    novel = get_object_or_404(Novel, slug=slug, is_published=True)

    if request.method in {'POST', 'GET'}:
        return JsonResponse(toggle_content_like(request.user, 'novel', novel.id))

    return JsonResponse({'success': False, 'message': 'غلط درخواست'})
