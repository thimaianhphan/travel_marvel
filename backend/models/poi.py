"""
Point of Interest Data Models

Defines the POI data structure and related models.
"""

from dataclasses import dataclass
from typing import Dict, Tuple, Any, Optional


@dataclass
class PointOfInterest:
    """Point of Interest data structure."""
    name: str
    lat: float
    lon: float
    poi_type: str  # e.g., "viewpoint", "lake", "park", "monument"
    source: str  # "osm", "opentripmap", etc.
    tags: Dict[str, Any]  # Additional metadata
    score: Optional[float] = None  # Scenic score (if evaluated)
    distance_from_route_km: Optional[float] = None  # Distance from route line
    position_along_route: Optional[float] = None  # Position along A→B (0.0 to 1.0)
    
    def to_latlng(self) -> Tuple[float, float]:
        """Return as (lat, lon) tuple for route generation."""
        return (self.lat, self.lon)
    
    def to_lonlat(self) -> Tuple[float, float]:
        """Return as (lon, lat) tuple for APIs."""
        return (self.lon, self.lat)

