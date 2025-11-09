"""
Utility helpers to turn POI metadata into descriptive text snippets.
"""

from __future__ import annotations

from typing import Dict

from diskcache import Cache

from .config import FAISS_CACHE_DIR

NOISY_TAGS = {
    "source",
    "check_date",
    "wikidata",
    "website",
    "image",
    "note",
    "start_date",
    "operator",
    "phone",
    "contact:phone",
    "contact:website",
    "email",
    "addr:full",
}

_TEXT_CACHE_DIR = FAISS_CACHE_DIR / "text"
_TEXT_CACHE_DIR.mkdir(parents=True, exist_ok=True)
TEXT_CACHE = Cache(str(_TEXT_CACHE_DIR))


def poi_text(data: Dict) -> str:
    """
    Build a normalized description string combining category, tags and narrative text.
    """
    cache_key = ("POI_TEXT", data.get("name"), data.get("category"), tuple(sorted((data.get("tags") or {}).items())))
    if cache_key in TEXT_CACHE:
        return TEXT_CACHE[cache_key]

    category = (data.get("category") or "unknown").lower()
    tags = data.get("tags") or {}
    tag_text = "; ".join(f"{key}={value}" for key, value in tags.items() if key not in NOISY_TAGS)

    description = (data.get("desc") or "").strip()
    if not description:
        defaults = {
            "lake": "clear waters, forest-lined shores, alpine setting",
            "waterfall": "vertical drop, rocky gorge, steady plunge",
            "beach": "sandy shore, gentle surf, unspoiled feel",
            "viewpoint": "elevated panorama, distant peaks, wide vistas",
            "park": "protected nature, woodland trails, quiet atmosphere",
            "castle": "historic walls, hilltop site, scenic surroundings",
            "church": "landmark spire, heritage architecture, scenic setting",
            "museum": "regional heritage, curated exhibits, cultural focus",
            "unknown": "scenic natural site, tranquil setting",
        }
        description = defaults.get(category, "scenic natural site, tranquil setting")

    text = f"[CATEGORY: {category}] [TAGS: {tag_text}] — {description}".strip().lower()
    TEXT_CACHE.set(cache_key, text, expire=30 * 24 * 60 * 60)
    return text


__all__ = ["poi_text"]

