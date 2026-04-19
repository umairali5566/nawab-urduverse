"""
Novels URL Configuration for Nawab Urdu Academy
"""

from django.urls import path
from . import views

urlpatterns = [
    # Novel List
    path('', views.NovelListView.as_view(), name='novel_list'),

    # Novel Detail
    path('<slug:slug>/', views.NovelDetailView.as_view(), name='novel_detail'),

    # Continue Reading
    path('<slug:slug>/continue/', views.continue_reading, name='continue_reading'),

    # Chapter Detail
    path('<slug:novel_slug>/<slug:chapter_slug>/', views.ChapterDetailView.as_view(), name='chapter_detail'),
]
