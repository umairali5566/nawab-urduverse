"""
Accounts URL Configuration for Nawab UrduVerse
"""

from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Profile
    path('dashboard/', views.dashboard, name='dashboard'),
    path('my-content/', views.my_content, name='my_content'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('profile/bookmarks/', views.bookmarks, name='bookmarks'),
    path('profile/delete/', views.delete_account, name='delete_account'),
    
    # Public Profile
    path('user/<str:username>/', views.public_profile, name='public_profile'),
]
