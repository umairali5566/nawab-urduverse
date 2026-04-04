"""
Nawab UrduVerse - Django Settings
A complete Urdu literature platform by Nawab
"""

import os
import sys
from importlib.util import find_spec
from pathlib import Path
from urllib.parse import urlparse

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


def add_static_headers(headers, path, url):
    """Allow the static service worker to control the full app scope."""
    if url.endswith('/sw.js'):
        headers['Service-Worker-Allowed'] = '/'
        headers['Cache-Control'] = 'no-cache'
    elif url.endswith('/manifest.json'):
        headers['Cache-Control'] = 'public, max-age=3600'


def build_database_config():
    """Support sqlite locally and PostgreSQL in production."""
    database_url = os.environ.get('DATABASE_URL', '').strip()
    if database_url:
        parsed = urlparse(database_url)
        if parsed.scheme in {'postgres', 'postgresql'}:
            return {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': parsed.path.lstrip('/'),
                'USER': parsed.username or '',
                'PASSWORD': parsed.password or '',
                'HOST': parsed.hostname or '',
                'PORT': str(parsed.port or '5432'),
                'CONN_MAX_AGE': int(os.environ.get('DB_CONN_MAX_AGE', '60')),
                'OPTIONS': {'sslmode': os.environ.get('DB_SSLMODE', 'require')},
            }

    if os.environ.get('DB_NAME'):
        return {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'nawab_urduverse'),
            'USER': os.environ.get('DB_USER', 'nawab_user'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
            'CONN_MAX_AGE': int(os.environ.get('DB_CONN_MAX_AGE', '60')),
            'OPTIONS': {'sslmode': os.environ.get('DB_SSLMODE', 'prefer')},
        }

    return {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'nawab-urduverse-local-dev-key-9f4c2a6e1b7d3k8m5p0q2r4s6t8u1v3x5z7',
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
TESTING = 'test' in sys.argv

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    # Django built-in apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.humanize',

    # Third-party apps
    'ckeditor',
    'ckeditor_uploader',
    'django_cleanup.apps.CleanupConfig',
    'crispy_forms',
    'crispy_bootstrap5',
    
    # Custom apps
    'core',
    'accounts',
    'novels',
    'stories',
    'poetry',
    'quotes',
    'blog',
    'videos',
    'dashboard',
    'ai_features',
]

#if find_spec('sslserver') is not None:
#    INSTALLED_APPS.append('sslserver')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'nawab_urduverse.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.site_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'nawab_urduverse.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': build_database_config()
}

# For PostgreSQL production (uncomment when deploying)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.environ.get('DB_NAME', 'nawab_urduverse'),
#         'USER': os.environ.get('DB_USER', 'nawab_user'),
#         'PASSWORD': os.environ.get('DB_PASSWORD', 'your_password'),
#         'HOST': os.environ.get('DB_HOST', 'localhost'),
#         'PORT': os.environ.get('DB_PORT', '5432'),
#     }
# }

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 4
        }
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'ur'

TIME_ZONE = 'Asia/Karachi'

USE_I18N = True

USE_TZ = True

# Languages
LANGUAGES = [
    ('ur', 'Urdu'),
    ('en', 'English'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_BACKEND = (
    'whitenoise.storage.CompressedManifestStaticFilesStorage'
    if not DEBUG and not TESTING
    else 'whitenoise.storage.CompressedStaticFilesStorage'
)
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': STATICFILES_BACKEND,
    },
}
WHITENOISE_ADD_HEADERS_FUNCTION = add_static_headers
WHITENOISE_MIMETYPES = {
    '.js': 'application/javascript',
}

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CKEditor Configuration
CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent'],
            ['JustifyRight', 'JustifyCenter', 'JustifyLeft', 'JustifyBlock'],
            ['Link', 'Unlink'],
            ['RemoveFormat', 'Source'],
            ['Image', 'Iframe'],
        ],
        'height': 300,
        'width': '100%',
        'contentsLangDirection': 'rtl',
        'language': 'ur',
    },
}

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Authentication
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Site Settings
SITE_NAME = 'Nawab UrduVerse'
SITE_TAGLINE = 'اردو ادب کی جدید دنیا'
SITE_DESCRIPTION = 'Nawab UrduVerse is a modern Urdu literature platform for poetry, blogs, quotes, novels, and literary videos.'
SITE_KEYWORDS = 'Urdu poetry, Urdu novels, Urdu blogs, Urdu quotes, Urdu literature, literary videos, Nawab UrduVerse, اردو شاعری, اردو ناول, اردو ادب'

# Poetry TTS configuration
POETRY_TTS_ENGINE = os.environ.get('POETRY_TTS_ENGINE', 'edge')  # edge | gtts
POETRY_TTS_EDGE_VOICE = os.environ.get('POETRY_TTS_EDGE_VOICE', 'ur-PK-AsadNeural')
POETRY_TTS_GTTS_TLD = os.environ.get('POETRY_TTS_GTTS_TLD', 'com')

# Email Settings (configure for production)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@gmail.com'
# EMAIL_HOST_PASSWORD = 'your-password'

# Pagination
PAGINATION_PAGE_SIZE = 12

# Cache Settings (configure for production)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'nawab-urdu-acadmey-cache',
        'TIMEOUT': int(os.environ.get('CACHE_TIMEOUT', '300')),
    }
}

# Feature flags and monetization
AI_STUDIO_ENABLED = os.environ.get('AI_STUDIO_ENABLED', 'True').lower() == 'true'
PREMIUM_MEMBERSHIP_ENABLED = os.environ.get('PREMIUM_MEMBERSHIP_ENABLED', 'True').lower() == 'true'
ADSENSE_CLIENT_ID = os.environ.get('ADSENSE_CLIENT_ID', '')
ADSENSE_SLOT_INLINE = os.environ.get('ADSENSE_SLOT_INLINE', '')
ADSENSE_SLOT_SIDEBAR = os.environ.get('ADSENSE_SLOT_SIDEBAR', '')
ADSENSE_ENABLED = bool(ADSENSE_CLIENT_ID)
SEARCH_SUGGESTION_LIMIT = int(os.environ.get('SEARCH_SUGGESTION_LIMIT', '8'))
AI_SEARCH_RESULT_LIMIT = int(os.environ.get('AI_SEARCH_RESULT_LIMIT', '18'))
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
OPENAI_POETRY_MODEL = os.environ.get('OPENAI_POETRY_MODEL', 'gpt-5-mini')
OPENAI_SEARCH_MODEL = os.environ.get('OPENAI_SEARCH_MODEL', 'gpt-5-mini')
OPENAI_REASONING_EFFORT = os.environ.get('OPENAI_REASONING_EFFORT', 'low')

# Production-friendly security defaults
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',')
    if origin.strip()
]
SESSION_COOKIE_SECURE = not DEBUG and os.environ.get('SESSION_COOKIE_SECURE', 'True').lower() == 'true'
CSRF_COOKIE_SECURE = not DEBUG and os.environ.get('CSRF_COOKIE_SECURE', 'True').lower() == 'true'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'
X_FRAME_OPTIONS = 'DENY'

USE_HTTPS = os.environ.get(
    'USE_HTTPS',
    'False' if DEBUG or TESTING else 'True',
).lower() == 'true'
SECURE_SSL_REDIRECT = USE_HTTPS and not DEBUG
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https') if USE_HTTPS else None
USE_X_FORWARDED_HOST = USE_HTTPS
SECURE_HSTS_SECONDS = 31536000 if USE_HTTPS and not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = USE_HTTPS and not DEBUG
SECURE_HSTS_PRELOAD = USE_HTTPS and not DEBUG

# Explicitly disable SSL settings for development
if DEBUG:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_HSTS_SECONDS = 0

# CKEditor package advisory warning.
# This suppresses the noisy check output in development until editor migration.
SILENCED_SYSTEM_CHECKS = ['ckeditor.W001']
