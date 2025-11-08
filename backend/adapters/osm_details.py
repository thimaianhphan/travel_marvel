"""
Utilities for fetching detailed OSM tags via Overpass when a feature ID is known.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from services.poi_discovery.config import OVERPASS_URLS
from .osm import _is_overpass_available
from .http_cache import cached_post


OSM_TYPE_MAP = {"N": "node", "W": "way", "R": "relation"}


def fetch_tags(osm_type: str, osm_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetch tag dictionary for the given OSM feature.

    Args:
        osm_type: Single-letter type identifier as returned by Nominatim (N/W/R).
        osm_id: Numeric OSM identifier.
    """
    kind = OSM_TYPE_MAP.get(osm_type.upper())
    if not kind:
        raise ValueError(f"Unsupported OSM type: {osm_type!r}")

    query = f"[out:json][timeout:25]; {kind}({osm_id}); out tags;"
    for idx, url in enumerate(OVERPASS_URLS):
        if not _is_overpass_available(url, timeout=25):
            continue
        try:
            payload = cached_post(url, {"data": query})
        except Exception:
            if idx == len(OVERPASS_URLS) - 1:
                raise
            continue
        elements = payload.get("elements", [])
        if elements:
            for element in elements:
                tags = element.get("tags")
                if tags:
                    return tags
    return {}


__all__ = ["fetch_tags"]

