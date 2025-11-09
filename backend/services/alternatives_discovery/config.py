"""
Configuration for alternatives discovery services.
"""

from __future__ import annotations

import os
from pathlib import Path

# Embedding model configuration
EMBED_MODEL_PATH = os.getenv("EMBED_MODEL_PATH", "./models/e5-small-v2")
EMBED_MODEL_FALLBACK = os.getenv("EMBED_MODEL_FALLBACK", "intfloat/e5-small-v2")

# Cache directory root (shared by HTTP + embedding caches)
CACHE_ROOT = Path(os.getenv("TRAVEL_MARVEL_CACHE_DIR", "./.cache")).resolve()
FAISS_CACHE_DIR = CACHE_ROOT / "faiss"

# External services configuration
REQUEST_USER_AGENT = os.getenv(
    "TRAVEL_MARVEL_USER_AGENT",
    "travel_marvel/0.1 (cassini-hackathon prototype)",
)

NOMINATIM_SEARCH_URL = os.getenv(
    "TRAVEL_MARVEL_NOMINATIM_SEARCH_URL",
    "https://nominatim.openstreetmap.org/search",
)

OVERPASS_API_URL = os.getenv(
    "TRAVEL_MARVEL_OVERPASS_URL",
    "https://overpass-api.de/api/interpreter",
)

COPERNICUS_EUDEM_WMTS = os.getenv("COPERNICUS_EUDEM_WMTS", "").strip()
COPERNICUS_TOKEN = os.getenv("COPERNICUS_TOKEN", "").strip()

# Generic request timeout (seconds)
DEFAULT_REQUEST_TIMEOUT = float(os.getenv("TRAVEL_MARVEL_REQUEST_TIMEOUT", "30"))

# Respectful delay between repeated requests (seconds)
DEFAULT_REQUEST_DELAY = float(os.getenv("TRAVEL_MARVEL_REQUEST_DELAY", "1.0"))

__all__ = [
    "EMBED_MODEL_PATH",
    "EMBED_MODEL_FALLBACK",
    "CACHE_ROOT",
    "FAISS_CACHE_DIR",
    "REQUEST_USER_AGENT",
    "NOMINATIM_SEARCH_URL",
    "OVERPASS_API_URL",
    "COPERNICUS_EUDEM_WMTS",
    "COPERNICUS_TOKEN",
    "DEFAULT_REQUEST_TIMEOUT",
    "DEFAULT_REQUEST_DELAY",
]

