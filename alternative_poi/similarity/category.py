from typing import List

CATEGORY_EQUIV = {
    "lake": {"lake","lagoon","reservoir","pond","fjord","glacial_lake","crater_lake"},
    "waterfall": {"waterfall","cascade"},
    "beach": {"beach","bay","shore","coastline"},
    "viewpoint": {"viewpoint","peak","summit","overlook","cliff"},
    "park": {"park","protected_area","nature_reserve"},
    "castle": {"castle","fortress"},
    "church": {"church","cathedral","basilica","monastery"},
    "museum": {"museum"},
    "unknown": {"unknown"},
}

SUBTYPE_TO_COARSE = {
    "lagoon":"lake","reservoir":"lake","pond":"lake","fjord":"lake",
    "cascade":"waterfall","cathedral":"church","basilica":"church","monastery":"church",
    "fortress":"castle","protected_area":"park","nature_reserve":"park"
}

def matching_buckets(qcat: str) -> List[str]:
    q = (qcat or "unknown").lower()
    allowed = CATEGORY_EQUIV.get(q, {q})
    cats = []
    for coarse, members in CATEGORY_EQUIV.items():
        if (coarse in allowed) or (len(members.intersection(allowed)) > 0):
            cats.append(coarse)
    return cats
