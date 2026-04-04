"""
Quotes URL Configuration for Nawab Urdu Academy
"""

from django.urls import path
from . import views

urlpatterns = [
    # Quote List
    path('', views.QuoteListView.as_view(), name='quote_list'),
    
    # Quotes by Type
    path('type/<slug:quote_type>/', views.quotes_by_type, name='quotes_by_type'),
    
    # Collections
    path('collections/', views.QuoteCollectionListView.as_view(), name='quote_collection_list'),
    path('collections/<slug:slug>/', views.QuoteCollectionDetailView.as_view(), name='quote_collection_detail'),
    
    # Quote Detail
    path('<slug:slug>/', views.QuoteDetailView.as_view(), name='quote_detail'),
    
    # Like
    path('<slug:slug>/like/', views.like_quote, name='like_quote'),
    
    # Share
    path('<slug:slug>/share/', views.share_quote, name='share_quote'),
    
    # Download
    path('<slug:slug>/download/', views.download_quote_image, name='download_quote'),
]

