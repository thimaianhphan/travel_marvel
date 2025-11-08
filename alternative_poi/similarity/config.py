import os
MODEL_PATH = os.getenv("EMBED_MODEL_PATH", "./models/e5-small-v2")
MODEL_FALLBACK = os.getenv("EMBED_MODEL_FALLBACK", "intfloat/e5-small-v2")

COPERNICUS_EUDEM_WMS = os.getenv("COPERNICUS_EUDEM_WMTS", "").strip()
COPERNICUS_TOKEN = os.getenv("COPERNICUS_TOKEN", "").strip()
USER_AGENT = "travel_marvel/0.1 (pmaianh1910@gmail.com)"
