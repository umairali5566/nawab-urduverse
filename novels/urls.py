"""
Novels URL Configuration for Nawab Urdu Academy
"""

from django.urls import path
from . import views

urlpatterns = [
    # Novel List
    path('', views.NovelListView.as_view(), name='novel_list'),

    # Like
    path('<str:slug>/like/', views.like_novel, name='like_novel'),

    # Continue Reading
    path('<str:slug>/continue/', views.continue_reading, name='continue_reading'),

    # Canonical Chapter Detail
    path(
        '<str:novel_slug>/chapter-<int:chapter_number>/<str:chapter_slug>/',
        views.ChapterDetailView.as_view(),
        name='chapter_detail',
    ),

    # Legacy Chapter Detail
    path(
        '<str:novel_slug>/<str:chapter_slug>/',
        views.legacy_chapter_redirect,
        name='chapter_detail_legacy',
    ),

    # Novel Detail
    path('<str:slug>/', views.NovelDetailView.as_view(), name='novel_detail'),
]
