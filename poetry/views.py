"""
Poetry Views for Nawab Urdu Academy
"""

from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, ListView

from .models import Poetry


class PoetryListView(ListView):
    """Poetry list view"""

    model = Poetry
    template_name = "poetry/poetry_list.html"
    context_object_name = "poems"
    paginate_by = 10

    def get_queryset(self):
        return Poetry.objects.filter(is_published=True).select_related('author', 'category')


class PoetryDetailView(DetailView):
    """Poetry detail view"""

    model = Poetry
    template_name = "poetry/poetry_detail.html"
    context_object_name = "poem"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Poetry.objects.filter(is_published=True).select_related('author', 'category')
