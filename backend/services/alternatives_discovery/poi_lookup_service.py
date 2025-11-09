"""
Name-based POI resolver using Nominatim + Overpass enrichment.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from backend.adapters.nominatim import best_match
from backend.adapters.osm_details import fetch_tags

from .lookup_category import infer_category
from .scenic_descriptions import generate_scenic_description, is_narrative


def resolve_one(name: str, hint: Optional[str] = None) -> Optional[Dict]:
    candidate = best_match(name)
    if not candidate:
        return None

    lat = float(candidate["lat"])
    lon = float(candidate["lon"])
    osm_type = candidate["osm_type"][0].upper()
    osm_id = int(candidate["osm_id"])
    tags = fetch_tags(osm_type, osm_id) or candidate.get("extratags", {}) or {}
    category = infer_category(tags, hint)

    raw_description = tags.get("description") or tags.get("note")
    scenic_description = generate_scenic_description(category, tags, lat, lon)
    if scenic_description and len(scenic_description.split()) >= 20:
        description = scenic_description
    elif is_narrative(raw_description):
        description = raw_description
    else:
        description = scenic_description or raw_description

    resolved_name = (
        candidate.get("namedetails", {}).get("name")
        or candidate["display_name"].split(",")[0]
    )

    return {
        "name": resolved_name,
        "lat": lat,
        "lon": lon,
        "category": category,
        "tags": tags,
        "desc": description,
    }


def batch_resolve(pois: List[Dict]) -> List[Optional[Dict]]:
    return [resolve_one(poi["name"], hint=poi.get("hint")) for poi in pois]


__all__ = ["resolve_one", "batch_resolve"]

