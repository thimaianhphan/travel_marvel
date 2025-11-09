from __future__ import annotations

from dataclasses import asdict
from typing import Dict, List, Tuple

from fastapi import APIRouter, HTTPException
from backend.models.poi import PointOfInterest
from backend.services.alternatives_discovery import plan_alternative_routes
from backend.models.alternative import AlternativePoi, AlternativeRoute, AlternativesRequest, AlternativesResponse

router = APIRouter()


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


@router.post("/alternatives", response_model=AlternativesResponse)
def generate_alternatives(payload: AlternativesRequest) -> AlternativesResponse:
    target, candidate_pool = _mock_extract_attractions(payload.video_url)

    try:
        raw_result = plan_alternative_routes(
            user_start=(payload.user_lat, payload.user_lon),
            target_poi=target,
            regional_candidates=candidate_pool,
            radius_km=200,
            topk_each=payload.max_alternatives,
            poi_discovery_kwargs={
                "search_radius_km": 40,
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
        video_url=payload.video_url,
        target_name=target_name,
        alternatives=serialised,
    )