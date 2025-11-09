"""
Route Safety Functions

Functions to ensure POIs are properly filtered, ordered, and validated
to guarantee routes always go from A to B.
"""

import logging
from typing import List, Tuple

from backend.models.poi import PointOfInterest
from .helper_functions import distance_km

logger = logging.getLogger(__name__)


def point_to_line_distance_km(
    px: float, py: float,
    x1: float, y1: float,
    x2: float, y2: float
) -> Tuple[float, float]:
    """
    Calculate perpendicular distance from point to line segment (in km).
    Also returns the position along the line (0.0 to 1.0) where the closest point is.
    
    Returns:
        (distance_km, position_along_route) where position is 0.0 at start, 1.0 at end
    """
    import math
    
    # Convert to approximate km
    dx = (x2 - x1) * 111.0
    dy = (y2 - y1) * 111.0 * math.cos(math.radians((y1 + y2) / 2))
    dpx = (px - x1) * 111.0
    dpy = (py - y1) * 111.0 * math.cos(math.radians((y1 + py) / 2))
    
    # Line segment length squared
    line_len_sq = dx * dx + dy * dy
    
    if line_len_sq < 1e-10:  # Points are the same
        dist = math.sqrt(dpx * dpx + dpy * dpy)
        return dist, 0.0
    
    # Project point onto line
    t = max(0, min(1, (dpx * dx + dpy * dy) / line_len_sq))
    
    # Closest point on line
    closest_x = x1 + t * (x2 - x1)
    closest_y = y1 + t * (y2 - y1)
    
    # Distance from POI to closest point
    dist_km = distance_km(px, py, closest_x, closest_y)
    return dist_km, t


def filter_pois_near_route(
    pois: List[PointOfInterest],
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
    max_distance_km: float
) -> List[PointOfInterest]:
    """
    Filter POIs to only those reasonably close to the route.
    Also annotates POIs with distance and position along route.
    """
    filtered = []
    
    for poi in pois:
        # Calculate perpendicular distance from POI to route line
        distance, position = point_to_line_distance_km(
            poi.lat, poi.lon,
            start_lat, start_lon,
            end_lat, end_lon
        )
        
        if distance <= max_distance_km:
            poi.distance_from_route_km = distance
            poi.position_along_route = position
            filtered.append(poi)
    
    return filtered


def order_pois_along_route(pois: List[PointOfInterest]) -> List[PointOfInterest]:
    """
    Order POIs by their position along the A→B route.
    This ensures waypoints are visited in the correct order.
    """
    # Filter out POIs without position data
    valid_pois = [p for p in pois if p.position_along_route is not None]
    
    # Sort by position along route (0.0 = start, 1.0 = end)
    valid_pois.sort(key=lambda p: p.position_along_route)
    
    return valid_pois


def estimate_route_detour_km(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
    pois: List[PointOfInterest]
) -> float:
    """
    Estimate how much longer the route will be with POI waypoints.
    This is a rough estimate: sum of distances between consecutive waypoints.
    """
    if not pois:
        return 0.0
    
    # Build waypoint sequence: start → POIs (ordered) → end
    waypoints = [(start_lat, start_lon)]
    for poi in pois:
        waypoints.append((poi.lat, poi.lon))
    waypoints.append((end_lat, end_lon))
    
    # Calculate total distance
    total_distance = 0.0
    for i in range(len(waypoints) - 1):
        total_distance += distance_km(
            waypoints[i][0], waypoints[i][1],
            waypoints[i+1][0], waypoints[i+1][1]
        )
    
    # Compare to direct distance
    direct_distance = distance_km(start_lat, start_lon, end_lat, end_lon)
    detour = total_distance - direct_distance
    
    return detour


def deduplicate_pois(pois: List[PointOfInterest], distance_threshold_m: float = 100) -> List[PointOfInterest]:
    """Remove duplicate POIs that are very close to each other."""
    if not pois:
        return []
    
    # Convert threshold to degrees (approximate)
    threshold_deg = distance_threshold_m / 111000.0
    
    unique_pois = []
    seen = set()
    
    for poi in pois:
        # Round coordinates to threshold precision
        key = (
            round(poi.lat / threshold_deg),
            round(poi.lon / threshold_deg)
        )
        
        if key not in seen:
            seen.add(key)
            unique_pois.append(poi)
    
    return unique_pois


def check_progressive_approach(
    pois: List[PointOfInterest],
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
    tolerance_km: float = 1.0  # Allow small backward movements (e.g., 1km)
) -> bool:
    """
    Check if POIs follow a progressive approach to destination.
    
    Each POI should be closer to the destination than the previous one
    (with a small tolerance for minor detours).
    
    Args:
        pois: List of POIs in order
        start_lat: Start latitude
        start_lon: Start longitude
        end_lat: End latitude
        end_lon: End longitude
        tolerance_km: Allow backward movement up to this distance (default: 1km)
    
    Returns:
        True if POIs progressively approach destination, False otherwise
    """
    if not pois:
        return True
    
    # Calculate distance from start to destination
    current_distance = distance_km(start_lat, start_lon, end_lat, end_lon)
    
    for poi in pois:
        # Calculate distance from this POI to destination
        poi_distance = distance_km(poi.lat, poi.lon, end_lat, end_lon)
        
        # Check if this POI is closer to destination (with tolerance)
        # Allow small backward movements (e.g., to visit a nearby POI)
        if poi_distance > current_distance + tolerance_km:
            return False
        
        # Update current distance (allow some backward movement)
        current_distance = min(current_distance, poi_distance + tolerance_km)
    
    return True


def filter_progressive_pois(
    pois: List[PointOfInterest],
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
    tolerance_km: float = 1.0
) -> List[PointOfInterest]:
    """
    Filter POIs to ensure progressive approach to destination.
    
    Only keeps POIs that move progressively closer to the destination.
    This allows unlimited detours as long as each step gets closer.
    
    Args:
        pois: List of POIs (should be ordered along route)
        start_lat: Start latitude
        start_lon: Start longitude
        end_lat: End latitude
        end_lon: End longitude
        tolerance_km: Allow backward movement up to this distance
    
    Returns:
        Filtered list of POIs that progressively approach destination
    """
    if not pois:
        return []
    
    # Calculate initial distance from start to destination
    current_distance = distance_km(start_lat, start_lon, end_lat, end_lon)
    
    filtered = []
    for poi in pois:
        # Calculate distance from this POI to destination
        poi_distance = distance_km(poi.lat, poi.lon, end_lat, end_lon)
        
        # Keep POI if it's closer to destination (with tolerance)
        if poi_distance <= current_distance + tolerance_km:
            filtered.append(poi)
            # Update current distance (allow some backward movement)
            current_distance = min(current_distance, poi_distance + tolerance_km)
    
    return filtered