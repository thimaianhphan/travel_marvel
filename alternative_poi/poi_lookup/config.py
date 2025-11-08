import os
USER_AGENT = "travel_marvel/0.1 (pmaianh1910@gmail.com)"
NOMINATIM = "https://nominatim.openstreetmap.org/search"
OVERPASS = "https://overpass-api.de/api/interpreter"

# Optional Copernicus
COPERNICUS_EUDEM_WMTS = os.getenv("COPERNICUS_EUDEM_WMTS", "").strip()
COPERNICUS_TOKEN = os.getenv("COPERNICUS_TOKEN", "").strip()
