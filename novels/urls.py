"""
Novels URL Configuration for Nawab UrduVerse
"""

from django.urls import path
from . import views

urlpatterns = [
    # Novel List
    path('', views.NovelListView.as_view(), name='novel_list'),
    
    # Categories
    path('categories/', views.novel_categories, name='novel_categories'),
    
    # Continue Reading
    path('<slug:slug>/continue/', views.continue_reading, name='continue_reading'),
    
    # Review
    path('<slug:slug>/review/', views.add_review, name='add_review'),
    
    # Like
    path('<slug:slug>/like/', views.like_novel, name='like_novel'),

    # Chapter Detail (canonical)
    path('<slug:novel_slug>/chapters/<slug:chapter_slug>/', views.ChapterDetailView.as_view(), name='chapter_detail'),

    # Legacy chapter URL support
    path('<slug:novel_slug>/<slug:chapter_slug>/', views.legacy_chapter_redirect, name='chapter_detail_legacy'),

    # Novel Detail
    path('<slug:slug>/', views.NovelDetailView.as_view(), name='novel_detail'),
]
