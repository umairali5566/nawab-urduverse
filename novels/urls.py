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
]
