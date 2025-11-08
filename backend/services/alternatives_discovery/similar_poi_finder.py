"""
Service for discovering locally similar POIs to a viral destination.
"""

from __future__ import annotations

import logging
import math
from typing import Dict, List, Optional, Tuple

from sentence_transformers import SentenceTransformer

from .category_mapping import CATEGORY_EQUIV, SUBTYPE_TO_COARSE, matching_buckets
from .config import EMBED_MODEL_FALLBACK, EMBED_MODEL_PATH
from .embedding_index import TextIndex
from .scenic_boost import scenic_boost
from .text_features import poi_text

logger = logging.getLogger(__name__)


def _distance_km(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    lat1, lon1 = a
    lat2, lon2 = b
    radius = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    hav = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return 2 * radius * math.asin(math.sqrt(hav))


class SimilarPOIFinder:
    def __init__(
        self,
        *,
        model_path: Optional[str] = EMBED_MODEL_PATH,
        alpha: float = 0.7,
        radius_km: float = 200.0,
    ) -> None:
        self.alpha = float(alpha)
        self.radius_km = float(radius_km)

        try:
            self.model = SentenceTransformer(model_path or EMBED_MODEL_PATH)
        except Exception as exc:
            logger.warning(
                "Failed to load embedding model from %s (%s). Falling back to %s.",
                model_path,
                exc,
                EMBED_MODEL_FALLBACK,
            )
            self.model = SentenceTransformer(EMBED_MODEL_FALLBACK)

        self.user_center: Optional[Tuple[float, float]] = None
        self.index_by_cat: Dict[str, TextIndex] = {}
        self.meta_by_cat: Dict[str, List[Dict]] = {}

    def build_index(self, regional_pois: List[Dict], *, user_center: Tuple[float, float]) -> None:
        self.user_center = user_center
        buckets: Dict[str, List[Dict]] = {name: [] for name in CATEGORY_EQUIV.keys()}

        for poi in regional_pois:
            try:
                plat = float(poi["lat"])
                plon = float(poi["lon"])
            except (KeyError, TypeError, ValueError):
                continue

            if _distance_km((plat, plon), user_center) > self.radius_km:
                continue

            category = (poi.get("category") or "unknown").lower()
            if category not in buckets:
                category = SUBTYPE_TO_COARSE.get(category, category if category in buckets else "unknown")
            buckets.setdefault(category, []).append(poi)

        self.index_by_cat.clear()
        self.meta_by_cat.clear()

        for category, items in buckets.items():
            if not items:
                continue
            index = TextIndex(self.model)
            texts = [poi_text(item) for item in items]
            index.add(items, texts)
            self.index_by_cat[category] = index
            self.meta_by_cat[category] = items

    def _search_bucket(self, query_poi: Dict, category: str, topn: int):
        index = self.index_by_cat.get(category)
        if not index:
            return []
        return index.search(poi_text(query_poi), topn)

    def find_similar(self, seed_pois: List[Dict], *, topk_each: int = 5) -> List[Dict]:
        if not self.index_by_cat:
            raise RuntimeError("Similarity index is empty. Call build_index() first.")

        results: List[Dict] = []
        alpha = self.alpha
        for query in seed_pois:
            name = query.get("name") or "poi"
            category = (query.get("category") or "unknown").lower()
            lonlat = [float(query.get("lon", 0.0)), float(query.get("lat", 0.0))]
            buckets = matching_buckets(category)
            hits = []
            for bucket in buckets:
                hits.extend(self._search_bucket(query, bucket, topn=max(30, topk_each * 5)))

            seen = set()
            deduped = []
            for item, cosine in hits:
                key = (
                    item.get("name"),
                    round(float(item.get("lat", 0.0)), 6),
                    round(float(item.get("lon", 0.0)), 6),
                    item.get("category"),
                )
                if key in seen:
                    continue
                seen.add(key)
                if self.user_center and _distance_km(
                    (float(item.get("lat", 0.0)), float(item.get("lon", 0.0))),
                    self.user_center,
                ) > self.radius_km:
                    continue
                deduped.append((item, cosine))

            query_key = (
                round(float(query.get("lat", 0.0)), 6),
                round(float(query.get("lon", 0.0)), 6),
                category,
            )

            scored = []
            for item, cosine in deduped:
                item_key = (
                    round(float(item.get("lat", 0.0)), 6),
                    round(float(item.get("lon", 0.0)), 6),
                    (item.get("category") or "unknown").lower(),
                )
                if item_key == query_key:
                    continue
                boost = scenic_boost(item)
                final_score = alpha * max(0.0, min(1.0, cosine)) + (1.0 - alpha) * boost
                scored.append((item, final_score))

            scored.sort(key=lambda pair: pair[1], reverse=True)
            top_hits = scored[:topk_each]
            results.append(
                {
                    "query_name": name,
                    "query_lonlat": lonlat,
                    "results": [
                        {
                            "name": poi.get("name"),
                            "lonlat": [float(poi.get("lon", 0.0)), float(poi.get("lat", 0.0))],
                            "score": float(score),
                            "category": poi.get("category") or "unknown",
                            "tags": poi.get("tags") or {},
                        }
                        for poi, score in top_hits
                    ],
                }
            )
        return results


__all__ = ["SimilarPOIFinder"]

