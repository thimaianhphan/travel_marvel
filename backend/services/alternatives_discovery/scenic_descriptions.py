"""
Generate descriptive scenic narratives for resolved POIs.
"""

from __future__ import annotations

from typing import Dict, Optional

from adapters.copernicus import relief_is_steep
from adapters.wikidata import fetch_entity, has_instance, located_in


def is_narrative(text: Optional[str]) -> bool:
    if not text:
        return False
    words = text.split()
    if len(words) < 10:
        return False
    if sum(ch in ":;()/[]" for ch in text) >= 3:
        return False
    return True


def generate_scenic_description(category: str, tags: Dict, lat: float, lon: float) -> Optional[str]:
    wikidata_id = tags.get("wikidata")
    wikidata_entity = fetch_entity(wikidata_id) if wikidata_id else None

    type_word = {
        "lake": "lake",
        "waterfall": "waterfall",
        "beach": "beach",
        "viewpoint": "viewpoint",
        "park": "park",
        "castle": "castle",
        "church": "church",
        "museum": "museum",
        "unknown": "site",
    }.get(category or "unknown", "site")

    is_glacial = False
    is_caldera = False
    is_fjord_like = tags.get("water") == "fjord"
    in_protected_area = False
    has_forest = False
    clear_water = False
    steep_relief = False

    def tag_value(key: str) -> str:
        return (tags.get(key) or "").lower()

    if tag_value("glacier") == "yes" or tag_value("glacial") == "yes":
        is_glacial = True
    if "caldera" in tag_value("natural") or "crater" in tag_value("natural") or tag_value("volcanic") == "yes":
        is_caldera = True
    if tag_value("protect_class") or tag_value("boundary") == "protected_area" or "national_park" in tag_value("leisure"):
        in_protected_area = True
    if tag_value("wood") or tag_value("landuse") in {"forest"}:
        has_forest = True
    if category in {"lake", "beach", "waterfall"} and tags.get("natural") in {"water", "beach", "waterfall"}:
        clear_water = True

    if wikidata_entity:
        GLACIAL_QIDS = {"Q23397"}
        CRATER_LAKE_QIDS = {"Q107715"}
        if has_instance(wikidata_entity, GLACIAL_QIDS):
            is_glacial = True
        if has_instance(wikidata_entity, CRATER_LAKE_QIDS):
            is_caldera = True
        if located_in(wikidata_entity, {"national park", "protected", "park"}):
            in_protected_area = True
        if located_in(wikidata_entity, {"alps", "gebirge", "mountain"}):
            steep_relief = True

    if relief_is_steep(lat, lon):
        steep_relief = True

    clauses = []
    if in_protected_area:
        clauses.append("within a protected national park")
    if steep_relief:
        clauses.append("surrounded by towering mountains")
    elif category in {"viewpoint", "waterfall", "lake"}:
        clauses.append("framed by high slopes")
    if category in {"lake", "beach", "waterfall"} and clear_water:
        clauses.append("renowned for its clear, emerald-toned waters")
    if is_glacial and category == "lake":
        clauses.append("shaped by glacier activity")
    if is_caldera and category == "lake":
        clauses.append("set within a volcanic crater")
    if is_fjord_like and category == "lake":
        clauses.append("with a long, fjord-like basin")
    if has_forest or in_protected_area:
        clauses.append("forest-lined shores")

    unique_clauses = list(dict.fromkeys(clauses))[:3]
    mood = "serene atmosphere"

    defaults = {
        "lake": "A lake with clear waters and forested slopes, creating a calm alpine setting.",
        "waterfall": "A waterfall dropping into a narrow gorge, backed by steep, rugged terrain.",
        "beach": "A natural beach with clean shoreline and an unspoiled feel.",
        "viewpoint": "An elevated viewpoint with broad panoramas across surrounding peaks and valleys.",
        "park": "A protected natural area with trails, woodland, and a quiet atmosphere.",
        "castle": "A historic castle set amid scenic landscapes and traditional architecture.",
        "church": "A landmark church noted for its setting and striking silhouette.",
        "museum": "A museum focused on the region’s heritage in a pleasant setting.",
        "unknown": "A scenic natural site in a tranquil setting.",
    }

    if not unique_clauses:
        return defaults.get(category or "unknown")

    sentence1 = f"A {type_word}, " + ", ".join(unique_clauses) + "."
    sentence2_bits = []
    if category in {"lake", "beach"}:
        sentence2_bits.append("Its waters appear distinctly clear")
    if category == "lake" and any("fjord-like" in clause or "narrow" in clause for clause in unique_clauses):
        sentence2_bits.append("with a long, narrow profile")
    sentence2_bits.append(f"creating a {mood}")
    sentence2 = (", ".join(sentence2_bits) + ".").replace("..", ".")

    text = (sentence1 + " " + sentence2).strip()
    if len(text.split()) < 20:
        text = sentence1 + " " + defaults.get(category or "unknown", "")
    if len(text.split()) > 50:
        text = sentence1 + " " + f"It offers a {mood}."
    return text


__all__ = ["generate_scenic_description", "is_narrative"]

