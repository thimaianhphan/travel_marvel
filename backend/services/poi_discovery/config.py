"""
POI Discovery Configuration

Centralized configuration for POI discovery services.
"""

# Overpass API endpoints (rotate between local + public instances)
OVERPASS_URLS = [
    "http://localhost/api/interpreter",  # optional self-hosted instance
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter",
    "https://overpass.openstreetmap.ru/api/interpreter",
]

# Backwards compatibility constant (primary endpoint)
OVERPASS_URL = OVERPASS_URLS[0]

# Nominatim API (for reverse geocoding if needed)
NOMINATIM_URL = "https://nominatim.openstreetmap.org"

# OpenTripMap API (free tier, no key required for basic usage)
OPENTRIPMAP_URL = "https://api.opentripmap.io/0.1/en/places"

# Request timeouts and rate limiting
OVERPASS_TIMEOUT = 30
NOMINATIM_TIMEOUT = 10
REQUEST_DELAY = 1.0  # Delay between requests to respect rate limits