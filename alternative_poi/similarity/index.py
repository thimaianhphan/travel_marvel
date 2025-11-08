import hashlib, numpy as np, faiss
from typing import List, Dict
from diskcache import Cache
from sentence_transformers import SentenceTransformer

CACHE = Cache("./.cache/faiss")

def _hash(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]

class TextIndex:
    def __init__(self, model: SentenceTransformer):
        self.model = model
        self.dim = model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatIP(self.dim)
        self.meta: List[Dict] = []

    def _embed(self, texts: List[str]) -> np.ndarray:
        out = [None]*len(texts)
        to_compute = []
        idxs = []
        for i,t in enumerate(texts):
            key=("EMB",_hash(t))
            if key in CACHE: out[i]=CACHE[key]
            else: to_compute.append(t); idxs.append(i)
        if to_compute:
            X = self.model.encode(to_compute, batch_size=256, normalize_embeddings=True, show_progress_bar=False).astype("float32")
            for j,i in enumerate(idxs):
                out[i]=X[j]; CACHE.set(("EMB",_hash(texts[i])), X[j], expire=30*86400)
        return np.vstack(out).astype("float32")

    def add(self, items: List[Dict], texts: List[str]):
        X = self._embed(texts)
        self.index.add(X)
        self.meta.extend(items)

    def search(self, qtext: str, topn: int):
        q = self._embed([qtext])
        sims, idxs = self.index.search(q, topn)
        out=[]
        for s,i in zip(sims[0], idxs[0]):
            if i<0: continue
            out.append((self.meta[i], float(s)))
        return out
