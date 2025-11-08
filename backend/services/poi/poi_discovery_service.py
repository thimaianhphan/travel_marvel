"""
Main POI Discovery Functions

Orchestrates POI discovery from multiple sources and applies route safety filters.
"""

import logging
from typing import List, Optional

from models.poi import PointOfInterest
from adapters.osm import discover_osm_pois
from utils.poi_route_safety import (
    estimate_route_detour_km,
    deduplicate_pois,
    filter_progressive_pois,
    point_to_line_distance_km
)
from utils.helper_functions import distance_km

# Import ORS POIs (primary reliable source)
try:
    from adapters.ors import discover_ors_pois
    ORS_POIS_AVAILABLE = True
except ImportError:
    ORS_POIS_AVAILABLE = False
    discover_ors_pois = None

logger = logging.getLogger(__name__)


def discover_pois_along_route(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
    search_radius_km: Optional[float] = None,  # Auto-calculated based on distance
    max_pois: Optional[int] = None,  # Auto-calculated based on distance
    progressive_tolerance_km: float = 2.0,  # Allow small backward movements (2km)
    sources: Optional[List[str]] = None,
    prioritize_scenic: bool = True  # Prioritize POIs with scenic scores
) -> List[PointOfInterest]:
    """
    Discover scenic POIs in the area between two points, then route through them.
    
    This function:
    1. Discovers scenic POIs (viewpoints, lakes, mountains, riversides) in the area between A and B
    2. Includes some cultural/historic sites (monuments, cathedrals) with lower priority
    3. Orders POIs progressively: each POI must be closer to destination (allows unlimited detours)
    4. Prioritizes POIs with good scenic scores
    5. Returns POIs that will be used as waypoints: A → POI1 → POI2 → ... → B
    
    POI count is dynamic based on route distance (reduced for performance):
    - < 50km: 2 POIs
    - < 100km: 3 POIs
    - >= 100km: 5 POIs (max, roughly covers one German state)
    
    Args:
        start_lat: Start latitude
        start_lon: Start longitude
        end_lat: End latitude
        end_lon: End longitude
        search_radius_km: Search radius around midpoint (auto-calculated if None)
        max_pois: Maximum number of POIs to return (auto-calculated if None)
        progressive_tolerance_km: Allow backward movement up to this distance (default: 2km)
        sources: List of sources to use (["osm", "ors"]), None = all (defaults to OSM + ORS)
        prioritize_scenic: If True, prioritize POIs with higher scenic scores
    
    Returns:
        List of POI objects, ordered progressively toward destination, to be used as waypoints
    """
    if sources is None:
        # Default to reliable sources: OSM (via Overpass) and ORS POIs
        sources = ["osm", "ors"]
    
    # Calculate route midpoint and distance
    mid_lat = (start_lat + end_lat) / 2.0
    mid_lon = (start_lon + end_lon) / 2.0
    
    route_distance_km = distance_km(start_lat, start_lon, end_lat, end_lon)
    
    # Calculate max_pois based on distance (reduced for performance)
    if max_pois is None:
        if route_distance_km < 50:
            max_pois = 2  # Reduced from 3
        elif route_distance_km < 100:
            max_pois = 3  # Reduced from 5
        else:
            max_pois = 5  # Reduced from 8
    
    # Calculate search radius based on distance
    # Max radius should be roughly the size of a German state (Bayern ~200km across)
    # Use a reasonable fraction of the route distance, capped at ~100km
    if search_radius_km is None:
        # For shorter routes, use a generous radius
        # For longer routes, cap at ~100km (roughly half a German state)
        effective_radius = min(route_distance_km * 0.5, 100.0)
        # But ensure minimum radius for very short routes
        effective_radius = max(effective_radius, 10.0)
    else:
        # If provided, use it but cap at reasonable max
        effective_radius = min(search_radius_km, 100.0)
    
    all_pois = []
    
    # Limit initial POI discovery to avoid processing too many
    # We'll get a reasonable sample, then filter down
    max_initial_pois = max_pois * 30  # Get 30x more than needed for filtering (reduced from 50)
    
    # Query OSM (primary source - most reliable)
    if "osm" in sources:
        try:
            osm_pois = discover_osm_pois(mid_lat, mid_lon, effective_radius, limit=max_initial_pois)
            all_pois.extend(osm_pois)
            logger.info(f"Found {len(osm_pois)} POIs from OSM")
        except Exception as e:
            logger.warning(f"OSM POI discovery failed: {e}")
    
    # Query ORS POIs (reliable, uses same API key as routing)
    if "ors" in sources and ORS_POIS_AVAILABLE and discover_ors_pois:
        try:
            # ORS POIs API is reliable and uses the same API key
            ors_pois = discover_ors_pois(mid_lat, mid_lon, effective_radius, limit=max_initial_pois)
            all_pois.extend(ors_pois)
            logger.info(f"Found {len(ors_pois)} POIs from ORS")
        except Exception as e:
            logger.warning(f"ORS POI discovery failed: {e}")
    
    # Deduplicate POIs (same location within ~100m)
    deduplicated = deduplicate_pois(all_pois, distance_threshold_m=100)
    
    # Don't filter by distance to direct A→B line - we want POIs anywhere in the area
    # The progressive filter will ensure they move toward the destination
    # Just annotate them with position along the direct line for ordering purposes
    for poi in deduplicated:
        _, position = point_to_line_distance_km(
            poi.lat, poi.lon,
            start_lat, start_lon,
            end_lat, end_lon
        )
        poi.position_along_route = position
        # Calculate distance to destination for progressive filtering
        poi.distance_from_route_km = distance_km(poi.lat, poi.lon, end_lat, end_lon)
    
    # Order POIs by their position along the A→B direction (for initial ordering)
    # But we'll use progressive filtering to ensure they actually move toward B
    ordered_pois = sorted(deduplicated, key=lambda p: p.position_along_route or 0)
    
    # Apply progressive approach filter - only keep POIs that move closer to destination
    # This allows unlimited detours as long as each step gets closer
    progressive_pois = filter_progressive_pois(
        ordered_pois,
        start_lat, start_lon,
        end_lat, end_lon,
        tolerance_km=progressive_tolerance_km
    )
    
    logger.info(
        f"Progressive filtering: {len(ordered_pois)} POIs -> {len(progressive_pois)} POIs "
        f"(removed {len(ordered_pois) - len(progressive_pois)} that don't progress toward destination)"
    )
    
    # If we have scenic scores, prioritize them
    if prioritize_scenic:
        # Separate POIs with and without scores
        scored_pois = [p for p in progressive_pois if p.score is not None]
        unscored_pois = [p for p in progressive_pois if p.score is None]
        
        # Sort scored POIs by score (descending), but maintain progressive order
        scored_pois.sort(key=lambda p: -(p.score or 0))
        
        # Recombine: scored POIs first, then unscored
        progressive_pois = scored_pois + unscored_pois
    
    # Select POIs distributed evenly along the route
    # This ensures coverage across the entire route rather than clustering
    # The function divides the route into segments and picks the best POI from each
    logger.info(f"Before distribution: {len(progressive_pois)} POIs, target: {max_pois} POIs")
    if progressive_pois:
        # Log POI positions before distribution
        positions_before = [p.position_along_route for p in progressive_pois[:10] if p.position_along_route is not None]
        if positions_before:
            logger.info(f"Sample POI positions before distribution: {[f'{p:.2f}' for p in positions_before[:5]]}")
    
    selected_pois = _optimize_poi_selection(progressive_pois, max_pois)
    
    logger.info(f"After distribution: {len(selected_pois)} POIs selected")
    if selected_pois:
        positions_after = [p.position_along_route for p in selected_pois if p.position_along_route is not None]
        if positions_after:
            logger.info(f"POI positions after distribution: {[f'{p:.2f}' for p in positions_after]}")
    
    # Final check: ensure progressive approach is maintained
    # (should already be, but double-check)
    final_pois = filter_progressive_pois(
        selected_pois,
        start_lat, start_lon,
        end_lat, end_lon,
        tolerance_km=progressive_tolerance_km
    )
    
    final_detour = estimate_route_detour_km(start_lat, start_lon, end_lat, end_lon, final_pois)
    detour_ratio = final_detour / route_distance_km if route_distance_km > 0 else 0
    
    logger.info(
        f"Selected {len(final_pois)} POIs along route "
        f"(route: {route_distance_km:.1f}km, search radius: {effective_radius:.1f}km, "
        f"estimated detour: {final_detour:.1f}km, detour ratio: {detour_ratio:.2f}x) - "
        f"Progressive approach: each POI moves closer to destination"
    )
    
    return final_pois


def _optimize_poi_selection(pois: List[PointOfInterest], max_count: int) -> List[PointOfInterest]:
    """
    Optimize POI selection by distributing POIs evenly along the route.
    
    Divides the route into segments and selects the best POI from each segment.
    This ensures coverage across the entire route rather than clustering in one area.
    """
    if len(pois) <= max_count:
        return pois
    
    # Filter out POIs without position (shouldn't happen, but be safe)
    pois_with_position = [p for p in pois if p.position_along_route is not None]
    pois_without_position = [p for p in pois if p.position_along_route is None]
    
    if not pois_with_position:
        # Fallback: if no POIs have position, just return top N by score
        pois.sort(key=lambda p: (-(p.score or 0), p.lat, p.lon))
        return pois[:max_count]
    
    # Group POIs into segments along the route
    num_segments = max_count
    segment_size = 1.0 / num_segments
    
    segments = [[] for _ in range(num_segments)]
    for poi in pois_with_position:
        # position_along_route is 0.0 to 1.0, representing progress along route
        segment_idx = min(int(poi.position_along_route / segment_size), num_segments - 1)
        segments[segment_idx].append(poi)
    
    # Select best POI from each segment (by scenic score, or first if no score)
    selected = []
    for segment in segments:
        if segment:
            # Sort by score (descending), then by position
            segment.sort(key=lambda p: (-(p.score or 0), p.position_along_route or 0))
            selected.append(segment[0])
    
    # Fill remaining slots with best remaining POIs (prioritize segments that are empty)
    remaining = [p for p in pois_with_position if p not in selected]
    remaining.sort(key=lambda p: (-(p.score or 0), p.position_along_route or 0))
    
    # Add remaining POIs up to max_count
    selected.extend(remaining[:max_count - len(selected)])
    
    # If we still have slots and POIs without position, add those too
    if len(selected) < max_count and pois_without_position:
        pois_without_position.sort(key=lambda p: (-(p.score or 0), p.lat, p.lon))
        selected.extend(pois_without_position[:max_count - len(selected)])
    
    # Re-sort by position to maintain route order
    selected.sort(key=lambda p: p.position_along_route if p.position_along_route is not None else 999)
    
    return selected[:max_count]


def score_pois_with_scenic_model(pois: List[PointOfInterest], scenic_evaluator) -> List[PointOfInterest]:
    """
    Score POIs using the scenic evaluation model.
    
    This function can be used to rank POIs by their scenic value before
    inserting them as waypoints.
    
    Args:
        pois: List of POI objects
        scenic_evaluator: Function that takes (lat, lon) and returns scenic score
    
    Returns:
        List of POIs with scores assigned, sorted by score
    """
    scored_pois = []
    
    for poi in pois:
        try:
            # Evaluate scenic score at POI location
            # This would use your existing scenic evaluation service
            score = scenic_evaluator(poi.lat, poi.lon)
            poi.score = score
            scored_pois.append(poi)
        except Exception as e:
            logger.warning(f"Failed to score POI {poi.name}: {e}")
            scored_pois.append(poi)  # Include without score
    
    # Sort by score (highest first)
    scored_pois.sort(key=lambda p: p.score if p.score is not None else -1, reverse=True)
    
    return scored_pois