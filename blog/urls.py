"""
Blog URL Configuration for Nawab Urdu Academy
"""

from django.urls import path
from . import views

urlpatterns = [
    # Blog List
    path('', views.BlogListView.as_view(), name='blog_list'),
    
    # Blog Detail
    path('<slug:slug>/', views.BlogDetailView.as_view(), name='blog_detail'),
    
    # Like
    path('<slug:slug>/like/', views.like_post, name='like_post'),
]
