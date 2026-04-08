"""
Accounts views for authentication and user dashboard.
"""

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from core.models import Bookmark, Comment, ContentLike, Notification, ReadingProgress, Author
from core.services import build_seo_context, get_or_create_membership, rate_limit_request, resolve_content_object

from .forms import (
    CustomPasswordChangeForm,
    UserLoginForm,
    UserProfileForm,
    UserRegistrationForm,
)
from .models import User, UserActivity, Poetry

def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def admin_upload(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        author = request.POST.get('author')

        Poetry.objects.create(
            text=text,
            author=author
        )

        return redirect('home')

    return render(request, 'admin_upload.html')

def _resolve_user_bookmarks(user, limit=12):
    """Resolve bookmarked objects to title/url records for dashboard widgets."""
    from blog.models import BlogPost
    from novels.models import Novel
    from poetry.models import Poetry
    from quotes.models import Quote
    from stories.models import Story
    from videos.models import Video

    bookmarks = Bookmark.objects.filter(user=user).order_by("-created_at")[:limit]
    resolved = []

    for bookmark in bookmarks:
        obj = None
        title = None
        thumb = None

        if bookmark.content_type == "novel":
            obj = Novel.objects.filter(id=bookmark.object_id, is_published=True).first()
            if obj:
                title = obj.title
                thumb = obj.cover_image.url if obj.cover_image else None
        elif bookmark.content_type == "story":
            obj = Story.objects.filter(id=bookmark.object_id, is_published=True).first()
            if obj:
                title = obj.title
                thumb = obj.featured_image.url if obj.featured_image else None
        elif bookmark.content_type == "poetry":
            obj = Poetry.objects.filter(id=bookmark.object_id, is_published=True).first()
            if obj:
                title = obj.title
        elif bookmark.content_type == "blog":
            obj = BlogPost.objects.filter(id=bookmark.object_id, is_published=True).first()
            if obj:
                title = obj.title
                thumb = obj.featured_image.url if obj.featured_image else None
        elif bookmark.content_type == "quote":
            obj = Quote.objects.filter(id=bookmark.object_id, is_published=True).first()
            if obj:
                title = obj.text[:60] + "..." if len(obj.text) > 60 else obj.text
                thumb = obj.background_image.url if obj.background_image else None
        elif bookmark.content_type == "video":
            obj = Video.objects.filter(id=bookmark.object_id, is_published=True).first()
            if obj:
                title = obj.title
                thumb = obj.get_thumbnail_url()

        if obj:
            resolved.append(
                {
                    "id": bookmark.id,
                    "content_type": bookmark.content_type,
                    "object_id": bookmark.object_id,
                    "title": title or str(obj),
                    "url": obj.get_absolute_url(),
                    "thumb": thumb,
                    "created_at": bookmark.created_at,
                }
            )

    return resolved


def _resolve_user_likes(user, limit=12):
    """Resolve liked objects for dashboard/profile widgets."""
    likes = ContentLike.objects.filter(user=user).order_by("-created_at")[:limit]
    resolved = []

    for like in likes:
        obj = resolve_content_object(like.content_type, like.object_id, published_only=True)
        if not obj:
            continue

        resolved.append(
            {
                "id": like.id,
                "content_type": like.content_type,
                "title": getattr(obj, "title", getattr(obj, "text", str(obj)))[:90],
                "url": obj.get_absolute_url() if hasattr(obj, "get_absolute_url") else "#",
                "created_at": like.created_at,
            }
        )

    return resolved


def register(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        limited, retry_after = rate_limit_request(request, "register", limit=4, window=300)
        if limited:
            messages.error(request, f"Please wait {retry_after} seconds before creating another account.")
            return redirect("register")

        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your account has been created.")
            return redirect("home")
    else:
        form = UserRegistrationForm()

    return render(
        request,
        "accounts/register.html",
        {
            "form": form,
            **build_seo_context(
                request,
                title=f"Register | {settings.SITE_NAME}",
                description=f"Create your {settings.SITE_NAME} account to bookmark, comment, and track reading history.",
                keywords=settings.SITE_KEYWORDS,
                og_type="website",
            ),
        },
    )


def user_login(request):
    """User login view."""
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        limited, retry_after = rate_limit_request(request, "login", limit=5, window=300)
        if limited:
            messages.error(request, f"Too many login attempts. Please wait {retry_after} seconds.")
            return redirect("login")

        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    # Handle remember me
                    if request.POST.get('remember') == 'on':
                        # Set session to expire in 30 days
                        request.session.set_expiry(60 * 60 * 24 * 30)
                    else:
                        # Set session to expire on browser close
                        request.session.set_expiry(0)

                    next_url = request.GET.get("next")
                    if user.is_staff or user.is_superuser:
                        return redirect(next_url or "admin:index")
                    else:
                        return redirect(next_url or "dashboard")
                else:
                    messages.error(request, "Your account is inactive. Please contact support.")
            else:
                # Check if user exists but password is wrong vs user doesn't exist
                from django.contrib.auth.models import User
                if User.objects.filter(username=username).exists() or User.objects.filter(email=username).exists():
                    messages.error(request, "Invalid password. Please try again.")
                else:
                    messages.error(request, "Account does not exist with this username or email.")
        else:
            # Form validation errors are handled by the template
            pass
    else:
        form = UserLoginForm()

    return render(
        request,
        "accounts/login.html",
        {
            "form": form,
            **build_seo_context(
                request,
                title=f"Login | {settings.SITE_NAME}",
                description=f"Sign in to access your {settings.SITE_NAME} dashboard.",
                keywords=settings.SITE_KEYWORDS,
                og_type="website",
                robots="noindex, nofollow",
            ),
        },
    )


@login_required
def user_logout(request):
    """User logout view."""
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("home")


@login_required
def dashboard(request):
    """Unified user dashboard with profile, bookmarks, comments, and reading history."""
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("dashboard")
        messages.error(request, "Please correct the highlighted profile fields.")
    else:
        form = UserProfileForm(instance=request.user)

    membership = get_or_create_membership(request.user)

    context = {
        "profile_form": form,
        "bookmarks": _resolve_user_bookmarks(request.user, limit=12),
        "liked_items": _resolve_user_likes(request.user, limit=10),
        "comments": Comment.objects.filter(user=request.user).order_by("-created_at")[:15],
        "reading_history": ReadingProgress.objects.filter(user=request.user)
        .select_related("novel", "chapter")
        .order_by("-last_read_at")[:15],
        "recent_views": UserActivity.objects.filter(
            user=request.user, activity_type="view"
        ).order_by("-created_at")[:15],
        "notifications": Notification.objects.filter(user=request.user).select_related("actor").order_by("-created_at")[:8],
        "likes_count": request.user.get_likes_count(),
        "bookmarks_count": request.user.get_bookmarks_count(),
        "comments_count": request.user.get_comments_count(),
        "membership": membership,
        "has_premium_access": membership.is_active_membership,
        **build_seo_context(
            request,
            title=f"Dashboard | {settings.SITE_NAME}",
            description="User dashboard with profile, bookmarks, comments, and reading history.",
            keywords=settings.SITE_KEYWORDS,
            og_type="profile",
            robots="noindex, nofollow",
        ),
    }
    return render(request, "accounts/dashboard.html", context)


@login_required
def my_content(request):
    """User's own content listing - poetry, blogs, stories, novels, quotes, and videos."""
    from blog.models import BlogPost
    from novels.models import Novel
    from poetry.models import Poetry
    from quotes.models import Quote
    from stories.models import Story
    from videos.models import Video
    
    # Ensure the author is filtered by the correct field
    author_name = request.user.display_name or request.user.username
    poetry = Poetry.objects.filter(author__name=author_name).order_by("-created_at")
    blogs = BlogPost.objects.filter(author__name=author_name).order_by("-created_at")
    stories = Story.objects.filter(author__name=author_name).order_by("-created_at")
    novels = Novel.objects.filter(author__name=author_name).order_by("-created_at")
    quotes = Quote.objects.filter(author__name=author_name).order_by("-created_at")
    videos = Video.objects.filter(author__name=author_name).order_by("-created_at")
    
    membership = get_or_create_membership(request.user)
    
    context = {
        "poetry": poetry,
        "blogs": blogs,
        "stories": stories,
        "novels": novels,
        "quotes": quotes,
        "videos": videos,
        "total_poetry": poetry.count(),
        "total_blogs": blogs.count(),
        "total_stories": stories.count(),
        "total_novels": novels.count(),
        "total_quotes": quotes.count(),
        "total_videos": videos.count(),
        "membership": membership,
        "has_premium_access": membership.is_active_membership,
        **build_seo_context(
            request,
            title=f"میرا مواد | {settings.SITE_NAME}",
            description="اپنی تصنیف کردہ شاعری، ناولز، کہانیاں، بلاگز، اقتباسات اور ویڈیوز دیکھیں",
            keywords=settings.SITE_KEYWORDS,
            og_type="profile",
            robots="noindex, nofollow",
        ),
    }
    return render(request, "accounts/my_content.html", context)


@login_required
def profile(request):
    """Backwards-compatible profile endpoint."""
    return redirect("dashboard")


@login_required
def edit_profile(request):
    """Backwards-compatible edit endpoint."""
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
        else:
            messages.error(request, "Please correct the highlighted profile fields.")
    return redirect("dashboard")


@login_required
def change_password(request):
    """Change password view."""
    if request.method == "POST":
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password has been changed.")
            return redirect("dashboard")
    else:
        form = CustomPasswordChangeForm(request.user)

    return render(
        request,
        "accounts/change_password.html",
        {
            "form": form,
            **build_seo_context(
                request,
                title=f"Change Password | {settings.SITE_NAME}",
                description="Update your account password securely.",
                keywords=settings.SITE_KEYWORDS,
                og_type="website",
                robots="noindex, nofollow",
            ),
        },
    )


def public_profile(request, username):
    """Public profile view."""
    user = get_object_or_404(User, username=username, is_active=True)

    from novels.models import Novel
    from poetry.models import Poetry
    from stories.models import Story

    context = {
        "profile_user": user,
        "novels": Novel.objects.filter(author__name=user.display_name, is_published=True)[:6]
        if user.is_author
        else [],
        "stories": Story.objects.filter(author__name=user.display_name, is_published=True)[:6]
        if user.is_author
        else [],
        "poetry": Poetry.objects.filter(author__name=user.display_name, is_published=True)[:6]
        if user.is_author
        else [],
        "liked_items": _resolve_user_likes(user, limit=6),
        "likes_count": user.get_likes_count(),
        **build_seo_context(
            request,
            title=f"{user.get_full_name()} | {settings.SITE_NAME}",
            description=f"Public profile on {settings.SITE_NAME}.",
            keywords=settings.SITE_KEYWORDS,
            og_type="profile",
        ),
    }
    return render(request, "accounts/public_profile.html", context)


@login_required
def bookmarks(request):
    """Backwards-compatible bookmarks endpoint."""
    return redirect("bookmarks_dashboard")


@login_required
def delete_account(request):
    """Delete user account."""
    if request.method == "POST":
        request.user.delete()
        messages.success(request, "Your account has been deleted.")
        return redirect("home")

    return render(
        request,
        "accounts/delete_account.html",
        {
            **build_seo_context(
                request,
                title=f"Delete Account | {settings.SITE_NAME}",
                description="Delete your account permanently.",
                keywords=settings.SITE_KEYWORDS,
                og_type="website",
                robots="noindex, nofollow",
            ),
        },
    )
