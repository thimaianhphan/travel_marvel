"""
Simple heuristic scenic boost used during similarity scoring.

The goal is not to be perfect, but to provide a lightweight tie-breaker that
favours protected areas, steep relief and water features.
"""

from __future__ import annotations

from typing import Dict

from adapters.copernicus import relief_is_steep


def scenic_boost(poi: Dict) -> float:
    tags = poi.get("tags") or {}
    category = (poi.get("category") or "unknown").lower()

    boost = 0.0
    if category in {"lake", "waterfall", "beach", "viewpoint"}:
        boost += 0.12
    if category in {"park"}:
        boost += 0.08

    if tags.get("boundary") == "protected_area" or tags.get("protect_class"):
        boost += 0.07
    if tags.get("natural") in {"water", "beach", "waterfall"}:
        boost += 0.05
    if tags.get("leisure") in {"nature_reserve", "park"}:
        boost += 0.04

    try:
        lat = float(poi.get("lat"))
        lon = float(poi.get("lon"))
    except (TypeError, ValueError):
        lat = lon = None

    if lat is not None and lon is not None and relief_is_steep(lat, lon):
        boost += 0.05

    return max(0.0, min(0.3, boost))


__all__ = ["scenic_boost"]

