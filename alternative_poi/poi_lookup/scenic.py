from typing import Dict, Optional
from .wikidata import fetch_wikidata_entity, wd_has_instance, wd_located_in
from .copernicus import relief_is_steep

def is_narrative(text: Optional[str]) -> bool:
    if not text: return False
    w = text.split()
    if len(w) < 10: return False
    if sum(ch in ":;()/[]" for ch in text) >= 3: return False
    return True

def generate_scenic_desc(category: str, tags: Dict, lat: float, lon: float) -> Optional[str]:
    # (Texts unchanged from previous version)
    qid = tags.get("wikidata")
    wd_ent = fetch_wikidata_entity(qid) if qid else None

    type_word = {
        "lake":"lake","waterfall":"waterfall","beach":"beach","viewpoint":"viewpoint","park":"park",
        "castle":"castle","church":"church","museum":"museum","unknown":"site"
    }.get(category or "unknown","site")

    is_glacial = False; is_caldera = False
    is_fjord_like = tags.get("water") == "fjord"
    in_protected = False; has_forest = False; clear_water = False; steep_relief = False

    kv = lambda k: (tags.get(k) or "").lower()
    if kv("glacier") == "yes" or kv("glacial") == "yes": is_glacial = True
    if "caldera" in kv("natural") or "crater" in kv("natural") or kv("volcanic") == "yes": is_caldera = True
    if kv("protect_class") or kv("boundary") == "protected_area" or "national_park" in kv("leisure"): in_protected = True
    if kv("wood") or kv("landuse") in {"forest"}: has_forest = True
    if category in {"lake","beach","waterfall"} and tags.get("natural") in {"water","beach","waterfall"}: clear_water = True

    if wd_ent:
        GLACIAL_QIDS = {"Q23397"}
        CRATER_LAKE_QIDS = {"Q107715"}
        if wd_has_instance(wd_ent, GLACIAL_QIDS): is_glacial = True
        if wd_has_instance(wd_ent, CRATER_LAKE_QIDS): is_caldera = True
        if wd_located_in(wd_ent, {"national park","protected","park"}): in_protected = True
        if wd_located_in(wd_ent, {"alps","gebirge","mountain"}): steep_relief = True

    if relief_is_steep(lat, lon): steep_relief = True

    clauses = []
    if in_protected: clauses.append("within a protected national park")
    if steep_relief: clauses.append("surrounded by towering mountains")
    elif category in {"viewpoint","waterfall","lake"}: clauses.append("framed by high slopes")
    if category in {"lake","beach","waterfall"} and clear_water: clauses.append("renowned for its clear, emerald-toned waters")
    if is_glacial and category == "lake": clauses.append("shaped by glacier activity")
    if is_caldera and category == "lake": clauses.append("set within a volcanic crater")
    if is_fjord_like and category == "lake": clauses.append("with a long, fjord-like basin")
    if has_forest or in_protected: clauses.append("forest-lined shores")
    picked = list(dict.fromkeys(clauses))[:3]
    mood = "serene atmosphere"

    default_by_cat = {
        "lake": "A lake with clear waters and forested slopes, creating a calm alpine setting.",
        "waterfall": "A waterfall dropping into a narrow gorge, backed by steep, rugged terrain.",
        "beach": "A natural beach with clean shoreline and an unspoiled feel.",
        "viewpoint": "An elevated viewpoint with broad panoramas across surrounding peaks and valleys.",
        "park": "A protected natural area with trails, woodland, and a quiet atmosphere.",
        "castle": "A historic castle set amid scenic landscapes and traditional architecture.",
        "church": "A landmark church noted for its setting and striking silhouette.",
        "museum": "A museum focused on the region’s heritage in a pleasant setting.",
        "unknown": "A scenic natural site in a tranquil setting."
    }

    if not picked: return default_by_cat.get(category or "unknown")

    sentence1 = f"A {type_word}, " + ", ".join(picked) + "."
    sentence2_bits = []
    if category in {"lake","beach"}: sentence2_bits.append("Its waters appear distinctly clear")
    if category == "lake" and any("fjord-like" in c or "narrow" in c for c in picked): sentence2_bits.append("with a long, narrow profile")
    sentence2_bits.append(f"creating a {mood}")
    sentence2 = (", ".join(sentence2_bits) + ".").replace("..",".")

    text = (sentence1 + " " + sentence2).strip()
    if len(text.split()) < 20:
        text = sentence1 + " " + default_by_cat.get(category or "unknown")
    if len(text.split()) > 50:
        text = sentence1 + " " + f"It offers a {mood}."
    return text
