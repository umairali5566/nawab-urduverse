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
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

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


def home(request):
    """Rekhta-style homepage focused on Urdu poetry"""

    # Latest Poetry
    latest_poetry = list(
        Poetry.objects.filter(is_published=True)
        .select_related('author')
        .order_by('-created_at')[:12]
    )

    # Featured Poetry
    featured_poetry = Poetry.objects.filter(is_featured=True, is_published=True).select_related('author').first()

    # Categories (Poetry Types)
    poetry_categories = [
        {'name': 'غزل', 'slug': 'ghazal', 'count': Poetry.objects.filter(poetry_type='ghazal', is_published=True).count()},
        {'name': 'نظم', 'slug': 'nazm', 'count': Poetry.objects.filter(poetry_type='nazm', is_published=True).count()},
        {'name': 'شاعری', 'slug': 'shayari', 'count': Poetry.objects.filter(poetry_type='shayari', is_published=True).count()},
        {'name': 'اقتباس', 'slug': 'quotes', 'count': Poetry.objects.filter(poetry_type='qata', is_published=True).count()},
    ]

    # Featured Authors
    featured_authors = Author.objects.filter(is_featured=True, is_active=True).select_related()[:6]

    # Stats
    total_poetry = Poetry.objects.filter(is_published=True).count()
    total_authors = Author.objects.filter(is_active=True).count()

    context = {
        'latest_poetry': latest_poetry,
        'featured_poetry': featured_poetry,
        'poetry_categories': poetry_categories,
        'featured_authors': featured_authors,
        'total_poetry': total_poetry,
        'total_authors': total_authors,
        **build_seo_context(
            request,
            title=f"{settings.SITE_NAME} | اردو شاعری کا بہترین پلیٹ فارم",
            description="اردو شاعری، غزلیں، نظمیں اور مشہور شاعروں کی تخلیقات پڑھیں۔",
            keywords="اردو شاعری, غزل, نظم, شاعر, poetry, urdu",
            og_type='website',
        ),
        'show_superuser_panel': request.user.is_authenticated and request.user.is_superuser,
    }
    return render(request, 'core/home.html', context)


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
