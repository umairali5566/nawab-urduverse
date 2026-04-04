from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from core.services import build_seo_context, rate_limit_request
from poetry.models import Poetry

from .services import (
    AI_POETRY_STYLES,
    generate_poetry as generate_poetry_service,
    get_ai_search_suggestions,
    perform_ai_search,
    suggestion_seed_from_payload,
    synthesize_urdu_audio,
)


def ai_studio(request):
    return render(
        request,
        "ai/ai_studio.html",
        {
            "ai_styles": [
                ("ghazal", "Ghazal"),
                ("nazm", "Nazm"),
                ("sad", "Sad"),
                ("romantic", "Romantic"),
            ],
            "trending_poetry": Poetry.objects.filter(is_published=True).select_related("author").order_by("-views_count")[:6],
            **build_seo_context(
                request,
                title=f"AI Studio | {settings.SITE_NAME}",
                description="Generate Urdu poetry with AI, listen in Urdu voice, and explore smart search inside the Nawab UrduVerse AI Studio.",
                keywords=f"AI Urdu poetry, Urdu TTS, Urdu search, {settings.SITE_KEYWORDS}",
                og_type="website",
            ),
        },
    )


@require_POST
def generate_poetry(request):
    limited, retry_after = rate_limit_request(request, "ai_generate_poetry_v2", limit=6, window=300)
    if limited:
        return JsonResponse(
            {"success": False, "message": f"Please wait {retry_after} seconds before generating again."},
            status=429,
        )

    topic = request.POST.get("topic", "")
    style = request.POST.get("style", "ghazal").lower().strip()
    if style not in AI_POETRY_STYLES:
        style = "ghazal"

    try:
        payload = generate_poetry_service(topic=topic, style=style)
    except ValueError as exc:
        return JsonResponse({"success": False, "message": str(exc)}, status=400)
    except Exception as exc:
        return JsonResponse({"success": False, "message": str(exc)}, status=503)

    return JsonResponse({"success": True, **payload})


@require_POST
def tts_audio(request):
    limited, retry_after = rate_limit_request(request, "ai_tts_audio", limit=10, window=300)
    if limited:
        return JsonResponse(
            {"success": False, "message": f"Please wait {retry_after} seconds before requesting more audio."},
            status=429,
        )

    text = request.POST.get("text", "")
    cache_key = request.POST.get("cache_key", "ai-studio")

    try:
        audio_url, engine = synthesize_urdu_audio(text=text, cache_key=cache_key)
    except ValueError as exc:
        return JsonResponse({"success": False, "message": str(exc)}, status=400)
    except Exception as exc:
        return JsonResponse({"success": False, "message": str(exc)}, status=503)

    return JsonResponse({"success": True, "audio_url": audio_url, "engine": engine})


@require_GET
def ai_search(request):
    limited, retry_after = rate_limit_request(request, "ai_search", limit=30, window=300)
    if limited:
        return JsonResponse(
            {"success": False, "message": f"Please wait {retry_after} seconds before searching again."},
            status=429,
        )

    query = request.GET.get("q", "")
    mode = request.GET.get("mode", "results")
    content_type = request.GET.get("type", "all")

    if mode == "suggestions":
        return JsonResponse(
            {
                "success": True,
                "query": query,
                "suggestions": get_ai_search_suggestions(
                    query,
                    limit=getattr(settings, "SEARCH_SUGGESTION_LIMIT", 8),
                ),
            }
        )

    payload = perform_ai_search(
        query,
        content_type=content_type,
        limit=getattr(settings, "AI_SEARCH_RESULT_LIMIT", 18),
    )

    return JsonResponse(
        {
            "success": True,
            "query": payload["query"],
            "intent": payload["intent"],
            "results": [
                {
                    "title": item["title"],
                    "snippet": item["snippet"],
                    "author": item["author"],
                    "content_type": item["content_type"],
                    "content_type_label": item["content_type_label"],
                    "url": item["url"],
                    "image_url": item["image_url"],
                    "score": item["score"],
                }
                for item in payload["results"]
            ],
            "suggestions": suggestion_seed_from_payload(payload),
        }
    )
