"""
POI Discovery Configuration

Centralized configuration for POI discovery services.
"""

# Overpass API endpoint (public instance)
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
# Alternative: "https://overpass.kumi.systems/api/interpreter"

# Nominatim API (for reverse geocoding if needed)
NOMINATIM_URL = "https://nominatim.openstreetmap.org"

# OpenTripMap API (free tier, no key required for basic usage)
OPENTRIPMAP_URL = "https://api.opentripmap.io/0.1/en/places"

# Request timeouts and rate limiting
OVERPASS_TIMEOUT = 30
NOMINATIM_TIMEOUT = 10
REQUEST_DELAY = 1.0  # Delay between requests to respect rate limits