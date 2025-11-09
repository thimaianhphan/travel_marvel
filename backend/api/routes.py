from __future__ import annotations

from dataclasses import asdict
from typing import Dict, List, Set, Tuple

from fastapi import APIRouter, HTTPException

from backend.adapters.osm import discover_osm_pois
from backend.models.alternative import (
    AlternativePoi,
    AlternativeRoute,
    AlternativesRequest,
    AlternativesResponse,
)
from backend.models.poi import PointOfInterest
from backend.services.alternatives_discovery import plan_alternative_routes, resolve_one

router = APIRouter()


LOCAL_CANDIDATE_RADIUS_KM = 120.0
LOCAL_CANDIDATE_LIMIT = 60

# --- temporary stub until the video-analysis teammate plugs in ---
DEFAULT_TARGET = {"name": "Neuschwanstein Castle", "hint": "castle"}
DEFAULT_REGIONAL_CANDIDATES = [
    {"name": "Heidelberg Castle", "hint": "castle"},
    {"name": "Hohenzollern Castle", "hint": "castle"},
    {"name": "Lichtenstein Castle", "hint": "castle"},
    {"name": "Triberg Waterfalls", "hint": "waterfall"},
    {"name": "Titisee", "hint": "lake"},
    {"name": "Blautopf", "hint": "lake"},
]


def _mock_extract_attractions(video_url: str) -> Tuple[Dict[str, str], List[Dict[str, str]]]:
    # Drop something smarter here once the transcript extractor is ready.
    return DEFAULT_TARGET, DEFAULT_REGIONAL_CANDIDATES


def _serialize_poi(poi: PointOfInterest) -> AlternativePoi:
    data = asdict(poi)
    return AlternativePoi(
        name=data["name"],
        lat=data["lat"],
        lon=data["lon"],
        poi_type=data["poi_type"],
        source=data["source"],
        score=data.get("score"),
        tags=data.get("tags") or {},
    )


def _collect_local_candidate_names(
    lat: float,
    lon: float,
    exclude: Set[str],
    *,
    radius_km: float = LOCAL_CANDIDATE_RADIUS_KM,
    limit: int = LOCAL_CANDIDATE_LIMIT,
) -> List[Dict[str, str]]:
    pois = discover_osm_pois(lat, lon, radius_km=radius_km, limit=limit * 3)
    candidates: List[Dict[str, str]] = []
    seen = {name.lower() for name in exclude}

    for poi in pois:
        name = (poi.name or "").strip()
        if not name:
            continue
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        candidates.append({"name": name, "hint": poi.poi_type})
        if len(candidates) >= limit:
            break

    return candidates


@router.post("/alternatives", response_model=AlternativesResponse)
def generate_alternatives(payload: AlternativesRequest) -> AlternativesResponse:
    manual_places = [place.strip() for place in (payload.manual_places or []) if place and place.strip()]

    if not manual_places and not payload.video_url:
        raise HTTPException(status_code=400, detail="Provide either a video_url or manual_places.")

    search_radius = payload.search_radius_km or LOCAL_CANDIDATE_RADIUS_KM
    poi_search_radius = max(10.0, min(search_radius, 150.0))

    if manual_places:
        target_name = manual_places[0]
        resolved_target = resolve_one(target_name)
        if not resolved_target:
            raise HTTPException(status_code=404, detail=f"Could not resolve destination '{target_name}'.")

        target = {
            "name": resolved_target["name"],
            "hint": resolved_target.get("category"),
        }

        manual_candidate_seeds = [
            {"name": entry}
            for entry in manual_places[1:]
            if entry.lower() != resolved_target["name"].lower()
        ]

        auto_candidates = _collect_local_candidate_names(
            payload.user_lat,
            payload.user_lon,
            exclude={resolved_target["name"], *manual_places[1:]},
            radius_km=search_radius,
            limit=LOCAL_CANDIDATE_LIMIT,
        )
        candidate_pool = manual_candidate_seeds + auto_candidates

        if not candidate_pool:
            auto_candidates = _collect_local_candidate_names(
                payload.user_lat,
                payload.user_lon,
                exclude={resolved_target["name"]},
                radius_km=search_radius,
                limit=LOCAL_CANDIDATE_LIMIT,
            )
            candidate_pool = auto_candidates

        if not candidate_pool:
            raise HTTPException(
                status_code=502,
                detail="Unable to assemble local alternatives – try a different area or add manual suggestions.",
            )
    else:
        target, candidate_pool = _mock_extract_attractions(payload.video_url or "")

    if not manual_places:
        auto_candidates = _collect_local_candidate_names(
            payload.user_lat,
            payload.user_lon,
            exclude={target["name"]},
            radius_km=search_radius,
            limit=LOCAL_CANDIDATE_LIMIT,
        )
        candidate_pool = auto_candidates or candidate_pool

    try:
        raw_result = plan_alternative_routes(
            user_start=(payload.user_lat, payload.user_lon),
            target_poi=target,
            regional_candidates=candidate_pool,
            radius_km=max(200.0, search_radius),
            topk_each=payload.max_alternatives,
            poi_discovery_kwargs={
                "search_radius_km": poi_search_radius,
                "max_pois": 3,
                "prioritize_scenic": True,
            },
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    target_name, alternatives = next(iter(raw_result.items()))

    serialised: List[AlternativeRoute] = []
    for entry in alternatives:
        destination = _serialize_poi(entry["destination"])
        scenic_waypoints = [_serialize_poi(poi) for poi in entry["route_pois"]]
        serialised.append(
            AlternativeRoute(
                destination=destination,
                scenic_waypoints=scenic_waypoints,
                score=entry.get("score"),
            )
        )

    return AlternativesResponse(
        video_url=payload.video_url or manual_places[0],
        target_name=target_name,
        alternatives=serialised,
    )