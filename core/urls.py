"""
Core URL Configuration for Nawab Urdu Academy
"""

from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    
    # Static Pages
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    
    # Authors
    path('authors/', views.AuthorListView.as_view(), name='author_list'),
    path('authors/<slug:slug>/', views.AuthorDetailView.as_view(), name='author_detail'),
    
    # Search
    path('search/', views.search, name='search'),
    path('search/api/', views.search_api, name='search_api'),
    path('search/suggestions/', views.search_suggestions, name='search_suggestions'),

    # Admin Upload
    path('admin-upload/', views.admin_upload, name='admin_upload'),

    # SEO
    path('robots.txt', views.robots_txt, name='robots_txt'),
    
    # Categories
    path('categories/', views.all_categories, name='all_categories'),
    path('categories/<slug:slug>/', views.category_detail, name='category_detail'),
    path('category/<slug:slug>/', views.category_detail, name='legacy_category_detail'),
    
    # Newsletter
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),

    # Engagement
    path('engage/like/<str:content_type>/<int:object_id>/', views.toggle_like, name='toggle_like'),
    path('engage/share/<str:content_type>/<int:object_id>/', views.track_share, name='track_share'),

    # Notifications and membership
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/mark-read/', views.notifications_mark_read, name='notifications_mark_read'),
    path('membership/', views.membership_view, name='membership'),
    path('membership/activate/<slug:slug>/', views.activate_membership_view, name='activate_membership'),
    
    # Bookmarks
    path('bookmark/<str:content_type>/<int:object_id>/', views.add_bookmark, name='add_bookmark'),
    path('bookmarks/', views.bookmarks_dashboard, name='bookmarks_dashboard'),
    
    # Comments
    path('comment/<str:content_type>/<int:object_id>/', views.add_comment, name='add_comment'),
    
    # Demo Pages
    path('hover-cards-demo/', views.hover_cards_demo, name='hover_cards_demo'),
]
