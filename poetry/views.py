"""
Poetry Views for Nawab Urdu Academy
"""

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, ListView

from core.services import toggle_content_like

from .models import Poetry


class PoetryListView(ListView):
    """Poetry list view"""

    model = Poetry
    template_name = "poetry/poetry_list.html"
    context_object_name = "poems"
    paginate_by = 12

    def get_queryset(self):
        return Poetry.objects.filter(
            is_published=True
        ).select_related('author', 'category').only(
            'title', 'slug', 'author__name', 'author__slug',
            'category__name', 'category__slug', 'created_at',
            'views_count', 'likes_count'
        ).order_by('-created_at')


class PoetryDetailView(DetailView):
    """Poetry detail view"""

    model = Poetry
    template_name = "poetry/poetry_detail.html"
    context_object_name = "poem"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Poetry.objects.filter(is_published=True).select_related('author', 'category')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Increment view count (could be moved to middleware for better performance)
        Poetry.objects.filter(pk=obj.pk).update(views_count=obj.views_count + 1)
        obj.views_count += 1
        return obj


@login_required
def like_poetry(request, slug):
    """Like poetry"""
    poetry = get_object_or_404(Poetry, slug=slug, is_published=True)

    if request.method in {'POST', 'GET'}:
        return JsonResponse(toggle_content_like(request.user, 'poetry', poetry.id))

    return JsonResponse({'success': False, 'message': 'غلط درخواست'})
