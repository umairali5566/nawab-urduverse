from django.urls import register_converter


class UnicodeSlugConverter:
    """Allow Unicode slug values in Django URL patterns."""

    regex = r'[^/]+('
    r'(?=/)|$)'

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


register_converter(UnicodeSlugConverter, 'unicode_slug')
