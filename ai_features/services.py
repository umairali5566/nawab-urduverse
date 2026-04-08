import json
import re
from typing import Any

from django.conf import settings
from django.db.models import Q
from django.utils.html import strip_tags
from django.utils.text import slugify

from blog.models import BlogPost
from novels.models import Novel
from poetry.models import Poetry
from poetry.tts import generate_tts_audio
from quotes.models import Quote
from stories.models import Story
from videos.models import Video

from core.models import Author
from core.services import generate_poetry_from_prompt


AI_SEARCH_CONTENT_TYPES = {"all", "poetry", "blog", "video", "novel", "story", "quote", "author"}
AI_POETRY_STYLES = {"ghazal", "nazm", "sad", "romantic"}
SEARCH_STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "about",
    "best",
    "blog",
    "blogs",
    "find",
    "for",
    "in",
    "is",
    "latest",
    "love",
    "me",
    "my",
    "novel",
    "novels",
    "quote",
    "quotes",
    "of",
    "on",
    "or",
    "please",
    "poem",
    "poems",
    "poetry",
    "romantic",
    "sad",
    "search",
    "show",
    "story",
    "stories",
    "author",
    "authors",
    "the",
    "to",
    "urdu",
    "video",
    "videos",
    "with",
    "کی",
    "کے",
    "میں",
    "اور",
    "یہ",
    "وہ",
    "ہے",
    "ہیں",
    "کا",
    "کو",
    "سے",
    "پر",
    "شاعری",
    "غزل",
    "نظم",
    "ناول",
    "ویڈیو",
    "بلاگ",
}

CONTENT_TYPE_KEYWORDS = {
    "author": {"author", "authors", "poet", "poets", "writer", "writers"},
    "poetry": {"poetry", "poem", "poems", "ghazal", "nazm", "shayari", "sher", "شاعری", "غزل", "نظم", "شعر"},
    "blog": {"blog", "blogs", "article", "articles", "essay", "blogpost", "بلاگ", "مضمون"},
    "video": {"video", "videos", "watch", "clip", "youtube", "ویڈیو", "یوٹیوب"},
    "novel": {"novel", "novels", "book", "books", "read", "ناول", "کتاب"},
    "story": {"story", "stories", "fiction", "افسانہ", "کہانی"},
}


class AIServiceError(Exception):
    pass


class AIConfigurationError(AIServiceError):
    pass


def normalize_text(value: Any, *, limit: int = 5000) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()[:limit]


def normalize_multiline_text(value: Any, *, limit: int = 5000) -> str:
    text = str(value or "").replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()[:limit]


def extract_plain_text(value: Any, *, limit: int = 3000) -> str:
    return normalize_multiline_text(strip_tags(str(value or "")), limit=limit)


def tokenize_text(*parts: Any, limit: int = 10) -> list[str]:
    blob = " ".join(normalize_text(strip_tags(str(part or "")), limit=1200) for part in parts if part)
    tokens = re.findall(r"[A-Za-z\u0600-\u06FF]{2,}", blob.lower())
    unique_tokens = []
    seen = set()
    for token in tokens:
        if token in SEARCH_STOP_WORDS or token.isdigit():
            continue
        if token not in seen:
            seen.add(token)
            unique_tokens.append(token)
        if len(unique_tokens) >= limit:
            break
    return unique_tokens


def format_poetry_pairs(poetry_text: str) -> list[tuple[str, str]]:
    lines = [line.strip() for line in normalize_multiline_text(poetry_text).split("\n") if line.strip()]
    pairs = []
    for index in range(0, len(lines), 2):
        first = lines[index]
        second = lines[index + 1] if index + 1 < len(lines) else ""
        pairs.append((first, second))
    return pairs


def poetry_pairs_as_dicts(poetry_text: str) -> list[dict[str, str]]:
    return [{"first": first, "second": second} for first, second in format_poetry_pairs(poetry_text)]


def get_openai_client():
    api_key = normalize_text(getattr(settings, "OPENAI_API_KEY", ""), limit=300)
    if not api_key:
        raise AIConfigurationError("OPENAI_API_KEY is not configured.")

    try:
        from openai import OpenAI
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise AIConfigurationError("The openai package is not installed.") from exc

    return OpenAI(api_key=api_key)


def openai_json_response(*, model: str, instructions: str, prompt: str, schema_name: str, schema: dict, max_output_tokens: int = 900) -> dict:
    client = get_openai_client()
    response = client.responses.create(
        model=model,
        reasoning={"effort": getattr(settings, "OPENAI_REASONING_EFFORT", "low")},
        instructions=instructions,
        input=prompt,
        max_output_tokens=max_output_tokens,
        text={
            "format": {
                "type": "json_schema",
                "name": schema_name,
                "strict": True,
                "schema": schema,
            }
        },
    )
    output_text = normalize_text(getattr(response, "output_text", ""), limit=10000)
    if not output_text:
        raise AIServiceError("The OpenAI response was empty.")
    return json.loads(output_text)


def generate_poetry(topic: str, style: str = "ghazal") -> dict:
    cleaned_topic = normalize_text(topic, limit=120)
    cleaned_style = normalize_text(style, limit=30).lower()

    if len(cleaned_topic) < 2:
        raise ValueError("Topic must contain at least 2 characters.")
    if cleaned_style not in AI_POETRY_STYLES:
        cleaned_style = "ghazal"

    instructions = (
        "You are an expert Urdu poet. Create original Urdu poetry with natural diction, graceful rhythm, "
        "and proper sher formatting. Return valid JSON only."
    )
    prompt = (
        f"Generate a beautiful Urdu {cleaned_style} about '{cleaned_topic}'. "
        "Use traditional sher format with exactly 2 lines per sher, avoid numbering, and keep the tone literary."
    )
    schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "poetry_text": {"type": "string"},
            "style": {"type": "string"},
            "mood": {"type": "string"},
        },
        "required": ["title", "poetry_text", "style", "mood"],
        "additionalProperties": False,
    }

    try:
        payload = openai_json_response(
            model=getattr(settings, "OPENAI_POETRY_MODEL", "gpt-5-mini"),
            instructions=instructions,
            prompt=prompt,
            schema_name="urdu_poetry_generation",
            schema=schema,
            max_output_tokens=1000,
        )
        poetry_text = normalize_multiline_text(payload.get("poetry_text", ""), limit=4000)
        pairs = format_poetry_pairs(poetry_text)
        if not pairs:
            raise AIServiceError("The AI response could not be formatted into sher pairs.")
        return {
            "title": normalize_text(payload.get("title") or f"{cleaned_topic} پر اردو شاعری", limit=140),
            "topic": cleaned_topic,
            "style": normalize_text(payload.get("style") or cleaned_style, limit=30).lower(),
            "mood": normalize_text(payload.get("mood") or cleaned_style, limit=30).lower(),
            "content": poetry_text,
            "pairs": pairs,
            "pairs_json": poetry_pairs_as_dicts(poetry_text),
            "provider": "openai",
        }
    except Exception:
        fallback_style = cleaned_style if cleaned_style in {"ghazal", "nazm"} else "ghazal"
        fallback_mood = cleaned_style if cleaned_style in {"sad", "romantic"} else "romantic"
        payload = generate_poetry_from_prompt(
            cleaned_topic,
            mood=fallback_mood,
            poetry_type=fallback_style,
            line_count=6,
        )
        return {
            **payload,
            "style": payload.get("poetry_type", fallback_style),
            "provider": "local-fallback",
        }


def synthesize_urdu_audio(text: str, *, cache_key: str = "ai-studio") -> tuple[str, str]:
    clean_text = normalize_multiline_text(text, limit=6000)
    if len(clean_text) < 2:
        raise ValueError("Text is required for Urdu audio.")
    return generate_tts_audio(text=clean_text, cache_key=cache_key)


def heuristic_search_intent(query: str) -> dict:
    cleaned_query = normalize_text(query, limit=240)
    lower_query = cleaned_query.lower()
    content_type = "all"

    for item_type, markers in CONTENT_TYPE_KEYWORDS.items():
        if any(marker in lower_query for marker in markers):
            content_type = item_type
            break

    author = ""
    by_match = re.search(r"\bby\s+([A-Za-z\u0600-\u06FF][A-Za-z\u0600-\u06FF\s]{1,60})$", cleaned_query, flags=re.IGNORECASE)
    if by_match:
        author = normalize_text(by_match.group(1), limit=80)
    else:
        urdu_match = re.search(r"(?:از|کی|کے)\s+([A-Za-z\u0600-\u06FF][A-Za-z\u0600-\u06FF\s]{1,60})$", cleaned_query)
        if urdu_match:
            author = normalize_text(urdu_match.group(1), limit=80)

    keywords = tokenize_text(cleaned_query, limit=8)
    return {
        "query": cleaned_query,
        "content_type": content_type,
        "author": author,
        "keywords": keywords,
        "parsed_with": "heuristic",
    }


def parse_search_intent(query: str) -> dict:
    intent = heuristic_search_intent(query)
    if len(intent["query"]) < 8:
        return intent

    schema = {
        "type": "object",
        "properties": {
            "content_type": {"type": "string", "enum": ["all", "poetry", "blog", "video", "novel", "story", "quote", "author"]},
            "author": {"type": "string"},
            "keywords": {
                "type": "array",
                "items": {"type": "string"},
                "maxItems": 8,
            },
        },
        "required": ["content_type", "author", "keywords"],
        "additionalProperties": False,
    }
    try:
        payload = openai_json_response(
            model=getattr(settings, "OPENAI_SEARCH_MODEL", "gpt-5-mini"),
            instructions=(
                "Extract the search intent from a natural-language query for an Urdu literature platform. "
                "Return JSON only."
            ),
            prompt=(
                f"Query: {intent['query']}\n"
                "Infer the desired content type, author if present, and the most important search keywords."
            ),
            schema_name="urdu_search_intent",
            schema=schema,
            max_output_tokens=300,
        )
        ai_content_type = payload.get("content_type", "all")
        if ai_content_type not in AI_SEARCH_CONTENT_TYPES:
            ai_content_type = "all"
        ai_keywords = [normalize_text(item, limit=40).lower() for item in payload.get("keywords", []) if normalize_text(item, limit=40)]
        return {
            "query": intent["query"],
            "content_type": ai_content_type,
            "author": normalize_text(payload.get("author"), limit=80),
            "keywords": ai_keywords or intent["keywords"],
            "parsed_with": "openai",
        }
    except Exception:
        return intent


def resolve_item_title(item: Any) -> str:
    return normalize_text(getattr(item, "title", "") or getattr(item, "name", "") or getattr(item, "text", ""), limit=180)


def resolve_item_snippet(item: Any) -> str:
    if isinstance(item, Author):
        return normalize_text(item.bio or item.name, limit=220)
    if isinstance(item, Poetry):
        return normalize_text(item.plain_text_content, limit=220)
    if isinstance(item, BlogPost):
        return normalize_text(item.excerpt or extract_plain_text(item.content, limit=240), limit=220)
    if isinstance(item, Novel):
        return normalize_text(item.description_text, limit=220)
    if isinstance(item, Story):
        return normalize_text(item.excerpt or extract_plain_text(item.content, limit=240), limit=220)
    if isinstance(item, Quote):
        return normalize_text(item.text, limit=220)
    if isinstance(item, Video):
        return normalize_text(item.description, limit=220)
    return ""


def resolve_item_image(item: Any) -> str:
    field_candidates = ["featured_image", "cover_image", "thumbnail", "background_image", "image"]
    for field_name in field_candidates:
        field = getattr(item, field_name, None)
        try:
            if field and field.url:
                return field.url
        except Exception:
            continue
    if isinstance(item, Video):
        return item.get_thumbnail_url() or ""
    return ""


def _collect_item_categories(item: Any) -> list[Any]:
    categories = []
    category = getattr(item, "category", None)
    if category is not None:
        categories.append(category)

    category_manager = getattr(item, "categories", None)
    if category_manager is None:
        return categories

    try:
        categories.extend(list(category_manager.all()))
    except Exception:
        pass
    return categories


def get_item_keywords(item: Any) -> set[str]:
    category_blob = ""
    category_parts = []
    for category in _collect_item_categories(item):
        name = getattr(category, "name", "")
        english_name = getattr(category, "name_english", "")
        if name:
            category_parts.append(name)
        if english_name:
            category_parts.append(english_name)
    if category_parts:
        category_blob = " ".join(category_parts)

    author_name = getattr(getattr(item, "author", None), "name", "")
    return set(
        tokenize_text(
            resolve_item_title(item),
            resolve_item_snippet(item),
            getattr(item, "tags", ""),
            category_blob,
            author_name,
            limit=16,
        )
    )


def _author_matches(item: Any, author_term: str) -> bool:
    if not author_term:
        return False
    author_name = normalize_text(
        getattr(getattr(item, "author", None), "name", "") or getattr(item, "name", ""),
        limit=120,
    ).lower()
    return bool(author_name and author_term.lower() in author_name)


def _build_search_candidates(content_type: str, query: str, author_term: str):
    common_limit = 40
    if content_type == "author":
        return Author.objects.filter(
            Q(name__icontains=query),
            is_active=True,
        )[:common_limit]
    if content_type == "poetry":
        return Poetry.objects.filter(
            Q(title__icontains=query)
            | Q(content__icontains=query)
            | Q(tags__icontains=query)
            | Q(author__name__icontains=author_term or query),
            is_published=True,
        ).select_related("author", "category")[:common_limit]
    if content_type == "blog":
        return BlogPost.objects.filter(
            Q(title__icontains=query)
            | Q(content__icontains=query)
            | Q(excerpt__icontains=query)
            | Q(tags__icontains=query)
            | Q(author__name__icontains=author_term or query),
            is_published=True,
        ).select_related("author").prefetch_related("categories")[:common_limit]
    if content_type == "video":
        return Video.objects.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(tags__icontains=query)
            | Q(author__name__icontains=author_term or query),
            is_published=True,
        ).select_related("author").prefetch_related("categories")[:common_limit]
    if content_type == "novel":
        return Novel.objects.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(author__name__icontains=author_term or query),
            is_published=True,
        ).select_related("author", "category")[:common_limit]
    if content_type == "story":
        return Story.objects.filter(
            Q(title__icontains=query)
            | Q(content__icontains=query)
            | Q(excerpt__icontains=query)
            | Q(tags__icontains=query)
            | Q(author__name__icontains=author_term or query),
            is_published=True,
        ).select_related("author").prefetch_related("categories")[:common_limit]
    if content_type == "quote":
        return Quote.objects.filter(
            Q(text__icontains=query)
            | Q(tags__icontains=query)
            | Q(author__name__icontains=author_term or query),
            is_published=True,
        ).select_related("author").prefetch_related("categories")[:common_limit]
    return []


def _score_search_item(item: Any, *, requested_type: str, intent: dict, query: str) -> int:
    score = 0
    title = resolve_item_title(item).lower()
    snippet = resolve_item_snippet(item).lower()
    author_name = normalize_text(
        getattr(getattr(item, "author", None), "name", "") or getattr(item, "name", ""),
        limit=120,
    ).lower()
    item_keywords = get_item_keywords(item)
    query_lower = query.lower()

    if requested_type != "all":
        score += 30
    if title == query_lower:
        score += 60
    elif query_lower and query_lower in title:
        score += 28
    elif query_lower and query_lower in snippet:
        score += 12

    if intent.get("author") and _author_matches(item, intent["author"]):
        score += 30

    for keyword in intent.get("keywords", []):
        if keyword in title:
            score += 18
        elif keyword in author_name:
            score += 16
        elif keyword in item_keywords:
            score += 10
        elif keyword in snippet:
            score += 8

    score += min(int(getattr(item, "views_count", 0) / 25), 12)
    score += min(int(getattr(item, "likes_count", 0) / 10), 8)
    return score


def perform_ai_search(query: str, *, content_type: str = "all", limit: int = 18, use_ai_intent: bool = True) -> dict:
    cleaned_query = normalize_text(query, limit=240)
    if len(cleaned_query) < 2:
        return {
            "query": cleaned_query,
            "intent": heuristic_search_intent(cleaned_query),
            "results": [],
            "grouped_objects": {"poetry": [], "blog": [], "video": [], "novel": [], "story": [], "quote": [], "author": []},
        }

    intent = parse_search_intent(cleaned_query) if use_ai_intent else heuristic_search_intent(cleaned_query)
    requested_type = content_type if content_type in AI_SEARCH_CONTENT_TYPES else "all"
    if requested_type == "all":
        requested_type = intent.get("content_type") or "all"
    if requested_type not in AI_SEARCH_CONTENT_TYPES:
        requested_type = "all"

    content_types = ["poetry", "blog", "video", "novel", "story", "quote", "author"]
    if requested_type != "all":
        content_types = [requested_type]

    ranked_results = []
    for item_type in content_types:
        for item in _build_search_candidates(item_type, cleaned_query, intent.get("author", "")):
            score = _score_search_item(
                item,
                requested_type=requested_type,
                intent=intent,
                query=cleaned_query,
            )
            if score <= 0:
                continue
            ranked_results.append(
                {
                    "object": item,
                    "content_type": item_type,
                    "content_type_label": item_type.title(),
                    "title": resolve_item_title(item),
                    "snippet": resolve_item_snippet(item),
                    "author": normalize_text(
                        getattr(getattr(item, "author", None), "name", "") or getattr(item, "name", ""),
                        limit=120,
                    ),
                    "url": item.get_absolute_url(),
                    "image_url": resolve_item_image(item),
                    "score": score,
                }
            )

    deduped = []
    seen = set()
    for result in sorted(ranked_results, key=lambda item: (item["score"], item["title"]), reverse=True):
        key = (result["content_type"], result["object"].pk)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(result)
        if len(deduped) >= limit:
            break

    grouped_objects = {"poetry": [], "blog": [], "video": [], "novel": [], "story": [], "quote": [], "author": []}
    for result in deduped:
        grouped_objects[result["content_type"]].append(result["object"])

    return {
        "query": cleaned_query,
        "intent": intent,
        "results": deduped,
        "grouped_objects": grouped_objects,
    }


def get_ai_search_suggestions(query: str, *, limit: int = 8) -> list[dict]:
    cleaned_query = normalize_text(query, limit=120)
    if len(cleaned_query) < 2:
        return []

    suggestions = []
    for author in Author.objects.filter(
        Q(name__icontains=cleaned_query),
        is_active=True,
    )[:2]:
        suggestions.append(
            {
                "label": author.name,
                "type": "Author",
                "subtitle": "Writer profile",
                "url": author.get_absolute_url(),
                "source": "classic",
            }
        )

    for poem in Poetry.objects.filter(
        Q(title__icontains=cleaned_query) | Q(author__name__icontains=cleaned_query),
        is_published=True,
    ).select_related("author")[:2]:
        suggestions.append(
            {
                "label": poem.title,
                "type": "Poetry",
                "subtitle": poem.author.name,
                "url": poem.get_absolute_url(),
                "source": "classic",
            }
        )

    for novel in Novel.objects.filter(
        Q(title__icontains=cleaned_query) | Q(author__name__icontains=cleaned_query),
        is_published=True,
    ).select_related("author")[:2]:
        suggestions.append(
            {
                "label": novel.title,
                "type": "Novel",
                "subtitle": novel.author.name,
                "url": novel.get_absolute_url(),
                "source": "classic",
            }
        )

    for post in BlogPost.objects.filter(
        Q(title__icontains=cleaned_query) | Q(author__name__icontains=cleaned_query),
        is_published=True,
    ).select_related("author")[:2]:
        suggestions.append(
            {
                "label": post.title,
                "type": "Blog",
                "subtitle": post.author.name,
                "url": post.get_absolute_url(),
                "source": "classic",
            }
        )

    for quote in Quote.objects.filter(
        Q(text__icontains=cleaned_query) | Q(author__name__icontains=cleaned_query),
        is_published=True,
    ).select_related("author")[:2]:
        suggestions.append(
            {
                "label": resolve_item_title(quote),
                "type": "Quote",
                "subtitle": quote.author.name,
                "url": quote.get_absolute_url(),
                "source": "classic",
            }
        )

    for video in Video.objects.filter(
        Q(title__icontains=cleaned_query) | Q(description__icontains=cleaned_query),
        is_published=True,
    )[:2]:
        suggestions.append(
            {
                "label": video.title,
                "type": "Video",
                "subtitle": "Watch now",
                "url": video.get_absolute_url(),
                "source": "classic",
            }
        )

    ai_payload = perform_ai_search(cleaned_query, limit=max(4, limit // 2), use_ai_intent=False)
    for result in ai_payload["results"]:
        suggestions.append(
            {
                "label": result["title"],
                "type": result["content_type_label"],
                "subtitle": result["author"] or result["snippet"][:60] or "AI search result",
                "url": result["url"],
                "source": "ai",
            }
        )

    deduped = []
    seen = set()
    for item in suggestions:
        key = (item.get("url"), item.get("label"))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
        if len(deduped) >= limit:
            break
    return deduped


def suggestion_seed_from_payload(payload: dict) -> list[str]:
    results = payload.get("results", [])
    return [item["title"] for item in results[:3]]
