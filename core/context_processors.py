from django.db.utils import OperationalError

def site_context(request):
    try:
        site_settings = {s.key: s.value for s in SiteSetting.objects.all()}
        popular = get_popular_content(limit=5)
    except:
        site_settings = {}
        popular = {}
    
    return {
        'site_settings': site_settings,
        'popular': popular
    }