"""
Poetry Views for Nawab Urdu Academy
"""

from django.conf import settings
from django.db.models import F, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView

from core.models import Author, Bookmark, Category, Comment, Content, ContentLike
from core.services import (
    build_seo_context,
    generate_poetry_from_prompt,
    get_cross_content_suggestions,
    rate_limit_request,
    toggle_content_like,
    track_content_share,
    track_content_view,
)
from core.views import BaseContentListView, BaseContentDetailView, base_like_view, base_share_view
from .models import Poetry, PoetryCollection
from .tts import generate_tts_audio


class PoetryListView(BaseContentListView):
    """Poetry list view"""

    model = Poetry
    template_name = "poetry/poetry_list.html"
    context_object_name = "poems"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["poetry_types"] = Poetry.POETRY_TYPES
        context["moods"] = Poetry.MOOD_CHOICES
        context["categories"] = Category.objects.filter(category_type="poetry", is_active=True)
        context["love_poetry"] = Poetry.objects.filter(mood="love", is_published=True).select_related("author")[:6]
        context["sad_poetry"] = Poetry.objects.filter(mood="sad", is_published=True).select_related("author")[:6]
        return context


class PoetryDetailView(BaseContentDetailView):
    """Poetry detail view"""

    model = Poetry
    template_name = "poetry/poetry_detail.html"
    context_object_name = "poem"
    slug_url_kwarg = "slug"
    content_type = "poetry"

    def get_object(self, queryset=None):
        slug = self.kwargs.get("slug")
        return get_object_or_404(
            Poetry.objects.select_related("author", "category"),
            slug=slug,
            is_published=True,
        )

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        requested_author_slug = kwargs.get("author_slug")
        canonical_author_slug = self.object.author.slug

        if requested_author_slug and requested_author_slug != canonical_author_slug:
            return redirect(self.object.get_absolute_url(), permanent=True)

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        poem = self.object

        # Override suggested_content for poetry
        context["suggested_content"] = get_cross_content_suggestions(
            author=poem.author,
            categories=[poem.category] if poem.category else [],
            exclude_type="poetry",
            exclude_id=poem.id,
            limit=4,
            seed_text=f"{poem.title} {poem.plain_text_content}",
        )

        # Override SEO for poetry
        seo_title = poem.meta_title or f"{poem.title} Poetry by {poem.author.name} | {settings.SITE_NAME}"
        seo_description = poem.meta_description or (
            f"Read {poem.title} poetry by {poem.author.name} in beautiful Urdu Nastaliq format on {settings.SITE_NAME}."
        )
        seo_keywords = poem.meta_keywords or f"{poem.title}, {poem.author.name}, Urdu poetry, {settings.SITE_KEYWORDS}"

        context.update(
            build_seo_context(
                self.request,
                title=seo_title,
                description=seo_description,
                keywords=seo_keywords,
                og_type="article",
                og_image=poem.background_image.url if poem.background_image else None,
                canonical_url=self.request.build_absolute_uri(poem.get_absolute_url()),
            )
        )

        return context


class CollectionListView(ListView):
    """Poetry collection list view"""

    model = PoetryCollection
    template_name = "poetry/collection_list.html"
    context_object_name = "collections"
    paginate_by = 12

    def get_queryset(self):
        return PoetryCollection.objects.filter(is_published=True)


class CollectionDetailView(DetailView):
    """Poetry collection detail view"""

    model = PoetryCollection
    template_name = "poetry/collection_detail.html"
    context_object_name = "collection"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        collection = self.get_object()
        context["poems"] = collection.poems.filter(is_published=True)
        return context


def poetry_by_type(request, poetry_type):
    """Poetry by type view"""

    poems = Poetry.objects.filter(poetry_type=poetry_type, is_published=True)

    context = {
        "poems": poems,
        "poetry_type": poetry_type,
        "poetry_type_display": dict(Poetry.POETRY_TYPES).get(poetry_type, poetry_type),
        **build_seo_context(
            request,
            title=f"{dict(Poetry.POETRY_TYPES).get(poetry_type, poetry_type)} Poetry | {settings.SITE_NAME}",
            description="Browse Urdu poetry by type.",
            keywords=settings.SITE_KEYWORDS,
            og_type="website",
        ),
    }

    return render(request, "poetry/poetry_by_type.html", context)


def poetry_by_mood(request, mood):
    """Poetry by mood view"""

    poems = Poetry.objects.filter(mood=mood, is_published=True)

    context = {
        "poems": poems,
        "mood": mood,
        "mood_display": dict(Poetry.MOOD_CHOICES).get(mood, mood),
        **build_seo_context(
            request,
            title=f"{dict(Poetry.MOOD_CHOICES).get(mood, mood)} Poetry | {settings.SITE_NAME}",
            description="Browse Urdu poetry by mood.",
            keywords=settings.SITE_KEYWORDS,
            og_type="website",
        ),
    }

    return render(request, "poetry/poetry_by_mood.html", context)


def _resolve_poem(slug, author_slug=None):
    poem = get_object_or_404(Poetry, slug=slug, is_published=True)
    if author_slug and poem.author.slug != author_slug:
        # Canonical route mismatch; still operate on the poem by slug.
        return poem
    return poem


def like_poetry(request, slug, author_slug=None):
    """Like poetry and return updated counter."""
    poem = _resolve_poem(slug=slug, author_slug=author_slug)
    return base_like_view(request, Poetry, "poetry", poem.slug)


def share_poetry(request, slug, author_slug=None):
    """Track poetry shares for trending scoring."""
    poem = _resolve_poem(slug=slug, author_slug=author_slug)
    return base_share_view(request, Poetry, "poetry", poem.slug)


def ai_studio(request):
    """Urdu content search page."""
    query = request.GET.get('q')
    results = []
    if query:
        results = Content.objects.filter(
            Q(text__icontains=query) |
            Q(title__icontains=query) |
            Q(author__name__icontains=query),
            is_published=True
        ).select_related('author', 'category')[:20]

    return render(
        request,
        "poetry/ai_studio.html",
        {
            'query': query,
            'results': results,
            **build_seo_context(
                request,
                title=f"Urdu Content Search | {settings.SITE_NAME}",
                description="Search Urdu poetry, novels, and blogs in our collection.",
                keywords=settings.SITE_KEYWORDS,
                og_type="website",
            ),
        },
    )


def ai_generate(request):
    """AJAX endpoint for the AI poetry generator."""
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request."}, status=405)

    limited, retry_after = rate_limit_request(request, "ai_poetry", limit=6, window=300)
    if limited:
        return JsonResponse(
            {"success": False, "message": f"Please wait {retry_after} seconds before generating again."},
            status=429,
        )

    payload = generate_poetry_from_prompt(
        request.POST.get("topic", ""),
        mood=request.POST.get("mood", "romantic"),
        poetry_type=request.POST.get("poetry_type", "ghazal"),
        line_count=request.POST.get("line_count", 6),
    )
    return JsonResponse({"success": True, **payload})


def poetry_tts(request, slug, author_slug=None):
    """Generate or return cached Urdu MP3 narration for poetry text."""

    poem = _resolve_poem(slug=slug, author_slug=author_slug)
    clean_text = poem.plain_text_content

    if not clean_text:
        return JsonResponse(
            {"success": False, "message": "Poetry text is empty and cannot be converted to audio."},
            status=400,
        )

    try:
        audio_url, engine = generate_tts_audio(text=clean_text, cache_key=f"poetry-{poem.id}")
    except Exception as exc:
        return JsonResponse(
            {
                "success": False,
                "message": "TTS engine is unavailable right now. Install/configure edge-tts or gTTS.",
                "error": str(exc),
            },
            status=503,
        )

    return JsonResponse(
        {
            "success": True,
            "audio_url": audio_url,
            "engine": engine,
            "title": poem.title,
        }
    )


def legacy_poetry_redirect(request, slug):
    """Redirect old /poetry/<slug>/ URL to canonical author-based URL."""

    poem = get_object_or_404(Poetry, slug=slug, is_published=True)
    return redirect(poem.get_absolute_url(), permanent=True)


def author_profile(request, author_name):
    """Author profile page showing poetry in Rekhta-style layout"""
    author = get_object_or_404(Author, name=author_name)
    
    category_filter = request.GET.get('category', 'all')
    
    if category_filter == 'all':
        poems = Poetry.objects.filter(author=author, is_published=True).order_by('-published_at', '-created_at')
    elif category_filter in ['ghazal', 'nazm']:
        poems = Poetry.objects.filter(author=author, poetry_type=category_filter, is_published=True).order_by('-published_at', '-created_at')
    else:
        poems = Poetry.objects.filter(author=author, is_published=True).order_by('-published_at', '-created_at')
        category_filter = 'all'
    
    total_poetry = Poetry.objects.filter(author=author, is_published=True).count()
    ghazals_count = Poetry.objects.filter(author=author, poetry_type='ghazal', is_published=True).count()
    nazms_count = Poetry.objects.filter(author=author, poetry_type='nazm', is_published=True).count()
    
    context = {
        'author': author,
        'poems': poems,
        'category_filter': category_filter,
        'total_poetry': total_poetry,
        'ghazals_count': ghazals_count,
        'nazms_count': nazms_count,
        **build_seo_context(
            request,
            title=f"{author.name} Poetry | {settings.SITE_NAME}",
            description=f"Read poetry by {author.name}. {total_poetry} poems including {ghazals_count} ghazals and {nazms_count} nazms.",
            keywords=f"{author.name}, Urdu poetry, ghazal, nazm",
            og_type='profile',
            og_image=author.image.url if author.image else None,
        ),
    }
    
    return render(request, 'poetry/author_profile.html', context)
 
class PoetryPremiumView(DetailView):
    """Premium distraction-free poetry reading view"""

    model = Poetry
    template_name = "poetry/poetry_premium.html"
    context_object_name = "poem"
    slug_url_kwarg = "slug"

    def get_object(self, queryset=None):
        slug = self.kwargs.get("slug")
        return get_object_or_404(
            Poetry.objects.select_related("author", "category"),
            slug=slug,
            is_published=True,
        )

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        requested_author_slug = kwargs.get("author_slug")
        canonical_author_slug = self.object.author.slug

        if requested_author_slug and requested_author_slug != canonical_author_slug:
            return redirect(self.object.get_absolute_url(), permanent=True)

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        poem = self.object

        track_content_view(self.request, poem, "poetry", poem.title)

        if self.request.user.is_authenticated:
            context["is_bookmarked"] = Bookmark.objects.filter(
                user=self.request.user,
                content_type="poetry",
                object_id=poem.id,
            ).exists()
            context["is_liked"] = ContentLike.objects.filter(
                user=self.request.user,
                content_type="poetry",
                object_id=poem.id,
            ).exists()
        else:
            context["is_bookmarked"] = False
            context["is_liked"] = False

        context["comments"] = Comment.objects.filter(
            content_type="poetry",
            object_id=poem.id,
            is_approved=True,
            parent=None,
        ).select_related("user", "user__profile")[:10]

        context["related_poems"] = (
            Poetry.objects.filter(
                author=poem.author,
                is_published=True,
            )
            .exclude(id=poem.id)
            .order_by("-published_at")[:4]
        )

        context["suggested_content"] = get_cross_content_suggestions(
            author=poem.author,
            categories=[poem.category] if poem.category else [],
            exclude_type="poetry",
            exclude_id=poem.id,
            limit=4,
            seed_text=f"{poem.title} {poem.plain_text_content}",
        )

        seo_title = poem.meta_title or f"{poem.title} Poetry by {poem.author.name} | {settings.SITE_NAME}"
        seo_description = poem.meta_description or (
            f"Read {poem.title} poetry by {poem.author.name} in beautiful Urdu Nastaliq format on {settings.SITE_NAME}."
        )
        seo_keywords = poem.meta_keywords or f"{poem.title}, {poem.author.name}, Urdu poetry, {settings.SITE_KEYWORDS}"

        context.update(
            build_seo_context(
                self.request,
                title=seo_title,
                description=seo_description,
                keywords=seo_keywords,
                og_type="article",
                og_image=poem.background_image.url if poem.background_image else None,
                canonical_url=self.request.build_absolute_uri(poem.get_absolute_url()),
            )
        )

        return context
