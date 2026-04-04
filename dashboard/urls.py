from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('novels/', views.novel_list, name='dashboard_novel_list'),
    path('add-novel/', views.add_novel, name='dashboard_add_novel'),
    path('stories/', views.story_list, name='dashboard_story_list'),
    path('add-story/', views.add_story, name='dashboard_add_story'),
    path('poetry/', views.poetry_list, name='dashboard_poetry_list'),
    path('add-poetry/', views.add_poetry, name='dashboard_add_poetry'),
    path('blog/', views.blog_list, name='dashboard_blog_list'),
    path('add-blog/', views.add_blog, name='dashboard_add_blog'),
    path('quotes/', views.quote_list, name='dashboard_quote_list'),
    path('add-quote/', views.add_quote, name='dashboard_add_quote'),
    path('videos/', views.video_list, name='dashboard_video_list'),
    path('add-video/', views.add_video, name='dashboard_add_video'),
    path('bulk-upload/', views.bulk_upload, name='dashboard_bulk_upload'),
    path('users/', views.user_list, name='dashboard_user_list'),
]