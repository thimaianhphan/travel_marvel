from typing import Dict
from diskcache import Cache

NOISY_TAGS = {
    "source","check_date","wikidata","website","image","note","start_date","operator","phone","contact:phone","contact:website","email","addr:full"
}
CACHE = Cache("./.cache/faiss")

def poi_text(p: Dict) -> str:
    cat = (p.get("category") or "unknown").lower()
    tags = p.get("tags") or {}
    tagkv = "; ".join(f"{k}={v}" for k, v in tags.items() if k not in NOISY_TAGS)
    desc = (p.get("desc") or "").strip()
    if not desc:
        defaults = {
            "lake": "clear waters, forest-lined shores, alpine setting",
            "waterfall": "vertical drop, rocky gorge, steady plunge",
            "beach": "sandy shore, gentle surf, unspoiled feel",
            "viewpoint": "elevated panorama, distant peaks, wide vistas",
            "park": "protected nature, woodland trails, quiet atmosphere",
            "castle": "historic walls, hilltop site, scenic surroundings",
            "church": "landmark spire, heritage architecture, scenic setting",
            "museum": "regional heritage, curated exhibits, cultural focus",
            "unknown": "scenic natural site, tranquil setting"
        }
        desc = defaults.get(cat, "scenic natural site, tranquil setting")
    return f"[CATEGORY: {cat}] [TAGS: {tagkv}] — {desc}".strip().lower()
