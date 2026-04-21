"""
Poetry URL Configuration for Nawab Urdu Academy
"""

from django.urls import path

from . import views

urlpatterns = [
    # Poetry list
    path("", views.PoetryListView.as_view(), name="poetry_list"),

    # Poetry detail
    path("<slug:slug>/", views.PoetryDetailView.as_view(), name="poetry_detail"),

    # Like
    path("<slug:slug>/like/", views.like_poetry, name="like_poetry"),
]
