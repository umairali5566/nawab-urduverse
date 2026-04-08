"""
Core Views for Nawab Urdu Academy
"""

from pathlib import Path

from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.db.models import Q
from django.http import Http404, HttpResponse, JsonResponse
from django.urls import reverse
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.utils import timezone
from django.utils.text import slugify

from accounts.models import User
from novels.models import Novel, Chapter
from stories.models import Story
from poetry.models import Poetry
from quotes.models import Quote
from blog.models import BlogPost
from videos.models import Video
from .models import (
    Author,
    Bookmark,
    Category,
    Comment,
    ContactMessage,
    Content,
    NewsletterSubscriber,
    Notification,
    PremiumPlan,
)
from .services import (
    activate_membership,
    build_seo_context,
    create_notification,
    get_cross_content_suggestions,
    get_membership_plans,
    get_popular_content,
    get_search_suggestions,
    get_top_authors,
    get_trending_blogs,
    get_trending_content,
    get_trending_poetry,
    get_trending_quotes,
    get_trending_stories,
    get_trending_videos,
    mark_notifications_read,
    rate_limit_request,
    resolve_author_user,
    toggle_content_like,
    track_content_share,
    track_content_view,
    user_has_premium_access,
)


class BaseContentListView(ListView):
    """Base list view for content types"""

    paginate_by = 12

    def get_queryset(self):
        queryset = self.model.objects.filter(is_published=True).select_related('author')

        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)

        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search)

        sort = self.request.GET.get('sort', 'latest')
        if sort == 'latest':
            queryset = queryset.order_by('-published_at', '-created_at')
        elif sort == 'popular':
            queryset = queryset.order_by('-views_count', '-likes_count')
        elif sort == 'trending':
            queryset = queryset.order_by('-views_count', '-likes_count')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_items'] = self.model.objects.filter(is_featured=True, is_published=True).select_related('author')[:6]
        context.update(
            build_seo_context(
                self.request,
                title=f"{self.model._meta.verbose_name_plural} | {settings.SITE_NAME}",
                description=f"Read {self.model._meta.verbose_name_plural.lower()}.",
                keywords=settings.SITE_KEYWORDS,
                og_type='website',
            )
        )
        return context


class BaseContentDetailView(DetailView):
    """Base detail view for content types"""

    def get_queryset(self):
        return self.model.objects.filter(is_published=True).select_related('author')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        content_obj = self.object

        track_content_view(self.request, content_obj, self.content_type, content_obj.title)

        if self.request.user.is_authenticated:
            context['is_bookmarked'] = Bookmark.objects.filter(
                user=self.request.user,
                content_type=self.content_type,
                object_id=content_obj.id,
            ).exists()
            context['is_liked'] = ContentLike.objects.filter(
                user=self.request.user,
                content_type=self.content_type,
                object_id=content_obj.id,
            ).exists()
        else:
            context['is_bookmarked'] = False
            context['is_liked'] = False

        context['comments'] = Comment.objects.filter(
            content_type=self.content_type,
            object_id=content_obj.id,
            is_approved=True,
            parent=None,
        )

        context['related_items'] = (
            self.model.objects.filter(category=content_obj.category, is_published=True)
            .exclude(id=content_obj.id)[:4]
        )
        context['suggested_content'] = get_cross_content_suggestions(
            author=content_obj.author,
            categories=[content_obj.category] if content_obj.category else [],
            exclude_type=self.content_type,
            exclude_id=content_obj.id,
            limit=4,
            seed_text=f"{content_obj.title} {getattr(content_obj, 'content', '')}",
        )

        seo_title = content_obj.meta_title or f"{content_obj.title} | {settings.SITE_NAME}"
        seo_description = content_obj.meta_description or f"Read {content_obj.title}."
        seo_keywords = content_obj.meta_keywords or settings.SITE_KEYWORDS

        context.update(
            build_seo_context(
                self.request,
                title=seo_title,
                description=seo_description,
                keywords=seo_keywords,
                og_type='article',
                og_image=getattr(content_obj, 'background_image', None) or getattr(content_obj, 'cover_image', None) or getattr(content_obj, 'featured_image', None),
                canonical_url=self.request.build_absolute_uri(content_obj.get_absolute_url()),
            )
        )

        return context


def base_like_view(request, model, content_type, slug):
    """Generic like function for content types"""
    obj = get_object_or_404(model, slug=slug, is_published=True)

    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Login required.'}, status=403)

    if request.method in {'POST', 'GET'}:
        return JsonResponse(toggle_content_like(request.user, content_type, obj.id))

    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=405)


def base_share_view(request, model, content_type, slug):
    """Generic share function for content types"""
    obj = get_object_or_404(model, slug=slug, is_published=True)

    if request.method in {'POST', 'GET'}:
        return JsonResponse({'success': True, 'shares_count': track_content_share(obj)})

    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=405)


def home(request):
    """Modern Urdu search homepage."""
    categories = Category.objects.filter(category_type__in=['poetry', 'novel', 'blog'], is_active=True).order_by('name')
    authors = Author.objects.filter(is_active=True).order_by('name')[:25]

    # Latest poetry
    latest_poetry = Poetry.objects.filter(is_published=True).order_by('-created_at')[:9]

    # Featured content
    featured_content = Content.objects.filter(is_published=True).order_by('-created_at')[:6]

    # Stats
    total_poetry = Poetry.objects.filter(is_published=True).count()
    total_authors = Author.objects.filter(is_active=True).count()
    total_readers = 50000  # Placeholder, can be updated with actual user count

    context = {
        'categories': categories,
        'authors': authors,
        'latest_poetry': latest_poetry,
        'content_types': Content.CONTENT_TYPES,
        'featured_content': featured_content,
        'total_poetry': total_poetry,
        'total_authors': total_authors,
        'total_readers': total_readers,
        'show_superuser_panel': request.user.is_authenticated and request.user.is_superuser,
        **build_seo_context(
            request,
            title=f"{settings.SITE_NAME} | اردو شاعری کا بہترین منصہ",
            description="Urdu poetry, novels, and blog content search karein aur instant results ek hi page par dekhein.",
            keywords="Urdu search, poetry, novels, blog, search, nawab urdu academy",
            og_type='website',
        ),
    }
    return render(request, 'core/home.html', context)


def is_admin(user):
    return user.is_superuser


@user_passes_test(is_admin)
def admin_upload(request):
    categories = Category.objects.filter(category_type__in=['poetry', 'novel', 'blog'], is_active=True).order_by('name')
    authors = Author.objects.filter(is_active=True).order_by('name')[:50]
    error = ''

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        text = request.POST.get('text', '').strip()
        author_name = request.POST.get('author', '').strip()
        content_type = request.POST.get('content_type', 'poetry')
        category_slug = request.POST.get('category', '')
        bulk_text = request.POST.get('bulk_text', '').strip()

        if not author_name:
            error = 'مصنف کا نام فراہم کریں۔'
        elif bulk_text:
            author_obj, _ = Author.objects.get_or_create(
                name=author_name,
                defaults={'slug': slugify(author_name)}
            )
            category = Category.objects.filter(slug=category_slug, category_type=content_type).first()
            blocks = [block.strip() for block in bulk_text.split('---') if block.strip()]
            for idx, block in enumerate(blocks, start=1):
                slug = slugify(f"{title or 'content'}-{idx}")
                if Content.objects.filter(slug=slug).exists():
                    slug = f"{slug}-{idx}"
                Content.objects.create(
                    title=f"{title or 'Untitled'} {idx}",
                    slug=slug,
                    author=author_obj,
                    category=category,
                    content_type=content_type,
                    text=block,
                )
            return redirect('home')
        elif title and text:
            author_obj, _ = Author.objects.get_or_create(
                name=author_name,
                defaults={'slug': slugify(author_name)}
            )
            category = Category.objects.filter(slug=category_slug, category_type=content_type).first()
            slug = slugify(title)
            if Content.objects.filter(slug=slug).exists():
                slug = f"{slug}-{int(timezone.now().timestamp())}"
            Content.objects.create(
                title=title,
                slug=slug,
                author=author_obj,
                category=category,
                content_type=content_type,
                text=text,
            )
            return redirect('home')
        else:
            error = 'Title, author, and text are required for upload.'

    return render(request, 'core/admin_upload.html', {
        'categories': categories,
        'authors': authors,
        'error': error,
        **build_seo_context(
            request,
            title=f"Admin Upload | {settings.SITE_NAME}",
            description="Upload Urdu poetry, novels, and blogs from the frontend admin panel.",
            keywords="admin upload, urdu content, poetry upload",
            og_type='website',
        ),
    })


def search_api(request):
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', 'all').strip().lower()
    author_query = request.GET.get('author', '').strip()
    sort_by = request.GET.get('sort', 'latest').strip().lower()

    results = Content.objects.filter(is_published=True)
    if category in dict(Content.CONTENT_TYPES):
        results = results.filter(content_type=category)

    if author_query:
        results = results.filter(author__name__icontains=author_query)

    if query:
        results = results.filter(
            Q(title__icontains=query) |
            Q(text__icontains=query) |
            Q(author__name__icontains=query)
        )

    if sort_by == 'popular':
        results = results.order_by('-created_at')
    else:
        results = results.order_by('-created_at')

    results = results.select_related('author', 'category')[:50]

    serialized = []
    for item in results:
        serialized.append({
            'title': item.title,
            'author': item.author.name,
            'category': item.category.name if item.category else '',
            'content_type': item.content_type,
            'text': item.text,
            'created_at': item.created_at.strftime('%Y-%m-%d'),
        })

    suggestions = []
    if query:
        suggestion_qs = Content.objects.filter(is_published=True).filter(
            Q(title__icontains=query) |
            Q(text__icontains=query) |
            Q(author__name__icontains=query)
        ).select_related('author')[:10]
        seen = set()
        for item in suggestion_qs:
            if item.title not in seen:
                seen.add(item.title)
                suggestions.append(item.title)
            if item.author.name not in seen:
                seen.add(item.author.name)
                suggestions.append(item.author.name)
            if len(suggestions) >= 10:
                break

    return JsonResponse({
        'success': True,
        'results': serialized,
        'suggestions': suggestions,
    })


def poetry_search_api(request):
    """API endpoint for live poetry search on homepage."""
    query = request.GET.get('q', '').strip()
    if not query or len(query) < 2:
        return JsonResponse({'success': True, 'results': []})

    # Search poetry by title, author name, or content
    poetry_results = Poetry.objects.filter(is_published=True).filter(
        Q(title__icontains=query) |
        Q(author__name__icontains=query) |
        Q(content__icontains=query)
    ).select_related('author').order_by('-views_count', '-created_at')[:10]

    results = []
    for poetry in poetry_results:
        results.append({
            'id': poetry.id,
            'title': poetry.title,
            'author': poetry.author.name,
            'content_preview': poetry.content[:150] + '...' if len(poetry.content) > 150 else poetry.content,
            'url': poetry.get_absolute_url(),
            'views': poetry.views_count,
        })

    return JsonResponse({'success': True, 'results': results})


def about(request):
    """About page view"""
    stats = {
        'novels_count': Novel.objects.filter(is_published=True).count(),
        'stories_count': Story.objects.filter(is_published=True).count(),
        'poetry_count': Poetry.objects.filter(is_published=True).count(),
        'authors_count': Author.objects.filter(is_active=True).count(),
        'quotes_count': Quote.objects.filter(is_published=True).count(),
        'videos_count': Video.objects.filter(is_published=True).count(),
    }
    return render(request, 'core/about.html', stats)


def all_categories(request):
    """Categories landing page view."""
    categories = Category.objects.filter(is_active=True).order_by('category_type', 'name')

    grouped_categories = []
    for category_type, label in Category.CATEGORY_TYPES:
        items = [category for category in categories if category.category_type == category_type]
        if items:
            grouped_categories.append({
                'key': category_type,
                'label': label,
                'items': items,
            })

    context = {
        'categories': categories,
        'grouped_categories': grouped_categories,
        **build_seo_context(
            request,
            title=f"All Categories | {settings.SITE_NAME}",
            description="Browse all active Urdu literature categories across poetry, novels, stories, quotes, blogs, and videos.",
            keywords=f"categories, genres, {settings.SITE_KEYWORDS}",
            og_type='website',
        ),
    }
    return render(request, 'core/categories.html', context)


def hover_cards_demo(request):
    """Demo page for hover cards with dynamic content reveal effects"""
    return render(request, 'core/hover-cards-demo.html')


def contact(request):
    """Contact page view"""
    if request.method == 'POST':
        limited, retry_after = rate_limit_request(request, 'contact_form', limit=4, window=300)
        if limited:
            return JsonResponse({
                'success': False,
                'message': f'Please wait {retry_after} seconds before sending another message.'
            }, status=429)

        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        
        return JsonResponse({'success': True, 'message': 'آپ کا پیغام بھیج دیا گیا ہے۔ شکریہ!'})
    
    return render(request, 'core/contact.html')


def privacy_policy(request):
    """Privacy policy page"""
    return render(request, 'core/privacy_policy.html')


def terms_of_service(request):
    """Terms of service page"""
    return render(request, 'core/terms_of_service.html')


def robots_txt(request):
    """Serve robots.txt with sitemap location."""
    sitemap_url = request.build_absolute_uri(
        reverse('django.contrib.sitemaps.views.sitemap')
    )
    lines = [
        "User-agent: *",
        "Allow: /",
        "",
        f"Sitemap: {sitemap_url}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def service_worker(request):
    """Serve the service worker with full-app scope enabled."""
    sw_path = Path(settings.BASE_DIR) / 'static' / 'sw.js'
    if not sw_path.exists():
        raise Http404('Service worker not found.')

    response = HttpResponse(
        sw_path.read_text(encoding='utf-8'),
        content_type='application/javascript; charset=utf-8',
    )
    response['Service-Worker-Allowed'] = '/'
    response['Cache-Control'] = 'no-cache'
    return response


class AuthorListView(ListView):
    """Author list view"""
    model = Author
    template_name = 'core/author_list.html'
    context_object_name = 'authors'
    paginate_by = 24
    
    def get_queryset(self):
        queryset = Author.objects.filter(is_active=True)
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(bio__icontains=search)
            )
        
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['featured_authors'] = Author.objects.filter(is_featured=True, is_active=True)[:6]
        return context


class AuthorDetailView(DetailView):
    """Author detail view"""
    model = Author
    template_name = 'core/author_detail.html'
    context_object_name = 'author'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = self.get_object()

        # Get all content by this author
        novels = Novel.objects.filter(author=author, is_published=True).order_by('-published_at', '-created_at')
        stories = Story.objects.filter(author=author, is_published=True).order_by('-published_at', '-created_at')
        poetry = Poetry.objects.filter(author=author, is_published=True).order_by('-published_at', '-created_at')
        quotes = Quote.objects.filter(author=author, is_published=True).order_by('-created_at')
        blogs = BlogPost.objects.filter(author=author, is_published=True).order_by('-published_at', '-created_at')
        videos = Video.objects.filter(author=author, is_published=True).order_by('-published_at', '-created_at')

        # Combine all content for a unified list
        all_content = []
        for item in novels:
            all_content.append({'type': 'novel', 'item': item, 'date': item.published_at or item.created_at})
        for item in stories:
            all_content.append({'type': 'story', 'item': item, 'date': item.created_at})
        for item in poetry:
            all_content.append({'type': 'poetry', 'item': item, 'date': item.published_at or item.created_at})
        for item in quotes:
            all_content.append({'type': 'quote', 'item': item, 'date': item.created_at})
        for item in blogs:
            all_content.append({'type': 'blog', 'item': item, 'date': item.published_at or item.created_at})
        for item in videos:
            all_content.append({'type': 'video', 'item': item, 'date': item.published_at or item.created_at})

        # Sort by date descending
        all_content.sort(key=lambda x: x['date'], reverse=True)

        context['all_content'] = all_content
        context['published_total'] = author.published_content_total
        context.update(
            build_seo_context(
                self.request,
                title=f"Content by {author.name} | {settings.SITE_NAME}",
                description=f"Browse all content by {author.name} on {settings.SITE_NAME}",
            )
        )
        
        return context


def search(request):
    """Global search view"""
    query = request.GET.get('q', '')
    content_filter = request.GET.get('type', 'all')
    content_filter = content_filter if content_filter in {'all', 'poetry', 'blog', 'video', 'quote', 'story', 'novel', 'author'} else 'all'
    content_filters = ['all', 'poetry', 'blog', 'video', 'novel', 'quote', 'story', 'author']
    
    if not query:
        return render(request, 'core/search.html', {
            'query': '',
            'content_filter': content_filter,
            'content_filters': content_filters,
            'results': None,
            **build_seo_context(
                request,
                title=f"Search | {settings.SITE_NAME}",
                description=f"Search Urdu novels, stories, poetry, quotes, and blog posts on {settings.SITE_NAME}.",
                keywords=settings.SITE_KEYWORDS,
                og_type='website',
            ),
        })

    if query:
        try:
            author = Author.objects.get(name__iexact=query)
            return redirect(reverse('author_profile', kwargs={'author_name': author.name}))
        except Author.DoesNotExist:
            pass

    from ai_features.services import perform_ai_search

    ai_payload = perform_ai_search(query, content_type=content_filter, limit=18)

    novels = ai_payload['grouped_objects']['novel'] if content_filter in {'all', 'novel'} else []
    stories = ai_payload['grouped_objects']['story'] if content_filter in {'all', 'story'} else []
    poetry = ai_payload['grouped_objects']['poetry'] if content_filter in {'all', 'poetry'} else []
    blogs = ai_payload['grouped_objects']['blog'] if content_filter in {'all', 'blog'} else []
    videos = ai_payload['grouped_objects']['video'] if content_filter in {'all', 'video'} else []
    quotes = ai_payload['grouped_objects']['quote'] if content_filter in {'all', 'quote'} else []
    authors = ai_payload['grouped_objects']['author'] if content_filter in {'all', 'author'} else []

    total_results = (
        len(novels)
        + len(stories)
        + len(poetry)
        + len(quotes)
        + len(blogs)
        + len(videos)
        + len(authors)
    )
    
    context = {
        'query': query,
        'content_filter': content_filter,
        'content_filters': content_filters,
        'total_results': total_results,
        'novels': novels,
        'stories': stories,
        'poetry': poetry,
        'quotes': quotes,
        'blogs': blogs,
        'videos': videos,
        'authors': authors,
        'ai_intent': ai_payload['intent'],
        **build_seo_context(
            request,
            title=f'"{query}" search results | {settings.SITE_NAME}',
            description=f'{total_results} search results for "{query}" on {settings.SITE_NAME}.',
            keywords=f'{query}, {settings.SITE_KEYWORDS}',
            og_type='website',
        ),
    }
    
    return render(request, 'core/search.html', context)


def newsletter_subscribe(request):
    """Newsletter subscription"""
    if request.method == 'POST':
        limited, retry_after = rate_limit_request(request, 'newsletter', limit=4, window=300)
        if limited:
            return JsonResponse({
                'success': False,
                'message': f'Please wait {retry_after} seconds before trying again.'
            }, status=429)

        email = request.POST.get('email')
        name = request.POST.get('name', '')
        
        if email:
            subscriber, created = NewsletterSubscriber.objects.get_or_create(
                email=email,
                defaults={'name': name}
            )
            
            if created:
                return JsonResponse({
                    'success': True,
                    'message': 'آپ کامیابی سے سبسکرائب ہو گئے ہیں!'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'یہ ای میل پہلے سے سبسکرائب ہے۔'
                })
        
        return JsonResponse({
            'success': False,
            'message': 'براہ کرم درست ای میل درج کریں۔'
        })
    
    return JsonResponse({'success': False, 'message': 'غلط درخواست'})


@login_required
def add_bookmark(request, content_type, object_id):
    """Add bookmark"""
    if request.method == 'POST':
        bookmark, created = Bookmark.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=object_id
        )
        
        if created:
            return JsonResponse({
                'success': True,
                'message': 'بک مارک شامل کر دیا گیا',
                'bookmarked': True
            })
        else:
            bookmark.delete()
            return JsonResponse({
                'success': True,
                'message': 'بک مارک ہٹا دیا گیا',
                'bookmarked': False
            })
    
    return JsonResponse({'success': False, 'message': 'غلط درخواست'})


@login_required
def add_comment(request, content_type, object_id):
    """Add comment"""
    if request.method == 'POST':
        limited, retry_after = rate_limit_request(request, 'comment', limit=6, window=120)
        if limited:
            return JsonResponse({
                'success': False,
                'message': f'Please wait {retry_after} seconds before posting again.'
            }, status=429)

        text = request.POST.get('text')
        parent_id = request.POST.get('parent_id')
        
        if text:
            comment = Comment.objects.create(
                user=request.user,
                content_type=content_type,
                object_id=object_id,
                text=text,
                parent_id=parent_id if parent_id else None
            )

            content_obj = None
            owner = None
            if content_type == 'novel':
                content_obj = Novel.objects.filter(id=object_id, is_published=True).first()
                if content_obj is None:
                    chapter = Chapter.objects.filter(
                        id=object_id,
                        is_published=True,
                    ).select_related('novel__author').first()
                    if chapter:
                        content_obj = chapter
                        owner = resolve_author_user(chapter.novel.author)
            else:
                model_map = {
                    'story': Story,
                    'poetry': Poetry,
                    'quote': Quote,
                    'blog': BlogPost,
                    'video': Video,
                }
                model = model_map.get(content_type)
                if model:
                    content_obj = model.objects.filter(id=object_id, is_published=True).select_related('author').first()

            if owner is None and content_obj is not None:
                owner = resolve_author_user(getattr(content_obj, 'author', None))

            if owner and owner != request.user:
                create_notification(
                    owner,
                    notification_type='comment',
                    title='New comment',
                    message=f'{request.user.get_full_name() or request.user.username} commented on your content.',
                    actor=request.user,
                    link=content_obj.get_absolute_url() if content_obj and hasattr(content_obj, 'get_absolute_url') else '',
                    content_type=content_type,
                    object_id=object_id,
                )
            
            return JsonResponse({
                'success': True,
                'message': 'آپ کا تبصرہ شامل کر دیا گیا',
                'comment_id': comment.id
            })
        
        return JsonResponse({
            'success': False,
            'message': 'براہ کرم تبصرہ درج کریں'
        })
    
    return JsonResponse({'success': False, 'message': 'غلط درخواست'})


@login_required
def bookmarks_dashboard(request):
    """User bookmarks dashboard showing saved items across content types"""
    bookmarks = Bookmark.objects.filter(user=request.user).order_by('-created_at')

    resolved = []
    for b in bookmarks:
        obj = None
        url = None
        title = None
        thumb = None
        try:
            if b.content_type == 'novel':
                obj = Novel.objects.filter(id=b.object_id, is_published=True).first()
                if obj:
                    url = obj.get_absolute_url()
                    title = obj.title
                    try:
                        thumb = obj.cover_image.url
                    except Exception:
                        thumb = None
            elif b.content_type == 'story':
                obj = Story.objects.filter(id=b.object_id, is_published=True).first()
                if obj:
                    url = obj.get_absolute_url()
                    title = obj.title
                    try:
                        thumb = obj.featured_image.url
                    except Exception:
                        thumb = None
            elif b.content_type == 'poetry':
                obj = Poetry.objects.filter(id=b.object_id, is_published=True).first()
                if obj:
                    url = obj.get_absolute_url()
                    title = obj.title
            elif b.content_type == 'blog':
                obj = BlogPost.objects.filter(id=b.object_id, is_published=True).first()
                if obj:
                    url = obj.get_absolute_url()
                    title = obj.title
            elif b.content_type == 'quote':
                obj = Quote.objects.filter(id=b.object_id, is_published=True).first()
                if obj:
                    url = obj.get_absolute_url()
                    title = (obj.text[:60] + '...') if len(obj.text) > 60 else obj.text
            elif b.content_type == 'video':
                obj = Video.objects.filter(id=b.object_id, is_published=True).first()
                if obj:
                    url = obj.get_absolute_url()
                    title = obj.title
                    try:
                        thumb = obj.thumbnail.url
                    except Exception:
                        thumb = None
        except Exception:
            obj = None
        
        if obj and url and title:
            resolved.append({
                'id': b.id,
                'content_type': b.content_type,
                'object_id': b.object_id,
                'title': title,
                'url': url,
                'thumb': thumb,
                'created_at': b.created_at,
            })

    paginator = Paginator(resolved, 20)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)

    return render(request, 'core/bookmarks.html', {
        'page_obj': page_obj,
        'bookmarks': page_obj.object_list,
        'is_paginated': page_obj.has_other_pages(),
        **build_seo_context(
            request,
            title=f"My Bookmarks | {settings.SITE_NAME}",
            description=f"Saved posts and reading list for {request.user.get_full_name() or request.user.username}.",
            keywords=settings.SITE_KEYWORDS,
            og_type='profile',
            robots='noindex, nofollow',
        ),
    })


def category_detail(request, slug):
    """Category detail view"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    
    # Get content based on category type
    content = []
    if category.category_type == 'novel':
        content = Novel.objects.filter(category=category, is_published=True)
    elif category.category_type == 'story':
        content = Story.objects.filter(categories=category, is_published=True)
    elif category.category_type == 'poetry':
        content = Poetry.objects.filter(category=category, is_published=True)
    elif category.category_type == 'quote':
        content = Quote.objects.filter(categories=category, is_published=True)
    elif category.category_type == 'blog':
        content = BlogPost.objects.filter(categories=category, is_published=True)
    elif category.category_type == 'video':
        content = Video.objects.filter(categories=category, is_published=True)
    
    paginator = Paginator(content, 12)
    page = request.GET.get('page')
    content_page = paginator.get_page(page)
    
    context = {
        'category': category,
        'content': content_page,
        **build_seo_context(
            request,
            title=f"{category.name} | {settings.SITE_NAME}",
            description=(category.description[:160] if category.description else settings.SITE_DESCRIPTION),
            keywords=f"{category.name}, {settings.SITE_KEYWORDS}",
            og_type='website',
            og_image=category.image.url if category.image else None,
        ),
    }
    
    return render(request, 'core/category_detail.html', context)


def search_suggestions(request):
    """Autocomplete suggestions for the search bar."""
    query = request.GET.get('q', '')
    return JsonResponse({
        'success': True,
        'suggestions': get_search_suggestions(
            query,
            limit=getattr(settings, 'SEARCH_SUGGESTION_LIMIT', 8),
        ),
    })


@login_required
def toggle_like(request, content_type, object_id):
    """Generic like endpoint for all content types."""
    if request.method not in {'POST', 'GET'}:
        return JsonResponse({'success': False, 'message': 'Method not allowed.'}, status=405)
    payload = toggle_content_like(request.user, content_type, object_id)
    return JsonResponse(payload, status=200 if payload.get('success') else 400)


def track_share(request, content_type, object_id):
    """Generic share tracker used by reader and media templates."""
    if request.method not in {'POST', 'GET'}:
        return JsonResponse({'success': False, 'message': 'Method not allowed.'}, status=405)

    obj = None
    if content_type == 'novel':
        obj = Novel.objects.filter(id=object_id, is_published=True).first()
    elif content_type == 'story':
        obj = Story.objects.filter(id=object_id, is_published=True).first()
    elif content_type == 'poetry':
        obj = Poetry.objects.filter(id=object_id, is_published=True).first()
    elif content_type == 'quote':
        obj = Quote.objects.filter(id=object_id, is_published=True).first()
    elif content_type == 'blog':
        obj = BlogPost.objects.filter(id=object_id, is_published=True).first()
    elif content_type == 'video':
        obj = Video.objects.filter(id=object_id, is_published=True).first()

    if obj is None:
        return JsonResponse({'success': False, 'message': 'Content not found.'}, status=404)

    return JsonResponse({'success': True, 'shares_count': track_content_share(obj)})




@login_required
def notifications_view(request):
    """Notification inbox page."""
    notifications = Notification.objects.filter(user=request.user).select_related('actor').order_by('-created_at')
    paginator = Paginator(notifications, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'accounts/notifications.html', {
        'page_obj': page_obj,
        'notifications': page_obj.object_list,
        **build_seo_context(
            request,
            title=f"Notifications | {settings.SITE_NAME}",
            description="Your recent engagement and account notifications.",
            keywords=settings.SITE_KEYWORDS,
            og_type='profile',
            robots='noindex, nofollow',
        ),
    })


@login_required
def notifications_mark_read(request):
    """Mark all notifications as read."""
    if request.method not in {'POST', 'GET'}:
        return JsonResponse({'success': False, 'message': 'Method not allowed.'}, status=405)

    updated = mark_notifications_read(request.user)
    return JsonResponse({'success': True, 'updated': updated})


@login_required
def membership_view(request):
    """Membership and monetization landing page."""
    plans = get_membership_plans()
    premium_novels = Novel.objects.filter(is_premium=True, is_published=True).select_related('author')[:6]
    related_picks = get_trending_poetry(limit=4)

    return render(request, 'core/membership.html', {
        'plans': plans,
        'membership': getattr(request.user, 'membership', None),
        'has_premium_access': user_has_premium_access(request.user),
        'premium_novels': premium_novels,
        'related_picks': related_picks,
        **build_seo_context(
            request,
            title=f"Premium Membership | {settings.SITE_NAME}",
            description=f"Unlock premium Urdu literature, reader tools, and member-only access on {settings.SITE_NAME}.",
            keywords=settings.SITE_KEYWORDS,
            og_type='website',
        ),
    })


@login_required
def activate_membership_view(request, slug):
    """Demo-friendly membership activation endpoint."""
    if request.method != 'POST':
        return redirect('membership')

    plan = get_object_or_404(PremiumPlan, slug=slug, is_active=True)
    activate_membership(request.user, plan)
    return redirect('membership')
