from typing import Optional
from .cache_http import CACHE
from .config import COPERNICUS_EUDEM_WMTS, COPERNICUS_TOKEN, USER_AGENT
import requests

def relief_is_steep(lat: float, lon: float) -> bool:
    if not COPERNICUS_EUDEM_WMTS:
        return False
    try:
        params = {
            "SERVICE":"WMTS","REQUEST":"GetMap","VERSION":"1.3.0","LAYERS":"EUDEM","CRS":"EPSG:4326",
            "BBOX":f"{lat-0.02},{lon-0.02},{lat+0.02},{lon+0.02}","WIDTH":"128","HEIGHT":"128",
            "FORMAT":"image/png","AUTH":COPERNICUS_TOKEN or "",
        }
        key = ("COPERNICUS_TILE", COPERNICUS_EUDEM_WMTS, tuple(sorted(params.items())))
        if key in CACHE: return True
        r = requests.get(COPERNICUS_EUDEM_WMTS, params=params, headers={"User-Agent": USER_AGENT}, timeout=20)
        if r.ok and len(r.content) > 1000:
            CACHE.set(key, True, expire=7*86400)
            return True
    except Exception:
        pass
    return False
