"""
Shared services for SEO, ranking, engagement, premium access, search,
notifications, and AI-assisted content helpers.
"""

from datetime import timedelta
import re

from django.core.cache import cache
from django.db.models import Count, F, Q
from django.utils.html import strip_tags
from django.utils import timezone
from django.utils.text import slugify

from accounts.models import User, UserActivity
from blog.models import BlogPost
from novels.models import Novel
from poetry.models import Poetry
from quotes.models import Quote
from stories.models import Story
from videos.models import Video

from .models import (
    Author,
    Comment,
    ContentLike,
    Notification,
    PremiumPlan,
    UserMembership,
)


POPULAR_CACHE_TIMEOUT = 60 * 5
TRENDING_CACHE_TIMEOUT = 60 * 5
SUGGESTIONS_CACHE_TIMEOUT = 60 * 3
RECOMMENDATION_STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "for",
    "from",
    "into",
    "its",
    "that",
    "the",
    "this",
    "with",
    "میں",
    "اور",
    "کی",
    "کے",
    "کو",
    "سے",
    "پر",
    "ہے",
    "ہیں",
    "یہ",
    "وہ",
    "شاعری",
    "ناول",
    "ویڈیو",
    "بلاگ",
}

CONTENT_MODEL_REGISTRY = {
    "novel": Novel,
    "story": Story,
    "poetry": Poetry,
    "quote": Quote,
    "blog": BlogPost,
    "video": Video,
}

CONTENT_ICON_REGISTRY = {
    "novel": "bi-book-half",
    "story": "bi-journal-text",
    "poetry": "bi-feather",
    "quote": "bi-chat-quote",
    "blog": "bi-newspaper",
    "video": "bi-play-circle",
}


def build_seo_context(
    request,
    *,
    title,
    description,
    keywords="",
    og_type="website",
    og_image=None,
    canonical_url=None,
    robots="index, follow",
):
    """Build SEO metadata dict consumable by the base template."""
    canonical = canonical_url or request.build_absolute_uri()
    image = og_image
    if image and not str(image).startswith(("http://", "https://")):
        image = request.build_absolute_uri(image)

    return {
        "meta_title": title,
        "meta_description": description,
        "meta_keywords": keywords,
        "og_title": title,
        "og_description": description,
        "og_type": og_type,
        "og_image": image,
        "canonical_url": canonical,
        "robots_content": robots,
    }


def _resolve_actor_name(user):
    return user.get_full_name() or user.username


def get_client_identity(request):
    if request.user.is_authenticated:
        return f"user:{request.user.pk}"
    return f"ip:{request.META.get('REMOTE_ADDR', 'anonymous')}"


def rate_limit_request(request, scope, *, limit=8, window=60):
    """
    Lightweight cache-backed rate limiter.
    Returns (is_limited, retry_after_seconds).
    """
    cache_key = f"rate:{scope}:{get_client_identity(request)}"
    now = timezone.now().timestamp()
    history = cache.get(cache_key, [])
    history = [stamp for stamp in history if now - stamp < window]

    if len(history) >= limit:
        retry_after = max(int(window - (now - history[0])), 1)
        cache.set(cache_key, history, timeout=window)
        return True, retry_after

    history.append(now)
    cache.set(cache_key, history, timeout=window)
    return False, 0


def resolve_content_model(content_type):
    return CONTENT_MODEL_REGISTRY.get((content_type or "").lower())


def infer_content_type(obj):
    for content_type, model in CONTENT_MODEL_REGISTRY.items():
        if isinstance(obj, model):
            return content_type
    return ""


def resolve_content_object(content_type, object_id, *, published_only=True):
    model = resolve_content_model(content_type)
    if model is None:
        return None

    queryset = model.objects.all()
    if published_only and hasattr(model, "is_published"):
        queryset = queryset.filter(is_published=True)
    return queryset.filter(pk=object_id).first()


def resolve_content_title(obj):
    title = getattr(obj, "title", "")
    if title:
        return title
    text = getattr(obj, "text", "")
    if text:
        return text[:80] + ("..." if len(text) > 80 else "")
    return str(obj)


def resolve_author_user(author):
    """Best-effort mapping from content author profile to local platform user."""
    if not author:
        return None

    name = (getattr(author, "name", "") or "").strip()
    if not name:
        return None

    slug_name = slugify(name).replace("-", "")
    parts = [part for part in name.split() if part]

    filters = Q(display_name__iexact=name) | Q(username__iexact=slug_name)
    if len(parts) >= 2:
        filters |= Q(first_name__iexact=parts[0], last_name__iexact=" ".join(parts[1:]))

    return User.objects.filter(filters, is_active=True).first()


def create_notification(
    user,
    *,
    notification_type,
    title,
    message,
    actor=None,
    link="",
    content_type="",
    object_id=None,
):
    if not user:
        return None
    if actor and actor == user and notification_type != "system":
        return None

    return Notification.objects.create(
        user=user,
        actor=actor,
        notification_type=notification_type,
        title=title,
        message=message,
        link=link,
        content_type=content_type or "",
        object_id=object_id,
    )


def get_latest_notifications(user, limit=6):
    if not user or not user.is_authenticated:
        return []
    return list(
        Notification.objects.filter(user=user)
        .select_related("actor")
        .order_by("-created_at")[:limit]
    )


def mark_notifications_read(user):
    if not user or not user.is_authenticated:
        return 0
    return Notification.objects.filter(user=user, is_read=False).update(is_read=True)




def toggle_content_like(user, content_type, object_id):
    if not user or not user.is_authenticated:
        return {"success": False, "message": "Login required.", "liked": False}

    obj = resolve_content_object(content_type, object_id, published_only=True)
    if obj is None:
        return {"success": False, "message": "Content not found.", "liked": False}

    like, created = ContentLike.objects.get_or_create(
        user=user,
        content_type=content_type,
        object_id=object_id,
    )

    delta = 1 if created else -1
    if not created:
        like.delete()

    if hasattr(obj, "likes_count"):
        obj.__class__.objects.filter(pk=obj.pk).update(likes_count=F("likes_count") + delta)
        obj.refresh_from_db(fields=["likes_count"])

    owner = resolve_author_user(getattr(obj, "author", None))
    if created and owner and owner != user:
        create_notification(
            owner,
            notification_type="like",
            title="New appreciation",
            message=f"{_resolve_actor_name(user)} liked “{resolve_content_title(obj)}”.",
            actor=user,
            link=obj.get_absolute_url() if hasattr(obj, "get_absolute_url") else "",
            content_type=content_type,
            object_id=obj.pk,
        )

    return {
        "success": True,
        "liked": created,
        "likes_count": getattr(obj, "likes_count", 0),
        "message": "Liked successfully." if created else "Like removed.",
    }


def track_content_share(obj):
    if not hasattr(obj, "shares_count"):
        return 0
    obj.__class__.objects.filter(pk=obj.pk).update(shares_count=F("shares_count") + 1)
    obj.refresh_from_db(fields=["shares_count"])
    return obj.shares_count


def get_or_create_membership(user):
    membership, _ = UserMembership.objects.get_or_create(
        user=user,
        defaults={"status": "free"},
    )
    if membership.status == "active" and membership.ends_at and membership.ends_at <= timezone.now():
        membership.status = "expired"
        membership.save(update_fields=["status", "updated_at"])
    return membership


def get_membership_plans(limit=None):
    queryset = PremiumPlan.objects.filter(is_active=True).order_by("price", "billing_cycle_days")
    return list(queryset[:limit] if limit else queryset)


def activate_membership(user, plan):
    membership = get_or_create_membership(user)
    starts_at = timezone.now()
    ends_at = starts_at + timedelta(days=plan.billing_cycle_days)

    membership.plan = plan
    membership.status = "active"
    membership.starts_at = starts_at
    membership.ends_at = ends_at
    membership.auto_renew = True
    membership.save()

    create_notification(
        user,
        notification_type="membership",
        title="Premium activated",
        message=f"Your {plan.name} membership is active until {ends_at:%d %b %Y}.",
        link="/membership/",
    )
    return membership


def user_has_premium_access(user):
    if not user or not user.is_authenticated:
        return False
    membership = get_or_create_membership(user)
    return membership.is_active_membership


def content_requires_premium(obj):
    if getattr(obj, "is_premium", False):
        return True
    parent_novel = getattr(obj, "novel", None)
    return bool(parent_novel and getattr(parent_novel, "is_premium", False))


def user_can_access_content(user, obj):
    if not content_requires_premium(obj):
        return True
    return user_has_premium_access(user)


def track_content_view(request, obj, content_type, title, *, unique_per_session=False):
    """
    Increment object views and log user activity when authenticated.
    """
    session_key = f"viewed_{content_type}_{obj.pk}"
    should_increment = True

    if unique_per_session:
        should_increment = not request.session.get(session_key)
        if should_increment:
            request.session[session_key] = True
            request.session.modified = True

    if should_increment:
        obj.__class__.objects.filter(pk=obj.pk).update(views_count=F("views_count") + 1)
        obj.views_count += 1

    if request.user.is_authenticated:
        UserActivity.objects.create(
            user=request.user,
            activity_type="view",
            description=f"{content_type.title()}: {title[:180]}",
        )


def _get_comment_count_map(content_type, object_ids):
    if not object_ids:
        return {}

    rows = (
        Comment.objects.filter(content_type=content_type, object_id__in=object_ids, is_approved=True)
        .values("object_id")
        .annotate(total=Count("id"))
    )
    return {row["object_id"]: row["total"] for row in rows}


def _rank_content(items, *, content_type, recent_days=30):
    now = timezone.now()
    comment_map = _get_comment_count_map(content_type, [item.pk for item in items])
    ranked = []

    for item in items:
        activity_time = getattr(item, "updated_at", None) or getattr(item, "created_at", None) or now
        age_hours = max((now - activity_time).total_seconds() / 3600, 1.0)
        recent_window_hours = max(recent_days * 24, 1)
        freshness = max(recent_window_hours - age_hours, 0) / recent_window_hours
        comments_count = comment_map.get(item.pk, 0)

        score = (
            (float(getattr(item, "views_count", 0)) * 0.60)
            + (float(getattr(item, "likes_count", 0)) * 0.18)
            + (float(getattr(item, "shares_count", 0)) * 0.12)
            + (float(comments_count) * 0.10)
        )
        score *= 1.0 + (freshness * 0.35)

        item.comments_count = comments_count
        item.trending_score = round(score, 2)
        ranked.append(item)

    return ranked


def get_popular_content(limit=6):
    """Return most-engaged content buckets used for homepage and widgets."""
    cache_key = f"popular_content_v2_{limit}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    data = {
        "popular_novels": list(
            Novel.objects.filter(is_published=True).order_by("-views_count", "-likes_count", "-updated_at")[:limit]
        ),
        "popular_stories": list(
            Story.objects.filter(is_published=True).order_by("-views_count", "-likes_count", "-updated_at")[:limit]
        ),
        "popular_poetry": list(
            Poetry.objects.filter(is_published=True).order_by("-views_count", "-likes_count", "-updated_at")[:limit]
        ),
        "popular_blog_posts": list(
            BlogPost.objects.filter(is_published=True).order_by("-views_count", "-likes_count", "-updated_at")[:limit]
        ),
        "popular_videos": list(
            Video.objects.filter(is_published=True).order_by("-views_count", "-likes_count", "-updated_at")[:limit]
        ),
    }
    cache.set(cache_key, data, POPULAR_CACHE_TIMEOUT)
    return data


def _get_trending_items(queryset, *, content_type, limit=6, recent_days=21, cache_key=""):
    if cache_key:
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

    ranked = _rank_content(list(queryset), content_type=content_type, recent_days=recent_days)
    trending = sorted(ranked, key=lambda item: item.trending_score, reverse=True)[:limit]
    if cache_key:
        cache.set(cache_key, trending, TRENDING_CACHE_TIMEOUT)
    return trending


def get_trending_poetry(limit=6, recent_days=14):
    """Return poetry ranked by views, likes, comments, shares, and freshness."""
    cache_key = f"trending_poetry_v2_{limit}_{recent_days}"
    return _get_trending_items(
        Poetry.objects.filter(is_published=True)
        .select_related("author")
        .order_by("-updated_at")[:200],
        content_type="poetry",
        limit=limit,
        recent_days=recent_days,
        cache_key=cache_key,
    )


def get_trending_blogs(limit=6, recent_days=21):
    cache_key = f"trending_blog_v1_{limit}_{recent_days}"
    return _get_trending_items(
        BlogPost.objects.filter(is_published=True)
        .select_related("author")
        .order_by("-updated_at")[:200],
        content_type="blog",
        limit=limit,
        recent_days=recent_days,
        cache_key=cache_key,
    )


def get_trending_videos(limit=6, recent_days=21):
    cache_key = f"trending_video_v1_{limit}_{recent_days}"
    return _get_trending_items(
        Video.objects.filter(is_published=True)
        .select_related("author")
        .order_by("-updated_at")[:200],
        content_type="video",
        limit=limit,
        recent_days=recent_days,
        cache_key=cache_key,
    )


def get_trending_quotes(limit=6, recent_days=21):
    cache_key = f"trending_quote_v1_{limit}_{recent_days}"
    return _get_trending_items(
        Quote.objects.filter(is_published=True)
        .select_related("author")
        .order_by("-updated_at")[:200],
        content_type="quote",
        limit=limit,
        recent_days=recent_days,
        cache_key=cache_key,
    )


def get_trending_stories(limit=6, recent_days=21):
    cache_key = f"trending_story_v1_{limit}_{recent_days}"
    return _get_trending_items(
        Story.objects.filter(is_published=True)
        .select_related("author")
        .order_by("-updated_at")[:200],
        content_type="story",
        limit=limit,
        recent_days=recent_days,
        cache_key=cache_key,
    )


def get_trending_novels(limit=6, recent_days=28):
    cache_key = f"trending_novel_v1_{limit}_{recent_days}"
    return _get_trending_items(
        Novel.objects.filter(is_published=True)
        .select_related("author")
        .order_by("-updated_at")[:200],
        content_type="novel",
        limit=limit,
        recent_days=recent_days,
        cache_key=cache_key,
    )


def get_trending_content(limit=8, recent_days=21):
    """Return mixed trending content objects across the platform."""
    cache_key = f"trending_content_v1_{limit}_{recent_days}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    candidates = []
    sources = (
        ("poetry", get_trending_poetry(limit=limit, recent_days=recent_days)),
        ("blog", get_trending_blogs(limit=limit, recent_days=recent_days)),
        ("video", get_trending_videos(limit=limit, recent_days=recent_days)),
        ("story", get_trending_stories(limit=limit, recent_days=recent_days)),
        ("quote", get_trending_quotes(limit=limit, recent_days=recent_days)),
        ("novel", get_trending_novels(limit=limit, recent_days=max(recent_days, 28))),
    )

    for content_type, items in sources:
        for item in items:
            item.content_kind = content_type
            candidates.append(item)

    trending = sorted(
        candidates,
        key=lambda item: (
            getattr(item, "trending_score", 0),
            getattr(item, "views_count", 0),
            getattr(item, "likes_count", 0),
            getattr(item, "shares_count", 0),
        ),
        reverse=True,
    )[:limit]
    cache.set(cache_key, trending, TRENDING_CACHE_TIMEOUT)
    return trending


def get_top_authors(limit=6):
    """Return active authors ordered by output and readership."""
    cache_key = f"top_authors_v1_{limit}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    authors = list(
        Author.objects.filter(is_active=True)
        .annotate(
            poetry_count=Count("poetry", distinct=True),
            novel_count=Count("novels", distinct=True),
            quote_count=Count("quotes", distinct=True),
            blog_count=Count("blog_posts", distinct=True),
            video_count=Count("videos", distinct=True),
            story_count=Count("stories", distinct=True),
        )
        .order_by("-is_featured", "-views_count", "name")[: max(limit * 3, 12)]
    )

    for author in authors:
        author.total_content = (
            author.poetry_count
            + author.novel_count
            + author.quote_count
            + author.blog_count
            + author.video_count
            + author.story_count
        )

    ranked = sorted(
        authors,
        key=lambda item: (
            item.is_featured,
            getattr(item, "total_content", 0),
            getattr(item, "views_count", 0),
            item.name.lower(),
        ),
        reverse=True,
    )[:limit]
    cache.set(cache_key, ranked, TRENDING_CACHE_TIMEOUT)
    return ranked


def get_trending_sidebar_posts(limit=8, recent_days=30):
    """Build mixed trending feed for shared widgets."""
    cache_key = f"trending_sidebar_v2_{limit}_{recent_days}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    trending = get_trending_content(limit=limit, recent_days=recent_days)
    payload = [
        {
            "title": resolve_content_title(item),
            "url": item.get_absolute_url(),
            "views_count": getattr(item, "views_count", 0),
            "likes_count": getattr(item, "likes_count", 0),
            "shares_count": getattr(item, "shares_count", 0),
            "comments_count": getattr(item, "comments_count", 0),
            "content_type": infer_content_type(item).title(),
            "icon": CONTENT_ICON_REGISTRY.get(infer_content_type(item), "bi-stars"),
            "score": getattr(item, "trending_score", 0),
        }
        for item in trending
    ]
    cache.set(cache_key, payload, TRENDING_CACHE_TIMEOUT)
    return payload


def get_search_suggestions(query, limit=8):
    """Autocomplete suggestions across authors, poetry, novels, blogs, and videos."""
    normalized = (query or "").strip()
    if len(normalized) < 2:
        return []

    cache_key = f"search_suggestions_v1_{slugify(normalized)}_{limit}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        from ai_features.services import get_ai_search_suggestions

        ai_payload = get_ai_search_suggestions(normalized, limit=limit)
        if ai_payload:
            cache.set(cache_key, ai_payload, SUGGESTIONS_CACHE_TIMEOUT)
            return ai_payload
    except Exception:
        pass

    suggestions = []

    for author in Author.objects.filter(
        Q(name__icontains=normalized),
        is_active=True,
    )[:2]:
        suggestions.append(
            {
                "label": author.name,
                "type": "Author",
                "subtitle": "Writer profile",
                "url": author.get_absolute_url(),
            }
        )

    for poem in Poetry.objects.filter(
        Q(title__icontains=normalized) | Q(author__name__icontains=normalized),
        is_published=True,
    ).select_related("author")[:2]:
        suggestions.append(
            {
                "label": poem.title,
                "type": "Poetry",
                "subtitle": poem.author.name,
                "url": poem.get_absolute_url(),
            }
        )

    for novel in Novel.objects.filter(
        Q(title__icontains=normalized) | Q(author__name__icontains=normalized),
        is_published=True,
    ).select_related("author")[:2]:
        suggestions.append(
            {
                "label": novel.title,
                "type": "Novel",
                "subtitle": novel.author.name,
                "url": novel.get_absolute_url(),
            }
        )

    for post in BlogPost.objects.filter(
        Q(title__icontains=normalized) | Q(author__name__icontains=normalized),
        is_published=True,
    ).select_related("author")[:2]:
        suggestions.append(
            {
                "label": post.title,
                "type": "Blog",
                "subtitle": post.author.name,
                "url": post.get_absolute_url(),
            }
        )

    for quote in Quote.objects.filter(
        Q(text__icontains=normalized) | Q(author__name__icontains=normalized),
        is_published=True,
    ).select_related("author")[:2]:
        suggestions.append(
            {
                "label": resolve_content_title(quote),
                "type": "Quote",
                "subtitle": quote.author.name,
                "url": quote.get_absolute_url(),
            }
        )

    for video in Video.objects.filter(
        Q(title__icontains=normalized) | Q(description__icontains=normalized),
        is_published=True,
    )[:2]:
        suggestions.append(
            {
                "label": video.title,
                "type": "Video",
                "subtitle": "Watch now",
                "url": video.get_absolute_url(),
            }
        )

    payload = suggestions[:limit]
    cache.set(cache_key, payload, SUGGESTIONS_CACHE_TIMEOUT)
    return payload


def _tokenize_recommendation_text(*parts, limit=14):
    blob = " ".join(strip_tags(str(part or "")) for part in parts if part)
    tokens = re.findall(r"[A-Za-z\u0600-\u06FF]{2,}", blob.lower())
    unique = []
    seen = set()
    for token in tokens:
        if token in RECOMMENDATION_STOP_WORDS or token.isdigit():
            continue
        if token in seen:
            continue
        seen.add(token)
        unique.append(token)
        if len(unique) >= limit:
            break
    return set(unique)


def _resolve_recommendation_snippet(item):
    if isinstance(item, Poetry):
        return getattr(item, "plain_text_content", "")
    if isinstance(item, Novel):
        return getattr(item, "description_text", "")
    if isinstance(item, BlogPost):
        return getattr(item, "excerpt", "") or strip_tags(getattr(item, "content", ""))
    if isinstance(item, Story):
        return getattr(item, "excerpt", "") or strip_tags(getattr(item, "content", ""))
    if isinstance(item, Video):
        return getattr(item, "description", "")
    return ""


def _has_model_field(model, field_name):
    try:
        model._meta.get_field(field_name)
        return True
    except Exception:
        return False


def _iter_item_categories(item):
    category = getattr(item, "category", None)
    if category is not None:
        yield category

    category_manager = getattr(item, "categories", None)
    if category_manager is None:
        return

    try:
        for linked_category in category_manager.all():
            if linked_category is not None:
                yield linked_category
    except Exception:
        return


def _apply_category_related_loading(queryset):
    model = queryset.model
    if _has_model_field(model, "category"):
        queryset = queryset.select_related("category")
    if _has_model_field(model, "categories"):
        queryset = queryset.prefetch_related("categories")
    return queryset


def _build_category_filter(model, category_ids):
    if _has_model_field(model, "categories"):
        return Q(categories__in=category_ids)
    if _has_model_field(model, "category"):
        return Q(category_id__in=category_ids)
    return None


def _count_shared_categories(item, category_ids):
    if not category_ids:
        return 0

    shared_ids = set()
    category = getattr(item, "category", None)
    category_id = getattr(category, "id", None)
    if category_id in category_ids:
        shared_ids.add(category_id)

    category_manager = getattr(item, "categories", None)
    if category_manager is not None:
        try:
            shared_ids.update(set(category_manager.values_list("id", flat=True)) & category_ids)
        except Exception:
            pass

    return len(shared_ids)


def _collect_recommendation_keywords(item):
    category_parts = []
    for category in _iter_item_categories(item):
        if category.name:
            category_parts.append(category.name)
        if category.name_english:
            category_parts.append(category.name_english)

    return _tokenize_recommendation_text(
        getattr(item, "title", ""),
        _resolve_recommendation_snippet(item),
        getattr(item, "tags", ""),
        " ".join(category_parts),
        getattr(getattr(item, "author", None), "name", ""),
        limit=18,
    )


def get_cross_content_suggestions(
    *,
    author=None,
    categories=None,
    exclude_type="",
    exclude_id=None,
    limit=4,
    seed_text="",
):
    """Return mixed related suggestions ranked by author, category, and keyword overlap."""
    category_ids = {cat.id for cat in (categories or [])}
    source_keywords = _tokenize_recommendation_text(
        getattr(author, "name", ""),
        " ".join(cat.name for cat in (categories or [])),
        seed_text,
        limit=18,
    )

    candidates = []
    sources = (
        ("poetry", _apply_category_related_loading(Poetry.objects.filter(is_published=True).select_related("author"))),
        ("quote", _apply_category_related_loading(Quote.objects.filter(is_published=True).select_related("author"))),
        ("blog", _apply_category_related_loading(BlogPost.objects.filter(is_published=True).select_related("author"))),
        ("story", _apply_category_related_loading(Story.objects.filter(is_published=True).select_related("author"))),
        ("video", _apply_category_related_loading(Video.objects.filter(is_published=True).select_related("author"))),
        ("novel", _apply_category_related_loading(Novel.objects.filter(is_published=True).select_related("author"))),
    )

    for content_type, queryset in sources:
        if content_type == exclude_type:
            queryset = queryset.exclude(pk=exclude_id)

        if category_ids:
            category_filter = _build_category_filter(queryset.model, category_ids)
            if category_filter is not None:
                filters = category_filter
                if author:
                    filters |= Q(author=author)
                queryset = queryset.filter(filters)
                if _has_model_field(queryset.model, "categories"):
                    queryset = queryset.distinct()
            elif author:
                queryset = queryset.filter(author=author)
        elif author:
            queryset = queryset.filter(author=author)

        shortlist = list(queryset[:18])
        if not shortlist:
            fallback_queryset = queryset.model.objects.filter(is_published=True)
            if content_type == exclude_type:
                fallback_queryset = fallback_queryset.exclude(pk=exclude_id)
            fallback_queryset = _apply_category_related_loading(
                fallback_queryset.select_related("author")
            ).order_by("-views_count", "-updated_at")
            shortlist = list(fallback_queryset[:18])

        for item in shortlist:
            item_keywords = _collect_recommendation_keywords(item)
            keyword_matches = len(item_keywords & source_keywords)
            shared_categories = _count_shared_categories(item, category_ids)

            same_author = bool(author and getattr(item, "author_id", None) == getattr(author, "id", None))
            score = (shared_categories * 6) + (keyword_matches * 3) + (10 if same_author else 0)
            score += min(int(getattr(item, "views_count", 0) / 40), 4)
            if score <= 0:
                continue

            reasons = []
            if same_author:
                reasons.append("same author")
            if shared_categories:
                reasons.append("same category")
            if keyword_matches:
                reasons.append("matching theme")

            item.recommendation_score = score
            item.recommendation_reason = " • ".join(reasons[:2]) if reasons else "popular read"
            item.content_type_name = infer_content_type(item).title()
            candidates.append(item)

    deduped = []
    seen = set()
    for item in sorted(
        candidates,
        key=lambda entry: (
            getattr(entry, "recommendation_score", 0),
            getattr(entry, "views_count", 0),
            getattr(entry, "updated_at", None),
        ),
        reverse=True,
    ):
        key = (infer_content_type(item), item.pk)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
        if len(deduped) >= limit:
            break
    return deduped


def generate_poetry_from_prompt(topic, *, mood="romantic", poetry_type="ghazal", line_count=6):
    """
    Local AI-style poetry generator.
    Produces even-numbered sher lines so the existing formatter can render them.
    """
    cleaned_topic = (topic or "محبت").strip()[:80]
    cleaned_mood = (mood or "romantic").strip().lower()
    cleaned_type = (poetry_type or "ghazal").strip().lower()

    requested_lines = max(4, min(int(line_count or 6), 12))
    if requested_lines % 2:
        requested_lines += 1

    mood_bank = {
        "love": ["دل", "چاندنی", "وصل", "خوشبو", "محبت"],
        "romantic": ["دل", "نگاہ", "خواب", "چاندنی", "قربت"],
        "sad": ["تنہائی", "یاد", "خاموشی", "اشک", "درد"],
        "inspirational": ["حوصلہ", "منزل", "روشنی", "پرواز", "امید"],
        "religious": ["دعا", "سجدہ", "نور", "ایمان", "رحمت"],
        "philosophical": ["سوال", "آئینہ", "وقت", "سفر", "معنی"],
    }
    poetic_word_bank = mood_bank.get(cleaned_mood, mood_bank["romantic"])

    openings = [
        f"{cleaned_topic} کی صدا سے دل کا نگر روشن رہا",
        f"{cleaned_topic} کے ذکر نے خاموش راتوں کو رنگیں کیا",
        f"{cleaned_topic} کی ہوا آئی تو منظر بدلتا چلا گیا",
        f"{cleaned_topic} کا چراغ دل کے دریچوں میں جلتا رہا",
        f"{cleaned_topic} کے ساتھ ایک نیا خواب بھی بیدار ہوا",
        f"{cleaned_topic} کی بات نے روح کو نرم روشنی دی",
    ]
    closings = [
        f"{poetic_word_bank[0]} کے موسم میں ہر اک لفظ سنور جاتا ہے",
        f"{poetic_word_bank[1]} کے لمس سے پتھر بھی پگھل جاتے ہیں",
        f"{poetic_word_bank[2]} کی دہلیز پہ دل پھر سے ٹھہر جاتا ہے",
        f"{poetic_word_bank[3]} میں ڈوبا ہوا یہ شہر نکھر جاتا ہے",
        f"{poetic_word_bank[4]} کے سائے میں سفر اور بھی آسان لگے",
        f"یہی احساس مری ذات کو دریا کر دے",
    ]

    style_tail = {
        "ghazal": "یہ غزل دل کی فضا میں نرمی سے اترتی رہی",
        "nazm": "یہ نظم وقت کے سینے پہ نئی تحریر بنی",
        "shayari": "یہ شاعری آج بھی دل کے بہت نزدیک رہی",
        "rubai": "یہ رباعی کم لفظوں میں مکمل درد کہے",
    }

    lines = []
    for index in range(requested_lines // 2):
        opening = openings[index % len(openings)]
        closing = closings[index % len(closings)]
        if index == (requested_lines // 2) - 1:
            closing = style_tail.get(cleaned_type, closing)
        lines.extend([opening, closing])

    return {
        "title": f"{cleaned_topic} پر {cleaned_type.title()}",
        "topic": cleaned_topic,
        "mood": cleaned_mood,
        "poetry_type": cleaned_type,
        "content": "\n".join(lines),
        "pairs": [(lines[i], lines[i + 1]) for i in range(0, len(lines), 2)],
    }
