from typing import Dict, Optional
from .cache_http import cached_get, cached_post
from .config import NOMINATIM, OVERPASS

def nominatim_lookup(name: str, limit: int = 1):
    params = {"q": name, "format": "jsonv2", "limit": limit, "addressdetails": 0, "extratags": 1, "namedetails": 1}
    return cached_get(NOMINATIM, params=params)

def overpass_tags(osm_type: str, osm_id: int) -> Optional[Dict]:
    kind = {"N": "node", "W": "way", "R": "relation"}[osm_type]
    query = f"[out:json][timeout:25]; {kind}({osm_id}); out tags;"
    data = cached_post(OVERPASS, {"data": query})
    for el in data.get("elements", []):
        if el.get("tags"):
            return el["tags"]
    return {}
