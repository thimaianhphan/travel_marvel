"""
Copernicus EU-DEM helper for assessing surrounding relief.
"""

from __future__ import annotations

from typing import Optional

import requests

from backend.services.alternatives_discovery.config import (
    COPERNICUS_EUDEM_WMTS,
    COPERNICUS_TOKEN,
    REQUEST_USER_AGENT,
)
from .http_cache import HTTP_CACHE


def relief_is_steep(lat: float, lon: float) -> bool:
    """
    Heuristic: request a small DEM tile and treat data presence as indicator of relief.

    The original prototype simply checked if the request succeeded and cached the boolean.
    We keep that behaviour for the MVP to avoid heavy raster processing during the hackathon.
    """

    if not COPERNICUS_EUDEM_WMTS:
        return False

    params = {
        "SERVICE": "WMTS",
        "REQUEST": "GetMap",
        "VERSION": "1.3.0",
        "LAYERS": "EUDEM",
        "CRS": "EPSG:4326",
        "BBOX": f"{lat-0.02},{lon-0.02},{lat+0.02},{lon+0.02}",
        "WIDTH": "128",
        "HEIGHT": "128",
        "FORMAT": "image/png",
        "AUTH": COPERNICUS_TOKEN or "",
    }

    cache_key = ("COPERNICUS_TILE", COPERNICUS_EUDEM_WMTS, tuple(sorted(params.items())))
    cached = HTTP_CACHE.get(cache_key)
    if cached is not None:
        return bool(cached)

    try:
        response = requests.get(
            COPERNICUS_EUDEM_WMTS,
            params=params,
            headers={"User-Agent": REQUEST_USER_AGENT},
            timeout=20,
        )
        if response.ok and len(response.content) > 1000:
            HTTP_CACHE.set(cache_key, True, expire=7 * 24 * 60 * 60)
            return True
    except Exception:
        pass

    HTTP_CACHE.set(cache_key, False, expire=24 * 60 * 60)
    return False


__all__ = ["relief_is_steep"]

