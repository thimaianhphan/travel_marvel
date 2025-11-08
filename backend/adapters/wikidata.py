"""
Wikidata helpers used when enriching POI descriptions.
"""

from __future__ import annotations

import re
from typing import Dict, Optional, Set

from .http_cache import cached_get


def fetch_entity(qid: str) -> Optional[Dict]:
    if not qid or not re.fullmatch(r"Q\d+", qid):
        return None
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
    try:
        data = cached_get(url, ttl=7 * 24 * 60 * 60)
        return data.get("entities", {}).get(qid)
    except Exception:
        return None


def has_instance(entity: Dict, qids: Set[str]) -> bool:
    try:
        for claim in entity["claims"].get("P31", []):
            value = claim["mainsnak"]["datavalue"]["value"]
            if value.get("id") in qids:
                return True
    except Exception:
        pass
    return False


def located_in(entity: Dict, label_keywords: Set[str]) -> bool:
    try:
        related_ids = []
        for pid in ("P3018", "P131", "P706", "P361"):
            for claim in entity["claims"].get(pid, []):
                value = claim["mainsnak"]["datavalue"].get("value", {})
                if "id" in value:
                    related_ids.append(value["id"])
        for neighbour_id in related_ids[:5]:
            neighbour = fetch_entity(neighbour_id)
            if not neighbour:
                continue
            label = neighbour.get("labels", {}).get("en", {}).get("value")
            if not label:
                labels = neighbour.get("labels", {})
                if labels:
                    label = next(iter(labels.values())).get("value")
            if label and any(keyword in label.lower() for keyword in label_keywords):
                return True
    except Exception:
        pass
    return False


__all__ = ["fetch_entity", "has_instance", "located_in"]

