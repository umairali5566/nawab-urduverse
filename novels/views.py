"""
Novels Views for Nawab Urdu Academy
"""

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView, ListView

from core.models import ReadingProgress
from core.services import toggle_content_like
from .models import Chapter, Novel


class NovelListView(ListView):
    """Novel list view"""

    model = Novel
    template_name = "novels/novel_list.html"
    context_object_name = "novels"
    paginate_by = 10

    def get_queryset(self):
        return Novel.objects.filter(is_published=True).select_related('author', 'category')


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
        chapter_slug = self.kwargs['chapter_slug']
        novel = get_object_or_404(Novel, slug=novel_slug, is_published=True)
        return get_object_or_404(Chapter, novel=novel, slug=chapter_slug, is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chapter = self.object
        context['novel'] = chapter.novel
        context['previous_chapter'] = chapter.get_previous_chapter()
        context['next_chapter'] = chapter.get_next_chapter()
        context['chapter_count'] = chapter.novel.total_chapters
        return context


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
