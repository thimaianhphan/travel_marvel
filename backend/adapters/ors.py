"""
Adapter for OpenRouteService
"""
import json
import requests
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env
ORS_BASE = os.getenv('ORS_BASE')
ORS_KEY = os.getenv('ORS_KEY')

from utils.helper_functions import _decode_polyline, _to_lonlat_list
# -------------------------
# Route generation via OpenRouteService API
# -------------------------
def ors_route(latlng_points, profile="foot-walking", ask_alternatives=3):
    """
    Returns: list of routes, each as list[[lon,lat], ...]
    - If exactly 2 points: requests up to `ask_alternatives` alternatives (subject to service limits).
    - If >2 points: ORS returns routes following all waypoints, but may only return 1 route.
    """
    coords = _to_lonlat_list(latlng_points)
    body = {
        "coordinates": coords,
        "instructions": False,
        "format": "geojson",
    }
    
    # Only request alternatives for 2-point routes (ORS limitation)
    if len(latlng_points) == 2 and ask_alternatives > 1:
        body["alternative_routes"] = {
            "target_count": int(ask_alternatives),
            "share_factor": 0.2,  # How much overlap is allowed (smaller = more different routes)
            "weight_factor": 3,  # How much worse can an alternative be (larger = more diverse routes, including less efficient scenic ones)
        }
    
    # Prefer the base directions endpoint and request GeoJSON via body; fallback to /geojson if needed
    url_primary = f"{ORS_BASE}/v2/directions/{profile}"
    url_fallback = f"{ORS_BASE}/v2/directions/{profile}/geojson"
    headers = {"Authorization": ORS_KEY, "Content-Type": "application/json"}
    
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        r = requests.post(url_primary, headers=headers, json=body, timeout=30)
        if r.status_code == 404:
            logger.warning("ORS directions 404 on primary endpoint, retrying '/geojson' path")
            r = requests.post(url_fallback, headers=headers, json=body, timeout=30)
        r.raise_for_status()
        data = r.json()
        
        # Check for API errors in response
        if "error" in data:
            error_msg = data.get("error", {}).get("message", str(data.get("error", "Unknown error")))
            logger.error("ORS API error: %s", error_msg)
            raise RuntimeError(f"ORS API error: {error_msg}")
        
        routes = []
        
        # Handle GeoJSON format (features array)
        feats = data.get("features") or []
        if feats:
            routes = [feat["geometry"]["coordinates"] for feat in feats]
        # Handle routes array format (with encoded polyline geometry)
        elif "routes" in data:
            routes_list = data.get("routes") or []
            for route in routes_list:
                geom = route.get("geometry")
                if isinstance(geom, str):
                    # Encoded polyline - decode it
                    coords = _decode_polyline(geom)
                    if coords:
                        routes.append(coords)
                elif isinstance(geom, dict) and "coordinates" in geom:
                    # Already GeoJSON coordinates
                    routes.append(geom["coordinates"])
                elif isinstance(geom, list):
                    # Already a coordinate list
                    routes.append(geom)
        
        if not routes:
            logger.warning("ORS returned no routes in response: %s", json.dumps(data)[:200])
            raise RuntimeError(f"ORS: no routes in response: {json.dumps(data)[:200]}")
        
        logger.info("ORS returned %d route(s) for %d waypoints", len(routes), len(latlng_points))
        return routes
    except requests.exceptions.RequestException as e:
        logger.exception("ORS API request failed: %s", e)
        raise RuntimeError(f"Failed to fetch routes from ORS: {str(e)}") from e