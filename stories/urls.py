"""
Stories URL Configuration for Nawab UrduVerse
"""

from django.urls import path
from . import views

urlpatterns = [
    # Story List
    path('', views.StoryListView.as_view(), name='story_list'),
    
    # Categories
    path('categories/', views.story_categories, name='story_categories'),
    
    # Story Detail
    path('<slug:slug>/', views.StoryDetailView.as_view(), name='story_detail'),
    
    # Like
    path('<slug:slug>/like/', views.like_story, name='like_story'),
]
