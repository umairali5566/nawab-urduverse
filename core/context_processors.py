"""
Context processors for global template data.
"""

from django.conf import settings

from .models import Category, Notification, PremiumPlan, SiteSetting, UserMembership
from .services import get_latest_notifications, get_popular_content, get_trending_sidebar_posts


def site_context(request):
    """Add site-wide context variables."""
    site_settings = {setting.key: setting.value for setting in SiteSetting.objects.all()}
    popular = get_popular_content(limit=5)
    notifications = []
    unread_notifications_count = 0
    active_membership = None

    if request.user.is_authenticated:
        notifications = get_latest_notifications(request.user, limit=6)
        unread_notifications_count = Notification.objects.filter(user=request.user, is_read=False).count()
        active_membership = UserMembership.objects.select_related("plan").filter(user=request.user).first()

    context = {
        "SITE_NAME": getattr(settings, "SITE_NAME", "Nawab Urdu Academy"),
        "SITE_TAGLINE": getattr(settings, "SITE_TAGLINE", ""),
        "SITE_DESCRIPTION": getattr(settings, "SITE_DESCRIPTION", "Premium Urdu poetry, novels, blogs and literary content"),
        "SITE_KEYWORDS": getattr(settings, "SITE_KEYWORDS", ""),
        "AI_STUDIO_ENABLED": getattr(settings, "AI_STUDIO_ENABLED", True),
        "PREMIUM_MEMBERSHIP_ENABLED": getattr(settings, "PREMIUM_MEMBERSHIP_ENABLED", True),
        "ADSENSE_ENABLED": getattr(settings, "ADSENSE_ENABLED", False),
        "ADSENSE_CLIENT_ID": getattr(settings, "ADSENSE_CLIENT_ID", ""),
        "ADSENSE_SLOT_INLINE": getattr(settings, "ADSENSE_SLOT_INLINE", ""),
        "ADSENSE_SLOT_SIDEBAR": getattr(settings, "ADSENSE_SLOT_SIDEBAR", ""),
        "categories": Category.objects.filter(is_active=True),
        "site_settings": site_settings,
        "trending_sidebar_posts": get_trending_sidebar_posts(limit=8),
        "header_notifications": notifications,
        "unread_notifications_count": unread_notifications_count,
        "active_membership": active_membership,
        "premium_plans": PremiumPlan.objects.filter(is_active=True).order_by("price", "billing_cycle_days")[:3],
        **popular,
    }
    return context
