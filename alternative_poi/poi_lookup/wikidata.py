import re
from typing import Dict, Optional
from .cache_http import cached_get

def fetch_wikidata_entity(qid: str) -> Optional[Dict]:
    if not qid or not re.fullmatch(r"Q\d+", qid):
        return None
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
    try:
        data = cached_get(url, ttl=7*86400)
        return data.get("entities", {}).get(qid)
    except Exception:
        return None

def wd_has_instance(ent: Dict, qids: set) -> bool:
    try:
        for c in ent["claims"].get("P31", []):
            v = c["mainsnak"]["datavalue"]["value"]
            if v.get("id") in qids: return True
    except Exception:
        pass
    return False

def wd_located_in(ent: Dict, label_keywords: set) -> bool:
    from .wikidata import fetch_wikidata_entity as _fetch  # local reuse
    try:
        ids = []
        for pid in ("P3018", "P131", "P706", "P361"):
            for c in ent["claims"].get(pid, []):
                v = c["mainsnak"]["datavalue"]["value"]
                if "id" in v: ids.append(v["id"])
        for tid in ids[:5]:
            t = _fetch(tid)
            if not t: continue
            lab = t.get("labels", {}).get("en", {}).get("value") or next((v["value"] for v in t.get("labels", {}).values()), "")
            if any(k in (lab or "").lower() for k in label_keywords):
                return True
    except Exception:
        pass
    return False
