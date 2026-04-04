from django.urls import path

from . import views

urlpatterns = [
    path("generate-poetry/", views.generate_poetry, name="ai_generate"),
    path("tts/", views.tts_audio, name="ai_tts"),
    path("search/", views.ai_search, name="ai_search"),
]
