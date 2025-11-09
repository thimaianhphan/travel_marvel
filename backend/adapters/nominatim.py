"""
Thin wrapper around Nominatim search for name-based POI lookup.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from services.alternatives_discovery.config import NOMINATIM_SEARCH_URL
from .http_cache import cached_get


def search_place(
    name: str,
    *,
    limit: int = 5,
    address_details: int = 0,
    extratags: int = 1,
    namedetails: int = 1,
) -> List[Dict[str, Any]]:
    """
    Query Nominatim for the given name.

    Returns a list of candidate results (most relevant first).
    """
    params = {
        "q": name,
        "format": "jsonv2",
        "limit": limit,
        "addressdetails": address_details,
        "extratags": extratags,
        "namedetails": namedetails,
    }
    return cached_get(NOMINATIM_SEARCH_URL, params=params)


def best_match(name: str) -> Optional[Dict[str, Any]]:
    """
    Convenience helper returning the top search result (if any).
    """
    results = search_place(name, limit=1)
    return results[0] if results else None


__all__ = ["search_place", "best_match"]

