"""Utilities for Urdu poetry text-to-speech generation."""

import asyncio
import hashlib
from pathlib import Path

from django.conf import settings
from django.utils.text import slugify


def get_tts_engine_priority():
    preferred = str(getattr(settings, "POETRY_TTS_ENGINE", "edge")).lower().strip()
    candidates = [preferred]
    if preferred != "edge":
        candidates.append("edge")
    if preferred != "gtts":
        candidates.append("gtts")
    return [name for name in candidates if name in {"edge", "gtts"}]


def build_audio_cache_path(cache_key, text, engine):
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
    normalized_key = slugify(str(cache_key or "audio")) or "audio"
    filename = f"{normalized_key}-{engine}-{digest}.mp3"
    folder = Path(settings.MEDIA_ROOT) / "tts"
    folder.mkdir(parents=True, exist_ok=True)
    absolute_path = folder / filename
    media_url = settings.MEDIA_URL.rstrip("/")
    audio_url = f"{media_url}/tts/{filename}"
    return absolute_path, audio_url


def _run_edge_tts(text, output_path):
    import edge_tts

    voice = getattr(settings, "POETRY_TTS_EDGE_VOICE", "ur-PK-AsadNeural")

    async def _generate():
        communicator = edge_tts.Communicate(text=text, voice=voice)
        await communicator.save(str(output_path))

    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(_generate())
    finally:
        loop.close()


def _run_gtts(text, output_path):
    from gtts import gTTS

    tld = getattr(settings, "POETRY_TTS_GTTS_TLD", "com")
    speaker = gTTS(text=text, lang="ur", tld=tld, slow=False)
    speaker.save(str(output_path))


def generate_tts_audio(*, text, cache_key="audio", poem_id=None):
    """
    Generate and cache an MP3 for poetry text.
    Returns: (audio_url, engine_used)
    """
    if poem_id is not None and cache_key == "audio":
        cache_key = f"poetry-{poem_id}"

    errors = []
    for engine in get_tts_engine_priority():
        path, url = build_audio_cache_path(cache_key=cache_key, text=text, engine=engine)
        if path.exists() and path.stat().st_size > 0:
            return url, engine

        try:
            if engine == "edge":
                _run_edge_tts(text=text, output_path=path)
            elif engine == "gtts":
                _run_gtts(text=text, output_path=path)
            else:
                continue

            if path.exists() and path.stat().st_size > 0:
                return url, engine
            errors.append(f"{engine}: no audio file generated")
        except Exception as exc:  # pragma: no cover - runtime dependency branch
            errors.append(f"{engine}: {exc}")

    raise RuntimeError("TTS generation failed. " + " | ".join(errors))
