"""
Core Utilities for Nawab Urdu Academy
"""

from blog.models import BlogPost
from novels.models import Novel
from poetry.models import Poetry
from quotes.models import Quote
from stories.models import Story
from videos.models import Video


def get_author_published_content(author, limit=None):
    """
    Get published content for an author, optionally limited.
    Returns dict with content types.
    """
    content = {
        'novels': Novel.objects.filter(author=author, is_published=True).order_by('-published_at', '-created_at'),
        'stories': Story.objects.filter(author=author, is_published=True).order_by('-published_at', '-created_at'),
        'poetry': Poetry.objects.filter(author=author, is_published=True).order_by('-published_at', '-created_at'),
        'quotes': Quote.objects.filter(author=author, is_published=True).order_by('-created_at'),
        'blogs': BlogPost.objects.filter(author=author, is_published=True).order_by('-published_at', '-created_at'),
        'videos': Video.objects.filter(author=author, is_published=True).order_by('-published_at', '-created_at'),
    }
    if limit:
        for key in content:
            content[key] = content[key][:limit]
    return content


def get_author_published_content_by_name(display_name, limit=6):
    """
    Get published content for an author by display name, limited.
    Used for user profiles.
    """
    content = {
        'novels': Novel.objects.filter(author__name=display_name, is_published=True)[:limit],
        'stories': Story.objects.filter(author__name=display_name, is_published=True)[:limit],
        'poetry': Poetry.objects.filter(author__name=display_name, is_published=True)[:limit],
    }
    return content