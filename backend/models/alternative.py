"""
Models for alternatives discovery.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

class AlternativesRequest(BaseModel):
    video_url: str = Field(
        ...,
        example="https://youtube.com/shorts/hotspot123",
        description="URL of the viral travel video.",
    )
    user_lat: float = Field(..., example=49.4875)
    user_lon: float = Field(..., example=8.4660)
    max_alternatives: int = Field(
        2,
        ge=1,
        le=5,
        description="How many alternative destinations to keep.",
    )

class AlternativePoi(BaseModel):
    name: str
    lat: float
    lon: float
    poi_type: str
    source: str
    score: Optional[float] = None
    tags: Dict[str, Any] = {}

class AlternativeRoute(BaseModel):
    destination: AlternativePoi
    scenic_waypoints: List[AlternativePoi]
    score: Optional[float] = None


class AlternativesResponse(BaseModel):
    video_url: str
    target_name: str
    alternatives: List[AlternativeRoute]