"""
Quotes Views for Nawab Urdu Academy
"""

from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.db.models import Q
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import Quote, QuoteCollection
from core.models import Bookmark, Category, ContentLike
from core.services import build_seo_context, toggle_content_like, track_content_share, track_content_view


class QuoteListView(ListView):
    """Quote list view"""
    model = Quote
    template_name = 'quotes/quote_list.html'
    context_object_name = 'quotes'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Quote.objects.filter(is_published=True).select_related('author').prefetch_related('categories')
        
        # Filter by type
        quote_type = self.request.GET.get('type')
        if quote_type:
            queryset = queryset.filter(quote_type=quote_type)
        
        # Filter by category
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(categories__slug=category)
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(text__icontains=search) |
                Q(author__name__icontains=search)
            )
        
        # Sorting
        sort = self.request.GET.get('sort', 'latest')
        if sort == 'latest':
            queryset = queryset.order_by('-created_at')
        elif sort == 'popular':
            queryset = queryset.order_by('-views_count')
        elif sort == 'likes':
            queryset = queryset.order_by('-likes_count')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quote_types'] = Quote.QUOTE_TYPES
        context['categories'] = Category.objects.filter(category_type='quote', is_active=True)
        context['featured_quotes'] = Quote.objects.filter(is_featured=True, is_published=True).select_related('author')[:6]
        context['islamic_quotes'] = Quote.objects.filter(quote_type='islamic', is_published=True).select_related('author')[:6]
        context['motivational_quotes'] = Quote.objects.filter(quote_type='motivational', is_published=True).select_related('author')[:6]
        context.update(
            build_seo_context(
                self.request,
                title=f"Urdu Quotes | {settings.SITE_NAME}",
                description="Read inspirational, Islamic, and motivational Urdu quotes.",
                keywords=settings.SITE_KEYWORDS,
                og_type='website',
            )
        )
        return context


class QuoteDetailView(DetailView):
    """Quote detail view"""
    model = Quote
    template_name = 'quotes/quote_detail.html'
    context_object_name = 'quote'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Quote.objects.filter(is_published=True).select_related('author').prefetch_related('categories')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quote = self.get_object()
        
        track_content_view(self.request, quote, 'quote', quote.text)
        
        # Check if bookmarked
        if self.request.user.is_authenticated:
            context['is_bookmarked'] = Bookmark.objects.filter(
                user=self.request.user,
                content_type='quote',
                object_id=quote.id
            ).exists()
            context['is_liked'] = ContentLike.objects.filter(
                user=self.request.user,
                content_type='quote',
                object_id=quote.id
            ).exists()
        else:
            context['is_bookmarked'] = False
            context['is_liked'] = False
        
        # Related quotes
        context['related_quotes'] = Quote.objects.filter(
            quote_type=quote.quote_type,
            is_published=True
        ).exclude(id=quote.id)[:6]

        context.update(
            build_seo_context(
                self.request,
                title=quote.meta_title or f"{quote.text[:60]} | {settings.SITE_NAME}",
                description=quote.meta_description or quote.text[:160],
                keywords=settings.SITE_KEYWORDS,
                og_type='article',
                og_image=quote.background_image.url if quote.background_image else None,
            )
        )
        
        return context


class QuoteCollectionListView(ListView):
    """Quote collection list view"""
    model = QuoteCollection
    template_name = 'quotes/collection_list.html'
    context_object_name = 'collections'
    paginate_by = 12
    
    def get_queryset(self):
        return QuoteCollection.objects.filter(is_published=True)


class QuoteCollectionDetailView(DetailView):
    """Quote collection detail view"""
    model = QuoteCollection
    template_name = 'quotes/collection_detail.html'
    context_object_name = 'collection'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        collection = self.get_object()
        context['quotes'] = collection.quotes.filter(is_published=True)
        return context


def quotes_by_type(request, quote_type):
    """Quotes by type view"""
    quotes = Quote.objects.filter(quote_type=quote_type, is_published=True)
    
    context = {
        'quotes': quotes,
        'quote_type': quote_type,
        'quote_type_display': dict(Quote.QUOTE_TYPES).get(quote_type, quote_type),
        **build_seo_context(
            request,
            title=f"{dict(Quote.QUOTE_TYPES).get(quote_type, quote_type)} Quotes | {settings.SITE_NAME}",
            description="Browse Urdu quotes by type.",
            keywords=settings.SITE_KEYWORDS,
            og_type='website',
        ),
    }
    
    return render(request, 'quotes/quotes_by_type.html', context)


@login_required
def like_quote(request, slug):
    """Like quote"""
    quote = get_object_or_404(Quote, slug=slug, is_published=True)
    
    if request.method in {'POST', 'GET'}:
        return JsonResponse(toggle_content_like(request.user, 'quote', quote.id))
    
    return JsonResponse({'success': False, 'message': 'غلط درخواست'})


@login_required
def share_quote(request, slug):
    """Share quote"""
    quote = get_object_or_404(Quote, slug=slug, is_published=True)
    
    if request.method in {'POST', 'GET'}:
        return JsonResponse({
            'success': True,
            'shares_count': track_content_share(quote)
        })
    
    return JsonResponse({'success': False, 'message': 'غلط درخواست'})


def download_quote_image(request, slug):
    """Download quote as image"""
    quote = get_object_or_404(Quote, slug=slug, is_published=True)
    
    # This would typically generate an image using PIL or similar
    # For now, just return the quote data
    return JsonResponse({
        'success': True,
        'quote': quote.text,
        'author': quote.author.name,
        'background_image': quote.background_image.url if quote.background_image else None,
        'text_color': quote.text_color,
        'background_color': quote.background_color,
        'font_size': quote.font_size,
    })
