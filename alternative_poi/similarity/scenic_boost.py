from typing import Dict, Tuple
from diskcache import Cache
from .config import COPERNICUS_EUDEM_WMS, COPERNICUS_TOKEN, USER_AGENT
import requests

CACHE = Cache("./.cache/faiss")

def _http_get(url: str, params: Dict) -> bytes | None:
    try:
        r = requests.get(url, params=params, headers={"User-Agent": USER_AGENT}, timeout=20)
        if r.ok: return r.content
    except Exception:
        return None
    return None

def copernicus_relief_boost(lat: float, lon: float) -> float:
    if not COPERNICUS_EUDEM_WMS: return 0.0
    params = {
        "SERVICE":"WMS","REQUEST":"GetMap","VERSION":"1.3.0","LAYERS":"EUDEM","CRS":"EPSG:4326",
        "BBOX":f"{lat-0.02},{lon-0.02},{lat+0.02},{lon+0.02}","WIDTH":"128","HEIGHT":"128",
        "FORMAT":"image/png","AUTH":COPERNICUS_TOKEN or "",
    }
    key = ("COP_TILE", COPERNICUS_EUDEM_WMS, tuple(sorted(params.items())))
    if key in CACHE: return 0.1
    content = _http_get(COPERNICUS_EUDEM_WMS, params)
    if content and len(content) > 1000:
        CACHE.set(key, True, expire=7*86400)
        return 0.1
    return 0.0

def protected_area_boost(tags: Dict) -> float:
    k = lambda t: (t or "").lower()
    if k(tags.get("boundary")) == "protected_area" or k(tags.get("protect_class")) or "national_park" in k(tags.get("leisure")):
        return 0.05
    return 0.0

def scenic_boost(poi: Dict) -> float:
    lat, lon = float(poi["lat"]), float(poi["lon"])
    b = 0.0
    b += copernicus_relief_boost(lat, lon)
    b += protected_area_boost(poi.get("tags") or {})
    return min(0.3, max(0.0, b))
