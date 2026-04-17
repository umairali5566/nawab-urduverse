"""
Novels Views for Nawab Urdu Academy
"""

from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from .models import Novel


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
