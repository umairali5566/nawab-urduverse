from django.db.utils import OperationalError

from .models import SiteSetting, SiteTheme, Logo
from .services import get_popular_content
from nawab_urduverse.constants import NAV_LABELS, CONTENT_TYPES, DASHBOARD_LABELS

def site_context(request):
    try:
        site_settings = {s.key: s.value for s in SiteSetting.objects.all()}
        popular = get_popular_content(limit=5)

        # Get active theme or create default
        try:
            theme = SiteTheme.objects.get(is_active=True)
        except SiteTheme.DoesNotExist:
            # Create default theme if none exists
            theme = SiteTheme.objects.create(
                name='Default Theme',
                primary_color='#007bff',
                background_color='#ffffff',
                text_color='#333333',
                font_family='Poppins, sans-serif',
                is_active=True
            )
        
        # Get active logo
        try:
            logo = Logo.objects.get(is_active=True)
        except Logo.DoesNotExist:
            logo = None
    except OperationalError:
        site_settings = {}
        popular = {}
        theme = None
        logo = None

    return {
        'site_settings': site_settings,
        'popular': popular,
        'theme': theme,
        'logo': logo,
        'NAV_LABELS': NAV_LABELS,
        'CONTENT_TYPES': CONTENT_TYPES,
        'DASHBOARD_LABELS': DASHBOARD_LABELS,
    }