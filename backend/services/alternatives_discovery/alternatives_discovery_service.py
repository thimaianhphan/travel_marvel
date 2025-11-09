"""
High-level orchestration for discovering local alternatives to popular destinations.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Sequence, Tuple

from backend.adapters.ors import ors_route
from backend.models.poi import PointOfInterest
from backend.services.poi_discovery.poi_discovery_service import discover_pois_along_route

from .poi_lookup_service import batch_resolve, resolve_one
from .similar_poi_finder import SimilarPOIFinder

logger = logging.getLogger(__name__)


def _to_poi(record: Dict, *, source: str, score: Optional[float] = None) -> PointOfInterest:
    return PointOfInterest(
        name=record.get("name", "Unnamed POI"),
        lat=float(record.get("lat")),
        lon=float(record.get("lon")),
        poi_type=(record.get("category") or "unknown"),
        source=source,
        tags=record.get("tags") or {},
        score=score,
    )


def discover_local_alternatives(
    user_center: Tuple[float, float],
    target_pois: Sequence[Dict[str, str]],
    regional_candidates: Sequence[Dict[str, str]],
    *,
    radius_km: float = 200.0,
    topk_each: int = 5,
) -> Dict[str, List[Dict]]:
    """
    Resolve seed POIs and produce lists of locally similar alternatives.

    Args:
        user_center: Latitude/longitude tuple representing the user's region of interest.
        target_pois: Sequence of dicts containing at least a ``name`` field and optional ``hint``.
        regional_candidates: Pool of candidate POIs in the local area (same structure as ``target_pois``).
        radius_km: Maximum distance from ``user_center`` to keep when building the similarity index.
        topk_each: Number of alternatives to return per target POI.

    Returns:
        Mapping from target POI name to a list of alternative suggestion dicts.
    """
    resolved_targets = [resolve_one(poi["name"], hint=poi.get("hint")) for poi in target_pois]
    resolved_targets = [poi for poi in resolved_targets if poi is not None]
    if not resolved_targets:
        raise RuntimeError("Failed to resolve any target POIs via Nominatim.")

    resolved_candidates = batch_resolve(list(regional_candidates))
    resolved_candidates = [poi for poi in resolved_candidates if poi is not None]
    if not resolved_candidates:
        raise RuntimeError("Failed to resolve any regional candidate POIs via Nominatim.")

    finder = SimilarPOIFinder(radius_km=radius_km)
    try:
        finder.build_index(resolved_candidates, user_center=user_center)
        suggestions = finder.find_similar(resolved_targets, topk_each=topk_each)
    except Exception as exc:
        logger.warning("Similarity search failed (%s). Falling back to heuristic candidate order.", exc)
        suggestions = []
        for seed in resolved_targets:
            trimmed_candidates = resolved_candidates[:topk_each]
            suggestions.append(
                {
                    "query_name": seed["name"],
                    "query_lonlat": [float(seed.get("lon", 0.0)), float(seed.get("lat", 0.0))],
                    "results": [
                        {
                            "name": cand.get("name"),
                            "lonlat": [float(cand.get("lon", 0.0)), float(cand.get("lat", 0.0))],
                            "score": None,
                            "category": cand.get("category") or "unknown",
                            "tags": cand.get("tags") or {},
                        }
                        for cand in trimmed_candidates
                    ],
                }
            )

    output: Dict[str, List[Dict]] = {}
    for seed, suggestion in zip(resolved_targets, suggestions):
        alt_list = []
        for alternative in suggestion["results"]:
            alt_lat = alternative["lonlat"][1]
            alt_lon = alternative["lonlat"][0]
            record = next(
                (
                    candidate
                    for candidate in resolved_candidates
                    if candidate["name"] == alternative["name"]
                    and abs(float(candidate["lat"]) - alt_lat) < 1e-5
                    and abs(float(candidate["lon"]) - alt_lon) < 1e-5
                ),
                {
                    "name": alternative["name"],
                    "lat": alt_lat,
                    "lon": alt_lon,
                    "category": alternative.get("category", "unknown"),
                    "tags": alternative.get("tags", {}),
                },
            )
            alt_list.append(
                {
                    "destination": _to_poi(record, source="local_alternative", score=alternative.get("score")),
                    "raw": record,
                }
            )
        output[seed["name"]] = alt_list
    return output


def plan_alternative_routes(
    user_start: Tuple[float, float],
    target_poi: Dict[str, str],
    regional_candidates: Sequence[Dict[str, str]],
    *,
    radius_km: float = 200.0,
    topk_each: int = 3,
    poi_discovery_kwargs: Optional[Dict] = None,
) -> Dict[str, List[Dict]]:
    """
    Discover local alternatives and compute scenic routes to each.

    Args:
        user_start: Tuple of (lat, lon) for the user's origin.
        target_poi: Dict containing the viral POI's ``name`` and optional ``hint``.
        regional_candidates: List of dicts representing local options (same structure as ``target_poi``).
        radius_km: Radius for similarity search.
        topk_each: Number of alternatives to keep.
        poi_discovery_kwargs: Extra parameters passed to ``discover_pois_along_route``.

    Returns:
        Mapping with a single key (target name) containing route suggestions.
    """
    poi_discovery_kwargs = poi_discovery_kwargs or {}
    alternative_map = discover_local_alternatives(
        user_center=user_start,
        target_pois=[target_poi],
        regional_candidates=regional_candidates,
        radius_km=radius_km,
        topk_each=topk_each,
    )

    target_name = next(iter(alternative_map.keys()))
    routes: List[Dict] = []
    for entry in alternative_map[target_name]:
        destination: PointOfInterest = entry["destination"]
        route_pois = discover_pois_along_route(
            start_lat=user_start[0],
            start_lon=user_start[1],
            end_lat=destination.lat,
            end_lon=destination.lon,
            **poi_discovery_kwargs,
        )
        routes.append(
            {
                "destination": destination,
                "score": destination.score,
                "route_pois": route_pois,
                "route_path": _build_route_path(
                    user_start=user_start,
                    waypoints=route_pois,
                    destination=destination,
                ),
            }
        )

    return {target_name: routes}


__all__ = ["discover_local_alternatives", "plan_alternative_routes"]


def _build_route_path(
    *,
    user_start: Tuple[float, float],
    waypoints: List[PointOfInterest],
    destination: PointOfInterest,
) -> List[List[float]]:
    """
    Request a routed polyline from ORS. Falls back to straight-line segments if routing fails.
    Returns coordinates as [lat, lon] pairs.
    """
    latlng_points: List[Tuple[float, float]] = [
        (float(user_start[0]), float(user_start[1])),
        *[(float(poi.lat), float(poi.lon)) for poi in waypoints],
        (float(destination.lat), float(destination.lon)),
    ]

    route_path: List[List[float]] = []
    profiles = ("driving-car", "foot-walking", "cycling-regular")

    for profile in profiles:
        try:
            routes = ors_route(latlng_points, profile=profile, ask_alternatives=1)
            if routes:
                route_path = [[coord[1], coord[0]] for coord in routes[0] if len(coord) >= 2]
                if route_path:
                    logger.info("ORS returned %d points using profile '%s'", len(route_path), profile)
                    break
        except Exception as exc:  # pragma: no cover - network failures
            logger.warning("ORS routing failed with profile '%s' (%s)", profile, exc)

    if not route_path:
        logger.warning(
            "ORS routing unavailable for profiles %s; falling back to direct segments.",
            ", ".join(profiles),
        )
        route_path = [[lat, lon] for lat, lon in latlng_points]

    return route_path

