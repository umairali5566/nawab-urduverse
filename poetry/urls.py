"""
Poetry URL Configuration for Nawab UrduVerse
"""

from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    # Poetry list
    path("", views.PoetryListView.as_view(), name="poetry_list"),
    path("author/<slug:author_slug>/", views.author_profile, name="author_profile"),

    # Poetry by taxonomy
    path("type/<slug:poetry_type>/", views.poetry_by_type, name="poetry_by_type"),
    path("mood/<slug:mood>/", views.poetry_by_mood, name="poetry_by_mood"),

    # Collections
    path("collections/", views.CollectionListView.as_view(), name="collection_list"),
    path("collections/<slug:slug>/", views.CollectionDetailView.as_view(), name="collection_detail"),

    # Premium Poetry Reading (distraction-free)
    path("<slug:author_slug>/<slug:slug>/read/", views.PoetryPremiumView.as_view(), name="poetry_premium"),

    # Canonical SEO-friendly poetry routes
    path("<slug:author_slug>/<slug:slug>/", views.PoetryDetailView.as_view(), name="poetry_detail"),
    path("<slug:author_slug>/<slug:slug>/like/", views.like_poetry, name="like_poetry"),
    path("<slug:author_slug>/<slug:slug>/share/", views.share_poetry, name="share_poetry"),
    path("<slug:author_slug>/<slug:slug>/tts/", views.poetry_tts, name="poetry_tts"),

    # Legacy routes (backward compatibility)
    path("<slug:slug>/", views.legacy_poetry_redirect, name="legacy_poetry_detail"),
]
