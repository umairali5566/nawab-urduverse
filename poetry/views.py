"""
Poetry Views for Nawab Urdu Academy
"""

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from core.models import ContentLike
from core.services import toggle_content_like

from .models import Poetry


class PoetryListView(ListView):
    """Poetry list view"""

    model = Poetry
    template_name = "poetry/poetry_list.html"
    context_object_name = "poems"
    paginate_by = 12

    def get_queryset(self):
        queryset = Poetry.objects.filter(
            is_published=True
        ).select_related('author', 'category').only(
            'title', 'slug', 'content', 'author__name', 'author__slug',
            'category__name', 'category__slug', 'created_at',
            'views_count', 'likes_count'
        )

        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search) |
                Q(author__name__icontains=search)
            )

        genre = self.request.GET.get('genre', '').strip().lower()
        if genre:
            keyword_map = {
                'ghazal': ['ghazal', 'غزل'],
                'nazm': ['nazm', 'نظم'],
                'love': ['love', 'mohabbat', 'ishq', 'محبت', 'عشق'],
                'sad': ['sad', 'gham', 'udaas', 'udasi', 'غم', 'اداس', 'اداسی'],
            }
            genre_query = Q(category__slug__icontains=genre) | Q(category__name__icontains=genre)
            for keyword in keyword_map.get(genre, [genre]):
                genre_query |= Q(title__icontains=keyword) | Q(content__icontains=keyword)
            queryset = queryset.filter(genre_query)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_genre'] = self.request.GET.get('genre', '').strip().lower()
        context['search_query'] = self.request.GET.get('search', '').strip()
        context['genre_tabs'] = [
            {'label': 'All', 'value': ''},
            {'label': 'Ghazal', 'value': 'ghazal'},
            {'label': 'Nazm', 'value': 'nazm'},
            {'label': 'Love', 'value': 'love'},
            {'label': 'Sad', 'value': 'sad'},
        ]
        context['featured_poems'] = Poetry.objects.filter(
            is_published=True
        ).select_related('author', 'category').order_by('-views_count', '-created_at')[:3]
        return context


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
        # Increment view count safely
        try:
            Poetry.objects.filter(pk=obj.pk).update(views_count=obj.views_count + 1)
            obj.views_count += 1
        except Exception:
            # If update fails, continue without incrementing
            pass
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        poem = context.get('poem') or getattr(self, 'object', None)

        if poem is None:
            context['is_liked'] = False
            return context

        if self.request.user.is_authenticated:
            context['is_liked'] = ContentLike.objects.filter(
                user=self.request.user,
                content_type='poetry',
                object_id=poem.id,
            ).exists()
        else:
            context['is_liked'] = False

        return context


@login_required
def like_poetry(request, slug):
    """Like poetry"""
    poetry = get_object_or_404(Poetry, slug=slug, is_published=True)

    if request.method in {'POST', 'GET'}:
        return JsonResponse(toggle_content_like(request.user, 'poetry', poetry.id))

    return JsonResponse({'success': False, 'message': 'غلط درخواست'})
