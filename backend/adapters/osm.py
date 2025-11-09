"""
Adapter with OpenStreetMap for POI Discovery

Functions for discovering POIs from OpenStreetMap using the Overpass API.
"""
import logging
from typing import Any, Dict, List, Optional, Tuple

import requests

from backend.models.poi import PointOfInterest
from backend.services.poi_discovery.config import OVERPASS_TIMEOUT, OVERPASS_URLS
from backend.utils.helper_functions import calculate_bbox

logger = logging.getLogger(__name__)


def _is_overpass_available(url: str, timeout: int) -> bool:
    try:
        heartbeat = requests.get(
            url,
            params={"data": "[out:json][timeout:5];node(0,0,0,0);out;"},
            timeout=min(timeout, 5),
        )
        heartbeat.raise_for_status()
        return True
    except requests.RequestException:
        return False


def query_overpass(query: str, timeout: int = OVERPASS_TIMEOUT) -> Dict:
    """Execute an Overpass API query with endpoint rotation and health checks."""
    last_error: Optional[Exception] = None
    for idx, url in enumerate(OVERPASS_URLS):
        if not _is_overpass_available(url, timeout):
            logger.debug("Skipping Overpass endpoint %s (health check failed)", url)
            continue
        try:
            response = requests.post(
                url,
                data=query,
                headers={"Content-Type": "text/plain"},
                timeout=timeout,
            )
            response.raise_for_status()
            payload = response.json()
            elements = payload.get("elements", [])
            if elements:
                if idx > 0:
                    logger.info(
                        "Overpass fallback succeeded on endpoint %s after %d retries",
                        url,
                        idx,
                    )
                return payload
            logger.warning(
                "Overpass endpoint %s returned 0 elements. Trying next endpoint (%d/%d).",
                url,
                idx + 1,
                len(OVERPASS_URLS),
            )
            if idx == len(OVERPASS_URLS) - 1:
                return payload
        except requests.exceptions.RequestException as exc:
            last_error = exc
            logger.warning(
                "Overpass endpoint %s failed (%s). Trying next endpoint (%d/%d).",
                url,
                exc,
                idx + 1,
                len(OVERPASS_URLS),
            )
    if last_error:
        logger.error("All Overpass endpoints failed: %s", last_error)
        raise RuntimeError(f"Failed to query Overpass API: {last_error}") from last_error
    return {"elements": []}


def classify_poi_type(tags: Dict[str, Any]) -> Optional[str]:
    """Classify POI type from OSM tags. Focus on scenic POIs, some cultural/historic."""
    # Viewpoints and observation points (high priority - scenic)
    if tags.get("tourism") == "viewpoint" or tags.get("amenity") == "viewpoint":
        return "viewpoint"
    
    # Water features (high priority - scenic)
    if tags.get("natural") in ["water", "lake", "pond", "reservoir", "bay"]:
        return "lake"
    if tags.get("waterway") in ["river", "stream", "canal", "riverbank"]:
        return "waterway"
    if tags.get("natural") == "riverbank" or tags.get("waterway") == "riverbank":
        return "waterway"
    
    # Parks and natural areas (high priority - scenic)
    if tags.get("leisure") in ["park", "nature_reserve", "garden"]:
        return "park"
    if tags.get("landuse") in ["forest", "recreation_ground", "village_green"]:
        return "park"
    if tags.get("boundary") == "national_park":
        return "park"
    
    # Mountains and peaks (high priority - scenic)
    if tags.get("natural") == "peak" or tags.get("mountain_pass"):
        return "peak"
    if tags.get("natural") == "ridge" or tags.get("natural") == "cliff":
        return "peak"
    
    # Beaches (high priority - scenic)
    if tags.get("natural") == "beach":
        return "beach"
    
    # Scenic routes and paths (high priority - scenic)
    if tags.get("route") in ["hiking", "bicycle", "scenic"]:
        return "scenic_route"
    if tags.get("route") == "ferry" and tags.get("scenic"):
        return "scenic_route"
    
    # Cultural and historical sites (lower priority, but include)
    if tags.get("historic") in ["monument", "memorial", "castle", "ruins", "tower", "archaeological_site"]:
        return "monument"
    if tags.get("amenity") == "place_of_worship" and tags.get("religion") in ["christian", "catholic", "protestant"]:
        # Cathedrals and churches
        if tags.get("building") == "cathedral" or "cathedral" in (tags.get("name", "") or "").lower():
            return "monument"
    
    # Attractions (lower priority)
    if tags.get("tourism") in ["attraction", "museum", "artwork", "gallery"]:
        return "attraction"
    
    return None


def parse_overpass_elements(elements: List[Dict]) -> List[PointOfInterest]:
    """Parse Overpass API response elements into POI objects."""
    pois = []
    
    for elem in elements:
        if elem.get("type") not in ["node", "way", "relation"]:
            continue
        
        tags = elem.get("tags", {})
        
        # Extract coordinates
        if elem["type"] == "node":
            lat = elem.get("lat")
            lon = elem.get("lon")
        elif "center" in elem:
            lat = elem["center"].get("lat")
            lon = elem["center"].get("lon")
        elif "geometry" in elem and elem["geometry"]:
            # For ways/relations, use first point or centroid
            first_point = elem["geometry"][0]
            lat = first_point.get("lat")
            lon = first_point.get("lon")
        else:
            continue
        
        if lat is None or lon is None:
            continue
        
        # Determine POI type from tags
        poi_type = classify_poi_type(tags)
        if not poi_type:
            continue
        
        # Extract name
        name = (
            tags.get("name") or 
            tags.get("name:en") or 
            tags.get("ref") or 
            f"{poi_type.title()} (unnamed)"
        )
        
        pois.append(PointOfInterest(
            name=name,
            lat=float(lat),
            lon=float(lon),
            poi_type=poi_type,
            source="osm",
            tags=tags
        ))
    
    return pois


def discover_osm_pois(
    center_lat: float,
    center_lon: float,
    radius_km: float = 10.0,
    poi_types: Optional[List[str]] = None,
    limit: Optional[int] = None  # Limit number of results for performance
) -> List[PointOfInterest]:
    """
    Discover POIs from OpenStreetMap using Overpass API.
    
    Args:
        center_lat: Center latitude
        center_lon: Center longitude
        radius_km: Search radius in kilometers
        poi_types: Optional list of POI types to filter (e.g., ["viewpoint", "lake"])
    
    Returns:
        List of POI objects
    """
    min_lat, min_lon, max_lat, max_lon = calculate_bbox(center_lat, center_lon, radius_km)
    
    # Build Overpass query
    # Query for nodes, ways, and relations with scenic tags
    # Note: We limit results after parsing for performance
    query = f"""
    [out:json][timeout:25];
    (
        // Viewpoints
        node["tourism"="viewpoint"]({min_lat},{min_lon},{max_lat},{max_lon});
        way["tourism"="viewpoint"]({min_lat},{min_lon},{max_lat},{max_lon});
        relation["tourism"="viewpoint"]({min_lat},{min_lon},{max_lat},{max_lon});
        
        // Water features
        node["natural"~"^(water|lake|pond|reservoir|bay)$"]({min_lat},{min_lon},{max_lat},{max_lon});
        way["natural"~"^(water|lake|pond|reservoir|bay)$"]({min_lat},{min_lon},{max_lat},{max_lon});
        relation["natural"~"^(water|lake|pond|reservoir|bay)$"]({min_lat},{min_lon},{max_lat},{max_lon});
        
        // Parks and natural areas
        node["leisure"~"^(park|nature_reserve|garden)$"]({min_lat},{min_lon},{max_lat},{max_lon});
        way["leisure"~"^(park|nature_reserve|garden)$"]({min_lat},{min_lon},{max_lat},{max_lon});
        relation["leisure"~"^(park|nature_reserve|garden)$"]({min_lat},{min_lon},{max_lat},{max_lon});
        
        // Historical and cultural sites
        node["historic"~"^(monument|memorial|castle|ruins|tower|archaeological_site)$"]({min_lat},{min_lon},{max_lat},{max_lon});
        way["historic"~"^(monument|memorial|castle|ruins|tower|archaeological_site)$"]({min_lat},{min_lon},{max_lat},{max_lon});
        relation["historic"~"^(monument|memorial|castle|ruins|tower|archaeological_site)$"]({min_lat},{min_lon},{max_lat},{max_lon});
        
        // Attractions
        node["tourism"~"^(attraction|museum|artwork|gallery)$"]({min_lat},{min_lon},{max_lat},{max_lon});
        way["tourism"~"^(attraction|museum|artwork|gallery)$"]({min_lat},{min_lon},{max_lat},{max_lon});
        relation["tourism"~"^(attraction|museum|artwork|gallery)$"]({min_lat},{min_lon},{max_lat},{max_lon});
        
        // Peaks and mountains
        node["natural"="peak"]({min_lat},{min_lon},{max_lat},{max_lon});
        way["natural"="peak"]({min_lat},{min_lon},{max_lat},{max_lon});
        relation["natural"="peak"]({min_lat},{min_lon},{max_lat},{max_lon});
        
        // Beaches
        node["natural"="beach"]({min_lat},{min_lon},{max_lat},{max_lon});
        way["natural"="beach"]({min_lat},{min_lon},{max_lat},{max_lon});
        relation["natural"="beach"]({min_lat},{min_lon},{max_lat},{max_lon});
        
        // Waterways and riversides (scenic)
        node["waterway"~"^(river|stream|canal|riverbank)$"]({min_lat},{min_lon},{max_lat},{max_lon});
        way["waterway"~"^(river|stream|canal|riverbank)$"]({min_lat},{min_lon},{max_lat},{max_lon});
        relation["waterway"~"^(river|stream|canal|riverbank)$"]({min_lat},{min_lon},{max_lat},{max_lon});
        node["natural"="riverbank"]({min_lat},{min_lon},{max_lat},{max_lon});
        way["natural"="riverbank"]({min_lat},{min_lon},{max_lat},{max_lon});
        
        // Scenic routes
        node["route"~"^(hiking|bicycle|scenic)$"]({min_lat},{min_lon},{max_lat},{max_lon});
        way["route"~"^(hiking|bicycle|scenic)$"]({min_lat},{min_lon},{max_lat},{max_lon});
        relation["route"~"^(hiking|bicycle|scenic)$"]({min_lat},{min_lon},{max_lat},{max_lon});
        
        // Mountains, ridges, cliffs
        node["natural"~"^(ridge|cliff)$"]({min_lat},{min_lon},{max_lat},{max_lon});
        way["natural"~"^(ridge|cliff)$"]({min_lat},{min_lon},{max_lat},{max_lon});
        relation["natural"~"^(ridge|cliff)$"]({min_lat},{min_lon},{max_lat},{max_lon});
        
        // Cathedrals and major churches
        node["amenity"="place_of_worship"]["building"="cathedral"]({min_lat},{min_lon},{max_lat},{max_lon});
        way["amenity"="place_of_worship"]["building"="cathedral"]({min_lat},{min_lon},{max_lat},{max_lon});
        relation["amenity"="place_of_worship"]["building"="cathedral"]({min_lat},{min_lon},{max_lat},{max_lon});
    );
    out center;
    """
    
    try:
        logger.info(f"Querying OSM for POIs near ({center_lat}, {center_lon}) within {radius_km}km")
        data = query_overpass(query)
        elements = data.get("elements", [])
        pois = parse_overpass_elements(elements)
        
        # Filter by POI types if specified
        if poi_types:
            pois = [p for p in pois if p.poi_type in poi_types]
        
        # Apply limit if specified (in case Overpass limit didn't work)
        if limit and len(pois) > limit:
            pois = pois[:limit]
        
        logger.info(f"Found {len(pois)} POIs from OSM")
        return pois
    
    except Exception as e:
        logger.error(f"Error discovering OSM POIs: {e}")
        return []