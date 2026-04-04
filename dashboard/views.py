from django.contrib import messages
from datetime import timedelta
import csv
import io
from functools import wraps

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render
from django.utils import timezone
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
    base = slugify(raw_value)[:max_length] or 'item'
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
    return render(request, 'dashboard/dashboard_home.html', stats)


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
        cover_image = request.FILES.get('cover_image')
        pdf_file = request.FILES.get('pdf_file')

        if not title or not author_name or not description or not cover_image:
            messages.error(request, 'Please fill all required fields and upload a cover image.')
            return render(request, 'dashboard/add_novel.html')

        try:
            author = _resolve_author(author_name)
            default_category = _ensure_default_category('novel', 'Novel')
            novel = Novel(
                title=title,
                slug=_build_unique_slug(Novel, title),
                author=author,
                description=description,
                cover_image=cover_image,
                pdf_file=pdf_file,
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
    if request.method == 'POST':
        title = (request.POST.get('title') or '').strip()
        author_name = (request.POST.get('author') or '').strip()
        content = (request.POST.get('content') or request.POST.get('description') or '').strip()

        if not title or not author_name or not content:
            messages.error(request, 'Title, author, and story content are required.')
            return render(request, 'dashboard/add_story.html')

        try:
            author = _resolve_author(author_name)
            story = Story(
                title=title,
                slug=_build_unique_slug(Story, title),
                author=author,
                content=content,
                excerpt=content[:280],
                is_published=True,
                published_at=timezone.now(),
            )
            story.save()
            story.categories.add(_ensure_default_category('story', 'Story'))
            messages.success(request, 'Story has been published successfully.')
            return redirect('dashboard_story_list')
        except Exception as exc:
            messages.error(request, f'Unable to create story: {exc}')

    return render(request, 'dashboard/add_story.html')


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
        poetry_type = (request.POST.get('poetry_type') or 'ghazal').strip()
        background_image = request.FILES.get('background_image')

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
                poetry_type=poetry_type,
                background_image=background_image,
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
    if request.method == 'POST':
        title = (request.POST.get('title') or '').strip()
        author_name = (request.POST.get('author') or '').strip()
        content = (request.POST.get('content') or '').strip()
        featured_image = request.FILES.get('featured_image')

        if not title or not author_name or not content:
            messages.error(request, 'Title, author, and blog content are required.')
            return render(request, 'dashboard/add_blog.html')

        try:
            author = _resolve_author(author_name)
            post = BlogPost(
                title=title,
                slug=_build_unique_slug(BlogPost, title),
                author=author,
                content=content,
                excerpt=content[:280],
                featured_image=featured_image,
                status='published',
                is_published=True,
                published_at=timezone.now(),
            )
            post.save()
            post.categories.add(_ensure_default_category('blog', 'Blog'))
            messages.success(request, 'Blog post has been published successfully.')
            return redirect('dashboard_blog_list')
        except Exception as exc:
            messages.error(request, f'Unable to create blog post: {exc}')

    return render(request, 'dashboard/add_blog.html')


@admin_required
def quote_list(request):
    quotes = Quote.objects.select_related('author').order_by('-created_at')
    return render(request, 'dashboard/quote_list.html', {'quotes': quotes})


@superuser_upload_required
def add_quote(request):
    if request.method == 'POST':
        quote_text = (request.POST.get('quote') or '').strip()
        author_name = (request.POST.get('author') or '').strip()
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
            resolved_video_id = video_id or slugify(title)[:100] or 'video-item'
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
            messages.error(request, 'Please select a content type and upload a CSV file.')
            return render(request, 'dashboard/bulk_upload.html')

        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'File must be a CSV.')
            return render(request, 'dashboard/bulk_upload.html')

        try:
            data = csv_file.read().decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(data))

            created_count = 0
            for row in csv_reader:
                if content_type == 'poetry':
                    title = row.get('title', '').strip()
                    author_name = row.get('author', '').strip()
                    content = row.get('content', '').strip()
                    poetry_type = row.get('poetry_type', 'ghazal').strip()

                    if not title or not author_name or not content:
                        continue

                    author = _resolve_author(author_name)
                    default_category = _ensure_default_category('poetry', 'Poetry')
                    poem = Poetry(
                        title=title,
                        slug=_build_unique_slug(Poetry, title),
                        author=author,
                        content=content,
                        poetry_type=poetry_type,
                        category=default_category,
                        is_published=True,
                        published_at=timezone.now(),
                    )
                    poem.save()
                    created_count += 1

                elif content_type == 'quotes':
                    text = row.get('text', '').strip()
                    author_name = row.get('author', '').strip()
                    quote_type = row.get('quote_type', 'motivational').strip()

                    if not text or not author_name:
                        continue

                    author = _resolve_author(author_name)
                    quote = Quote(
                        text=text,
                        slug=_build_unique_slug(Quote, text[:50]),
                        author=author,
                        quote_type=quote_type,
                        is_published=True,
                    )
                    quote.save()
                    quote.categories.add(_ensure_default_category('quote', 'Quote'))
                    created_count += 1

                # Add more content types as needed

            messages.success(request, f'Successfully created {created_count} items.')
            return redirect('dashboard_home')

        except Exception as exc:
            messages.error(request, f'Error processing file: {exc}')

    return render(request, 'dashboard/bulk_upload.html')



