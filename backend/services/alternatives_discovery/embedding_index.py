"""
Lightweight FAISS-backed text index for POI similarity search.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Dict, List, Optional

import faiss  # type: ignore
import numpy as np
from diskcache import Cache
from sentence_transformers import SentenceTransformer

from .config import FAISS_CACHE_DIR

_CACHE_DIR = Path(FAISS_CACHE_DIR)
_CACHE_DIR.mkdir(parents=True, exist_ok=True)
EMBED_CACHE = Cache(str(_CACHE_DIR))


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


class TextIndex:
    def __init__(self, model: SentenceTransformer):
        self.model = model
        self.dim = model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatIP(self.dim)
        self.meta: List[Dict] = []

    def _embed(self, texts: List[str]) -> np.ndarray:
        outputs: List[Optional[np.ndarray]] = [None] * len(texts)
        missing: List[str] = []
        missing_positions: List[int] = []

        for idx, text in enumerate(texts):
            key = ("EMB", _hash(text))
            if key in EMBED_CACHE:
                outputs[idx] = EMBED_CACHE[key]
            else:
                missing.append(text)
                missing_positions.append(idx)

        if missing:
            computed = self.model.encode(
                missing,
                batch_size=128,
                normalize_embeddings=True,
                show_progress_bar=False,
            ).astype("float32")
            for pos, vector in zip(missing_positions, computed):
                outputs[pos] = vector
                EMBED_CACHE.set(("EMB", _hash(texts[pos])), vector, expire=30 * 24 * 60 * 60)

        stack_inputs = []
        for vec in outputs:
            if vec is None:
                raise ValueError("Embedding computation failed for one or more texts.")
            stack_inputs.append(vec)
        return np.vstack(stack_inputs).astype("float32")

    def add(self, items: List[Dict], texts: List[str]) -> None:
        vectors = self._embed(texts)
        self.index.add(vectors)
        self.meta.extend(items)

    def search(self, query_text: str, topn: int):
        vector = self._embed([query_text])
        sims, idxs = self.index.search(vector, topn)
        results = []
        for score, idx in zip(sims[0], idxs[0]):
            if idx < 0 or idx >= len(self.meta):
                continue
            results.append((self.meta[idx], float(score)))
        return results


__all__ = ["TextIndex", "EMBED_CACHE"]

