from django.contrib import messages
from datetime import timedelta
import csv
import io
from functools import wraps

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.text import slugify

from accounts.models import UserActivity
from blog.models import BlogPost
from core.models import (
    Author,
    Category,
    ContactMessage,
    NewsletterSubscriber,
    Notification,
    PremiumPlan,
    UserMembership,
)
from core.services import get_trending_blogs, get_trending_content, get_trending_poetry, get_trending_videos
from novels.models import Novel
from poetry.models import Poetry
from quotes.models import Quote
from stories.models import Story
from videos.models import Video
from .constants import ALLOWED_EXTENSIONS, CONTENT_TYPES, MAX_FILE_SIZE, VALIDATION_MESSAGES


def admin_required(view_func):
    return user_passes_test(
        lambda u: u.is_active and (u.is_staff or u.is_superuser),
        login_url='home',
    )(view_func)




def superuser_upload_required(view_func):
    @login_required
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, 'Access denied. Superuser required.')
            return redirect('home')
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def _build_unique_slug(model, raw_value, max_length=90):
    base = slugify(raw_value, allow_unicode=True)[:max_length] or 'item'
    slug = base
    counter = 2
    while model.objects.filter(slug=slug).exists():
        suffix = f'-{counter}'
        slug = f'{base[:max_length - len(suffix)]}{suffix}'
        counter += 1
    return slug


def _resolve_author(name):
    cleaned = (name or '').strip()
    if not cleaned:
        fallback_name = 'Unknown Author'
        author = Author.objects.filter(name__iexact=fallback_name).first()
        if author:
            return author

        author = Author(name=fallback_name)
        author.slug = _build_unique_slug(Author, fallback_name)
        author.save()
        return author

    author = Author.objects.filter(name__iexact=cleaned).first()
    if author:
        return author

    author = Author(name=cleaned)
    author.slug = _build_unique_slug(Author, cleaned)
    author.save()
    return author


def _ensure_default_category(category_type, label):
    existing = Category.objects.filter(category_type=category_type, is_active=True).order_by('id').first()
    if existing:
        return existing

    base_slug = f'{category_type}-general'
    slug = base_slug
    counter = 2
    while Category.objects.filter(slug=slug).exists():
        slug = f'{base_slug}-{counter}'
        counter += 1

    return Category.objects.create(
        name=f'{label} General',
        name_english=f'{label} General',
        slug=slug,
        category_type=category_type,
        description=f'Auto-created default category for {label.lower()} content.',
        is_active=True,
    )


def _create_content(request, model, template_name, redirect_url, content_type, category_label=None, success_message=None):
    if request.method == 'POST':
        title = strip_tags((request.POST.get('title') or '').strip())
        author_name = strip_tags((request.POST.get('author') or '').strip())
        content = strip_tags((request.POST.get('content') or request.POST.get('description') or '').strip())

        if not title or not author_name or not content:
            messages.error(request, f'Title, author, and {content_type} content are required.')
            return render(request, template_name)

        try:
            author = _resolve_author(author_name)
            obj = model(
                title=title,
                slug=_build_unique_slug(model, title),
                author=author,
                content=content,
                excerpt=content[:280],
                is_published=True,
                published_at=timezone.now(),
            )
            obj.save()
            if category_label:
                category = _ensure_default_category(content_type, category_label)
                if hasattr(obj, 'categories'):
                    obj.categories.add(category)
                elif hasattr(obj, 'category'):
                    obj.category = category
                    obj.save()
            messages.success(request, success_message or f'{content_type.title()} has been published successfully.')
            return redirect(redirect_url)
        except Exception as exc:
            messages.error(request, f'Unable to create {content_type}: {exc}')

    return render(request, template_name)


def _process_csv_row(content_type, row):
    """Process a single CSV row for the given content type."""
    config = CONTENT_TYPES[content_type]

    # Check required fields
    for field in config['required_fields']:
        if not row.get(field, '').strip():
            return False

    # Common processing
    author_name = row.get('author', '').strip()
    author = _resolve_author(author_name) if author_name else None

    if content_type == 'poetry':
        poem = Poetry(
            title=strip_tags(row['title']),
            slug=_build_unique_slug(Poetry, row['title']),
            author=author,
            content=strip_tags(row['content']),
            category=_ensure_default_category('poetry', 'Poetry'),
            is_published=True,
            published_at=timezone.now(),
        )
        poem.save()
        return True

    elif content_type == 'quotes':
        quote_type = row.get('quote_type', 'motivational').strip() or 'motivational'
        quote = Quote(
            text=strip_tags(row['text']),
            slug=_build_unique_slug(Quote, row['text'][:50]),
            author=author,
            quote_type=quote_type,
            is_published=True,
        )
        quote.save()
        quote.categories.add(_ensure_default_category('quote', 'Quote'))
        return True

    elif content_type == 'stories':
        content = strip_tags(row['content'])
        story = Story(
            title=strip_tags(row['title']),
            slug=_build_unique_slug(Story, row['title']),
            author=author,
            content=content,
            excerpt=content[:280],
            is_published=True,
            published_at=timezone.now(),
        )
        story.save()
        story.categories.add(_ensure_default_category('story', 'Story'))
        return True

    elif content_type == 'blog':
        content = strip_tags(row['content'])
        post = BlogPost(
            title=strip_tags(row['title']),
            slug=_build_unique_slug(BlogPost, row['title']),
            author=author,
            content=content,
            excerpt=content[:280],
            is_published=True,
            published_at=timezone.now(),
        )
        post.save()
        return True

    elif content_type == 'novels':
        novel = Novel(
            title=strip_tags(row['title']),
            slug=_build_unique_slug(Novel, row['title']),
            author=author,
            content=strip_tags(row['content']),
            category=_ensure_default_category('novel', 'Novel'),
            is_published=True,
            published_at=timezone.now(),
        )
        novel.save()
        return True

    elif content_type == 'videos':
        video = Video(
            title=strip_tags(row['title']),
            slug=_build_unique_slug(Video, row['title']),
            description=strip_tags(row.get('description', '')),
            author=author,
            category=_ensure_default_category('video', 'Video'),
            video_type=row.get('video_type', 'other').strip() or 'other',
            video_url=row['video_url'],
            is_published=True,
            published_at=timezone.now(),
        )
        video.save()
        return True

    return False


@admin_required
def dashboard_home(request):
    User = get_user_model()
    activity_window = []
    today = timezone.localdate()

    for days_back in range(6, -1, -1):
        target_date = today - timedelta(days=days_back)
        activity_window.append({
            'date': target_date,
            'count': UserActivity.objects.filter(created_at__date=target_date).count(),
        })

    stats = {
        'total_users': User.objects.count(),
        'total_authors': Author.objects.filter(is_active=True).count(),
        'total_novels': Novel.objects.count(),
        'total_stories': Story.objects.count(),
        'total_poetry': Poetry.objects.count(),
        'total_blog': BlogPost.objects.count(),
        'total_quotes': Quote.objects.count(),
        'total_videos': Video.objects.count(),
        'notifications_count': Notification.objects.count(),
        'subscribers_count': NewsletterSubscriber.objects.count(),
        'active_memberships': UserMembership.objects.filter(status='active').count(),
        'premium_plans_count': PremiumPlan.objects.filter(is_active=True).count(),
        'pending_messages': ContactMessage.objects.filter(is_read=False).count(),
        'daily_activity': activity_window,
        'trending_poetry': get_trending_poetry(limit=5),
        'trending_blogs': get_trending_blogs(limit=5),
        'trending_videos': get_trending_videos(limit=5),
        'trending_content': get_trending_content(limit=6),
        'recent_users': User.objects.order_by('-date_joined')[:6],
        'recent_authors': Author.objects.filter(is_active=True).order_by('-created_at')[:6],
        'latest_novels': Novel.objects.select_related('author').order_by('-created_at')[:5],
        'latest_stories': Story.objects.select_related('author').order_by('-created_at')[:5],
        'latest_blog_posts': BlogPost.objects.select_related('author').order_by('-created_at')[:5],
    }
    return render(request, 'dashboard/admin_dashboard_home.html', stats)


@admin_required
def novel_list(request):
    novels = Novel.objects.select_related('author').order_by('-created_at')
    return render(request, 'dashboard/novel_list.html', {'novels': novels})


@superuser_upload_required
def add_novel(request):
    if request.method == 'POST':
        title = (request.POST.get('title') or '').strip()
        author_name = (request.POST.get('author') or '').strip()
        description = (request.POST.get('description') or '').strip()

        if not title or not author_name or not description:
            messages.error(request, 'Title, author, and description are required.')
            return render(request, 'dashboard/add_novel.html')

        try:
            author = _resolve_author(author_name)
            default_category = _ensure_default_category('novel', 'Novel')
            novel = Novel(
                title=title,
                slug=_build_unique_slug(Novel, title),
                author=author,
                content=description,  # Use content field instead of description
                category=default_category,
                is_published=True,
                published_at=timezone.now(),
            )
            novel.save()
            messages.success(request, 'Novel has been published successfully.')
            return redirect('dashboard_novel_list')
        except Exception as exc:
            messages.error(request, f'Unable to create novel: {exc}')

    return render(request, 'dashboard/add_novel.html')


@admin_required
def story_list(request):
    stories = Story.objects.select_related('author').order_by('-created_at')
    return render(request, 'dashboard/story_list.html', {'stories': stories})


@superuser_upload_required
def add_story(request):
    return _create_content(request, Story, 'dashboard/add_story.html', 'dashboard_story_list', 'story', 'Story', 'Story has been published successfully.')


@admin_required
def poetry_list(request):
    poems = Poetry.objects.select_related('author').order_by('-created_at')
    return render(request, 'dashboard/poetry_list.html', {'poems': poems})


@superuser_upload_required
def add_poetry(request):
    if request.method == 'POST':
        title = (request.POST.get('title') or '').strip()
        author_name = (request.POST.get('author') or '').strip()
        content = (request.POST.get('content') or '').strip()
        if not title or not author_name or not content:
            messages.error(request, 'Title, author, and poetry content are required.')
            return render(request, 'dashboard/add_poetry.html')

        try:
            author = _resolve_author(author_name)
            default_category = _ensure_default_category('poetry', 'Poetry')
            poem = Poetry(
                title=title,
                slug=_build_unique_slug(Poetry, title),
                author=author,
                content=content,
                category=default_category,
                is_published=True,
                published_at=timezone.now(),
            )
            poem.save()
            messages.success(request, 'Poetry has been published successfully.')
            return redirect('dashboard_poetry_list')
        except Exception as exc:
            messages.error(request, f'Unable to create poetry: {exc}')

    return render(request, 'dashboard/add_poetry.html')


@admin_required
def blog_list(request):
    posts = BlogPost.objects.select_related('author').order_by('-created_at')
    return render(request, 'dashboard/blog_list.html', {'posts': posts})




@superuser_upload_required
def add_blog(request):
    return _create_content(request, BlogPost, 'dashboard/add_blog.html', 'dashboard_blog_list', 'blog', None, 'Blog post has been published successfully.')


@admin_required
def quote_list(request):
    quotes = Quote.objects.select_related('author').order_by('-created_at')
    return render(request, 'dashboard/quote_list.html', {'quotes': quotes})


@superuser_upload_required
def add_quote(request):
    if request.method == 'POST':
        quote_text = strip_tags((request.POST.get('quote') or '').strip())
        author_name = strip_tags((request.POST.get('author') or '').strip())
        quote_type = (request.POST.get('quote_type') or 'motivational').strip()
        background_image = request.FILES.get('background_image')

        if not quote_text or not author_name:
            messages.error(request, 'Quote text and author are required.')
            return render(request, 'dashboard/add_quote.html')

        try:
            author = _resolve_author(author_name)
            quote = Quote(
                text=quote_text,
                slug=_build_unique_slug(Quote, quote_text[:50]),
                author=author,
                quote_type=quote_type,
                background_image=background_image,
                is_published=True,
            )
            quote.save()
            quote.categories.add(_ensure_default_category('quote', 'Quote'))
            messages.success(request, 'Quote has been published successfully.')
            return redirect('dashboard_quote_list')
        except Exception as exc:
            messages.error(request, f'Unable to create quote: {exc}')

    return render(request, 'dashboard/add_quote.html')


@admin_required
def video_list(request):
    videos = Video.objects.select_related('author').order_by('-created_at')
    return render(request, 'dashboard/video_list.html', {'videos': videos})


@superuser_upload_required
def add_video(request):
    if request.method == 'POST':
        title = (request.POST.get('title') or '').strip()
        author_name = (request.POST.get('author') or '').strip()
        video_type = (request.POST.get('video_type') or 'poetry').strip()
        platform = (request.POST.get('platform') or 'youtube').strip()
        video_id = (request.POST.get('video_id') or '').strip()
        video_url = (request.POST.get('video_url') or '').strip()
        youtube_link = (request.POST.get('youtube_link') or '').strip()
        description = (request.POST.get('description') or '').strip()
        thumbnail = request.FILES.get('thumbnail')
        video_file = request.FILES.get('video_file')

        if not title:
            messages.error(request, 'Video title is required.')
            return render(request, 'dashboard/add_video.html')

        if not any([video_id, video_url, youtube_link, video_file]):
            messages.error(request, 'Provide a video file, YouTube link, video URL, or video ID.')
            return render(request, 'dashboard/add_video.html')

        try:
            author = _resolve_author(author_name) if author_name else None
            resolved_video_id = video_id or slugify(title, allow_unicode=True)[:100] or 'video-item'
            video = Video(
                title=title,
                slug=_build_unique_slug(Video, title),
                description=description,
                video_type=video_type,
                platform=platform,
                video_id=resolved_video_id,
                video_url=video_url,
                youtube_link=youtube_link,
                video_file=video_file,
                thumbnail=thumbnail,
                author=author,
                is_published=True,
                published_at=timezone.now(),
            )
            video.save()
            video.categories.add(_ensure_default_category('video', 'Video'))
            messages.success(request, 'Video has been published successfully.')
            return redirect('dashboard_video_list')
        except Exception as exc:
            messages.error(request, f'Unable to create video: {exc}')

    return render(request, 'dashboard/add_video.html')


@admin_required
def user_list(request):
    User = get_user_model()
    users = User.objects.order_by('-date_joined')
    return render(request, 'dashboard/user_list.html', {'users': users})


@superuser_upload_required
def bulk_upload(request):

    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        content_type = request.POST.get('content_type')

        if not csv_file or not content_type:
            messages.error(request, VALIDATION_MESSAGES['missing_fields'])
            return render(request, 'dashboard/bulk_upload.html')

        # Validate file type and size
        if not any(csv_file.name.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
            messages.error(request, VALIDATION_MESSAGES['invalid_file_type'])
            return render(request, 'dashboard/bulk_upload.html')

        if csv_file.size > MAX_FILE_SIZE:
            messages.error(request, VALIDATION_MESSAGES['file_too_large'])
            return render(request, 'dashboard/bulk_upload.html')

        if content_type not in CONTENT_TYPES:
            messages.error(request, 'Invalid content type selected.')
            return render(request, 'dashboard/bulk_upload.html')

        try:
            data = csv_file.read().decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(data))

            created_count = 0
            for row in csv_reader:
                try:
                    if _process_csv_row(content_type, row):
                        created_count += 1
                except Exception as row_exc:
                    # Log individual row errors but continue processing
                    print(f"Error processing row: {row_exc}")
                    continue

            messages.success(request, VALIDATION_MESSAGES['success'].format(created_count))
            return redirect('dashboard_home')

        except Exception as exc:
            messages.error(request, VALIDATION_MESSAGES['processing_error'].format(exc))

    return render(request, 'dashboard/bulk_upload.html')


@login_required
def user_dashboard(request):
    """User dashboard for regular users"""
    from core.models import Bookmark, Comment, ContentLike
    
    user = request.user
    
    # Get user stats
    bookmarks_count = Bookmark.objects.filter(user=user).count()
    comments_count = Comment.objects.filter(user=user).count()
    likes_count = ContentLike.objects.filter(user=user).count()
    unread_notifications = Notification.objects.filter(user=user, is_read=False).count()
    
    # Get user activities
    recent_activities = UserActivity.objects.filter(user=user).order_by('-created_at')[:10]
    
    # Get bookmarked content
    bookmarks = Bookmark.objects.filter(user=user).select_related(
        'poetry__author', 'story__author', 'novel__author', 'quote__author', 'blog__author'
    ).order_by('-created_at')[:6]
    
    context = {
        'user': user,
        'bookmarks_count': bookmarks_count,
        'comments_count': comments_count,
        'likes_count': likes_count,
        'unread_notifications': unread_notifications,
        'recent_activities': recent_activities,
        'bookmarks': bookmarks,
    }
    
    return render(request, 'dashboard/user_dashboard.html', context)

