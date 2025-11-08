from typing import Dict, Optional

CATEGORY_MAP = {
    "waterfall": {"natural": "waterfall"},
    "lake": {"natural": "water"},
    "viewpoint": {"tourism": "viewpoint"},
    "beach": {"natural": "beach"},
    "museum": {"tourism": "museum"},
    "castle": {"historic": "castle"},
    "church": {"amenity": "place_of_worship"},
    "park": {"leisure": "park"},
}

def infer_category(tags: Dict, hint: Optional[str]) -> str:
    if hint and hint in CATEGORY_MAP and all(tags.get(k) == v for k, v in CATEGORY_MAP[hint].items()):
        return hint
    if tags.get("natural") == "waterfall" or tags.get("waterway") == "waterfall":
        return "waterfall"
    if tags.get("water") in {"lake","lagoon","reservoir","pond","fjord"} or tags.get("natural") == "water":
        return "lake"
    if tags.get("tourism") == "viewpoint": return "viewpoint"
    if tags.get("natural") == "beach": return "beach"
    if tags.get("historic") == "castle": return "castle"
    if tags.get("amenity") == "place_of_worship": return "church"
    if tags.get("leisure") == "park": return "park"
    return "unknown"
