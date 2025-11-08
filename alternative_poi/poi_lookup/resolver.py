import json
from typing import Dict, List, Optional
from .osm import nominatim_lookup, overpass_tags
from .category import infer_category
from .scenic import generate_scenic_desc, is_narrative

def resolve_one(name: str, hint: Optional[str] = None) -> Optional[Dict]:
    hits = nominatim_lookup(name)
    if not hits:
        return None
    h = hits[0]
    lat = float(h["lat"]); lon = float(h["lon"])
    osm_type = h["osm_type"][0].upper(); osm_id = int(h["osm_id"])
    tags = overpass_tags(osm_type, osm_id) or h.get("extratags", {}) or {}
    category = infer_category(tags, hint)

    raw_desc = tags.get("description") or tags.get("note")
    gen_desc = generate_scenic_desc(category, tags, lat, lon)
    if gen_desc and len(gen_desc.split()) >= 20:
        desc = gen_desc
    elif is_narrative(raw_desc):
        desc = raw_desc
    else:
        desc = gen_desc or None

    return {
        "name": h.get("namedetails", {}).get("name") or h["display_name"].split(",")[0],
        "lat": lat,
        "lon": lon,
        "category": category,
        "tags": tags,
        "desc": desc,
    }

def batch_resolve(pois: List[Dict]) -> List[Optional[Dict]]:
    return [resolve_one(p["name"], hint=p.get("hint")) for p in pois]
