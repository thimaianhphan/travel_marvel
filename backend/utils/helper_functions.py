"""
Helper functions for backend utilities.
"""

import logging
from typing import List, Tuple
import math

# -------------------------
# Functions for ORS route handling
# -------------------------

def _to_lonlat_list(latlng_points):
    # input points are (lat, lng); APIs want [lon,lat]
    return [[lng, lat] for (lat, lng) in latlng_points]


def _decode_polyline(polyline_str: str) -> List[List[float]]:
    """
    Decode Google/ORS polyline encoded string to list of [lon, lat] coordinates.
    
    Polyline encoding algorithm: https://developers.google.com/maps/documentation/utilities/polylinealgorithm
    """
    if not polyline_str:
        return []
    
    try:
        coords = []
        index = 0
        lat = 0
        lon = 0
        
        while index < len(polyline_str):
            # Decode latitude
            shift = 0
            result = 0
            while True:
                b = ord(polyline_str[index]) - 63
                index += 1
                result |= (b & 0x1f) << shift
                shift += 5
                if b < 0x20:
                    break
            dlat = ~(result >> 1) if (result & 1) != 0 else (result >> 1)
            lat += dlat
            
            # Decode longitude
            shift = 0
            result = 0
            while True:
                b = ord(polyline_str[index]) - 63
                index += 1
                result |= (b & 0x1f) << shift
                shift += 5
                if b < 0x20:
                    break
            dlon = ~(result >> 1) if (result & 1) != 0 else (result >> 1)
            lon += dlon
            
            coords.append([lon / 1e5, lat / 1e5])
        
        return coords
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to decode polyline: {e}")
        return []

def _stitch_routes(route_segments, max_routes=5):
    """
    Stitch together route segments into complete routes.
    route_segments: list of lists, where each inner list contains routes for one segment
    max_routes: maximum number of complete routes to generate
    Returns: list of complete stitched routes (limited to max_routes)
    """
    if not route_segments:
        return []
    
    # Strategy: Create routes by varying one segment at a time
    # Start with best route (first) for all segments
    base_route = []
    for segment_routes in route_segments:
        if segment_routes:
            segment_route = segment_routes[0]
            if base_route:
                # Remove duplicate point if last point matches first of segment
                if (abs(base_route[-1][0] - segment_route[0][0]) < 1e-6 and
                    abs(base_route[-1][1] - segment_route[0][1]) < 1e-6):
                    base_route.extend(segment_route[1:])
                else:
                    base_route.extend(segment_route)
            else:
                base_route.extend(segment_route)
    
    complete_routes = [base_route]
    
    # Generate variations by changing one segment at a time
    for seg_idx, segment_routes in enumerate(route_segments):
        if len(segment_routes) > 1 and len(complete_routes) < max_routes:
            # Create a route with this segment varied
            for alt_route in segment_routes[1:]:  # Skip first (already used in base)
                if len(complete_routes) >= max_routes:
                    break
                
                # Build route with this segment alternative
                stitched = []
                for i, seg_routes in enumerate(route_segments):
                    if i == seg_idx:
                        route_to_use = alt_route
                    else:
                        route_to_use = seg_routes[0]  # Use first route for other segments
                    
                    if stitched:
                        if (abs(stitched[-1][0] - route_to_use[0][0]) < 1e-6 and
                            abs(stitched[-1][1] - route_to_use[0][1]) < 1e-6):
                            stitched.extend(route_to_use[1:])
                        else:
                            stitched.extend(route_to_use)
                    else:
                        stitched.extend(route_to_use)
                
                complete_routes.append(stitched)
    
    return complete_routes[:max_routes]

# -------------------------
# POI helper functions (discovery, scoring, etc.) can be added here
# -------------------------
def calculate_bbox(center_lat: float, center_lon: float, radius_km: float) -> Tuple[float, float, float, float]:
    """
    Calculate bounding box around a center point.
    Returns: (min_lat, min_lon, max_lat, max_lon)
    """
    # Approximate: 1 degree lat ≈ 111 km, 1 degree lon ≈ 111 km * cos(lat)
    lat_delta = radius_km / 111.0
    lon_delta = radius_km / (111.0 * math.cos(math.radians(center_lat)))
    
    return (
        center_lat - lat_delta,
        center_lon - lon_delta,
        center_lat + lat_delta,
        center_lon + lon_delta
    )


def distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points in kilometers (Haversine formula)."""
    R = 6371.0  # Earth radius in km
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (
        math.sin(dlat / 2) ** 2 +
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
        math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c