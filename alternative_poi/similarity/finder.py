import math, json
from typing import Dict, List, Tuple, Optional
from sentence_transformers import SentenceTransformer
from diskcache import Cache
from .config import MODEL_PATH, MODEL_FALLBACK
from .text import poi_text
from .scenic_boost import scenic_boost
from .category import CATEGORY_EQUIV, SUBTYPE_TO_COARSE, matching_buckets
from .index import TextIndex

CACHE = Cache("./.cache/faiss")

def _distance_km(a: Tuple[float,float], b: Tuple[float,float]) -> float:
    lat1,lon1=a; lat2,lon2=b; R=6371.0
    dlat=math.radians(lat2-lat1); dlon=math.radians(lon2-lon1)
    x=math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return 2*R*math.asin(math.sqrt(x))

class SimilarPOIFinder:
    def __init__(self, model_path: Optional[str]=MODEL_PATH, alpha: float=0.7, radius_km: float=200.0):
        self.alpha=float(alpha); self.radius_km=float(radius_km)
        try: self.model = SentenceTransformer(model_path)
        except Exception: self.model = SentenceTransformer(MODEL_FALLBACK)
        self.user_center: Optional[Tuple[float,float]] = None
        self.index_by_cat: Dict[str, TextIndex] = {}
        self.meta_by_cat: Dict[str, List[Dict]] = {}

    def build_index(self, regional_pois: List[Dict], user_center: Tuple[float,float]) -> None:
        self.user_center = user_center
        buckets: Dict[str, List[Dict]] = {k: [] for k in CATEGORY_EQUIV.keys()}
        for p in regional_pois:
            plat,plon=float(p["lat"]), float(p["lon"])
            if _distance_km((plat,plon), user_center) > self.radius_km: continue
            cat=(p.get("category") or "unknown").lower()
            if cat not in buckets: cat = SUBTYPE_TO_COARSE.get(cat, cat if cat in buckets else "unknown")
            buckets[cat].append(p)
        # build per bucket
        self.index_by_cat.clear(); self.meta_by_cat.clear()
        for cat, items in buckets.items():
            if not items: continue
            idx = TextIndex(self.model)
            texts=[poi_text(p) for p in items]
            idx.add(items, texts)
            self.index_by_cat[cat]=idx
            self.meta_by_cat[cat]=items

    def _search_bucket(self, qpoi: Dict, cat: str, topn: int):
        if cat not in self.index_by_cat: return []
        return self.index_by_cat[cat].search(poi_text(qpoi), topn)

    def find_for_video_pois(self, video_pois: List[Dict], topk_each: int=5) -> List[Dict]:
        res=[]
        alpha=self.alpha
        for vp in video_pois:
            qname=vp.get("name") or "poi"
            qcat=(vp.get("category") or "unknown").lower()
            qlonlat=[float(vp["lon"]), float(vp["lat"])]
            buckets = matching_buckets(qcat)
            hits=[]
            for cat in buckets:
                hits += self._search_bucket(vp, cat, topn=max(30, topk_each*5))
            # de-dup and re-check radius
            seen=set(); dedup=[]
            for poi,cos in hits:
                key=(poi.get("name"), round(float(poi["lat"]),6), round(float(poi["lon"]),6), poi.get("category"))
                if key in seen: continue
                seen.add(key)
                if self.user_center and _distance_km((float(poi["lat"]),float(poi["lon"])), self.user_center) > self.radius_km:
                    continue
                dedup.append((poi,cos))
            # drop identical to query and score
            my_key=(round(float(vp["lat"]),6), round(float(vp["lon"]),6), qcat)
            scored=[]
            for poi,cos in dedup:
                key2=(round(float(poi["lat"]),6), round(float(poi["lon"]),6), (poi.get("category") or "unknown").lower())
                if key2==my_key: continue
                sboost=scenic_boost(poi)  # 0..0.3
                final = alpha*max(0.0,min(1.0,cos)) + (1.0-alpha)*sboost
                scored.append((poi,final))
            scored.sort(key=lambda x:x[1], reverse=True)
            top=scored[:topk_each]
            res.append({
                "query_name": qname,
                "query_lonlat": qlonlat,
                "results": [
                    {"name": poi.get("name"), "lonlat":[float(poi["lon"]), float(poi["lat"])], "score": float(score), "category": poi.get("category") or "unknown"}
                    for poi,score in top
                ]
            })
        return res
