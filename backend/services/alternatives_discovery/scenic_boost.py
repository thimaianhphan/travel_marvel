"""
Simple heuristic scenic boost used during similarity scoring.

The goal is not to be perfect, but to provide a lightweight tie-breaker that
favours protected areas, steep relief and water features.
"""

from __future__ import annotations

from typing import Dict

from backend.adapters.copernicus import relief_is_steep


def scenic_boost(poi: Dict) -> float:
    tags = poi.get("tags") or {}
    category = (poi.get("category") or "unknown").lower()

    boost = 0.0
    boost += _category_boost(category)
    boost += _tag_boost(tags)
    boost += _protected_area_boost(tags)
    boost += _relief_boost(poi)

    return max(0.0, min(0.3, boost))


def _category_boost(category: str) -> float:
    category_weights = {
        "lake": 0.12,
        "waterfall": 0.12,
        "beach": 0.12,
        "viewpoint": 0.12,
        "park": 0.08,
    }
    return category_weights.get(category, 0.0)


def _tag_boost(tags: Dict) -> float:
    boost = 0.0
    natural_tag = (tags.get("natural") or "").lower()
    if natural_tag in {"water", "beach", "waterfall"}:
        boost += 0.05

    leisure_tag = (tags.get("leisure") or "").lower()
    if leisure_tag in {"nature_reserve", "park"}:
        boost += 0.04

    return boost


def _protected_area_boost(tags: Dict) -> float:
    boundary = (tags.get("boundary") or "").lower()
    protect_class = (tags.get("protect_class") or "").lower()
    leisure = (tags.get("leisure") or "").lower()
    protection_title = (tags.get("protection_title") or "").lower()

    if boundary == "protected_area":
        return 0.05
    if protect_class:
        return 0.05
    if "national_park" in leisure:
        return 0.05
    if protection_title:
        return 0.05
    return 0.0


def _relief_boost(poi: Dict) -> float:
    try:
        lat = float(poi["lat"])
        lon = float(poi["lon"])
    except (KeyError, TypeError, ValueError):
        return 0.0

    return 0.1 if relief_is_steep(lat, lon) else 0.0


__all__ = ["scenic_boost"]

