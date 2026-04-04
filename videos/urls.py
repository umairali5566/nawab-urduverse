"""
Videos URL Configuration for Nawab Urdu Academy
"""

from django.urls import path
from . import views

urlpatterns = [
    # Video List
    path('', views.VideoListView.as_view(), name='video_list'),
    
    # Videos by Type
    path('type/<slug:video_type>/', views.videos_by_type, name='videos_by_type'),
    
    # Playlists
    path('playlists/', views.PlaylistListView.as_view(), name='playlist_list'),
    path('playlists/<slug:slug>/', views.PlaylistDetailView.as_view(), name='playlist_detail'),
    
    # Video Detail
    path('<slug:slug>/', views.VideoDetailView.as_view(), name='video_detail'),
    
    # Like
    path('<slug:slug>/like/', views.like_video, name='like_video'),
]

