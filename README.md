# travel_marvel

# Travel-MVP: POI Lookup + Similarity (with EU Space Data)

This repo turns a viral travel video into **local places you can actually visit**.
It has two core pieces:

1. **`poi_lookup`** — take a *name* (“Königssee”, “Kvernufoss”) and turn it into a **real place** with coords, category, tags, and a short scenic description.
2. **`similarity`** — given that place, find **3–5 similar local alternatives** (within ~200 km of the user) using embeddings + FAISS, with optional Copernicus boosts.

It’s modular, production-minded, and avoids embedding proper names (to prevent name-leakage bias).

---

## How it fits together

```
video transcript → POI names
                ↓
poi_lookup  (resolve: name → lat/lon + tags + scenic desc)
                ↓
similarity   (find locals: FAISS semantic + optional Copernicus features)
                ↓
routing/UI   (your code: routes, maps, “Places like in the video” panel)
```

---

# 1) `poi_lookup` — Resolve text → real place

**Goal:** Return a *clean, normalized dict* that downstream code can trust.

**Output (per POI):**

```json
{
  "name": "Königssee",
  "lat": 47.5551,
  "lon": 12.9766,
  "category": "lake",
  "tags": { "natural": "water", "water": "lake", "boundary": "protected_area", ... },
  "desc": "A lake, within a protected national park, surrounded by towering mountains, renowned for its clear, emerald-toned waters, with a long, fjord-like basin. Forest-lined slopes create a serene atmosphere."
}
```

**What it does:**

* **Nominatim (OSM)** to geocode the name.
* **Overpass** to fetch richer **OSM tags**.
* **Category inference** from tags (includes both encodings for waterfalls, lake subtypes, etc.).
* **Scenic description** (1–2 sentences, name-free) using OSM/Wikidata evidence, with optional **EU-DEM** hint for mountainous terrain.

  * Ignores terse/technical OSM descriptions.
  * Stays short (≈25–45 words) and factual; no purple prose.

> Why name-free? We feed this desc into the embedding model; removing the name prevents accidental boosting of “similar names” instead of “similar places.”

---

# 2) `similarity` — Find local alternatives (3–5)

**Goal:** For each resolved POI, return nearby places with **the same vibe**.

**Rules baked in:**

* **No name** in embedding (names only in output for UI).
* **Soft category match** (e.g., lake ≈ lagoon/reservoir/fjord).
* **≤ 200 km** from the **user** (configurable).
* Semantic retrieval via **`intfloat/e5-small-v2`** → **FAISS cosine**.
* Optional **EU Space data** for a small scenic boost (relief/protection/clarity).

**Output (per query POI):**

```json
{
  "query_name": "Königssee",
  "query_lonlat": [12.9766, 47.5551],
  "results": [
    { "name": "Chiemsee",   "lonlat": [12.4744, 47.8811], "score": 0.65, "category": "lake" },
    { "name": "Walchensee", "lonlat": [11.3056, 47.5933], "score": 0.63, "category": "lake" },
    { "name": "Tegernsee",  "lonlat": [11.7587, 47.7120], "score": 0.63, "category": "lake" }
  ]
}
```

**Embedding text (what we actually embed):**

```
"[CATEGORY: lake] [TAGS: natural=water; protected_area=yes] — 
surrounded by towering mountains; emerald-clear water; fjord-like basin; forest-lined shores; serene atmosphere."
```

**Why scores look close:** cosine for semantically similar short texts is naturally clustered. If you need stronger separation later, add a reranker (see “Roadmap”).

---

# Why EU Space data (Copernicus, etc.)?

OpenStreetMap tells us *what* a place is. EU Space data helps estimate *how it feels*:

* **EU-DEM (Copernicus)** → terrain relief: “towering mountains” vs flat.
* **Sentinel-2** →

  * **NDWI** (G vs NIR) as a **water clarity** proxy
  * **NDVI** (NIR vs Red) as **greenness**
* **CLC / protected areas** → **naturalness** / “inside a national park”.

These signals are ideal as **numeric features** in a second stage (boost/rerank). We already expose them via `features.py` so you can blend them into your scoring when ready.

---

# Does AI/ML come into play?

Yes—at several layers:

* **Sentence-transformer embeddings** (`e5-small-v2`) for semantic similarity of places.

  * We embed **category + curated tags + scenic description** (no names).
* **FAISS** for fast vector search.
* **(Optional) Cross-encoder reranker** (future): rescore the FAISS top-k for sharper precision.
* **(Optional) Learned scenic model**: combine EU-DEM/NDVI/NDWI/Natura-2000 features with a tiny classifier/regressor for a data-driven beauty score.

The rest is deterministic plumbing (OSM/Wikidata fetch, category rules, distance filters).

---

## Setup

### Environment

Create `.env` (or real env vars):

```
# Embedding model – use local path for fast startup
EMBED_MODEL_PATH=./models/e5-small-v2
EMBED_MODEL_FALLBACK=intfloat/e5-small-v2

# Copernicus WMTS/WMS (optional, graceful if unset)
COPERNICUS_EUDEM_WMTS=https://<your-eudem-wmts-or-wms>
COPERNICUS_TOKEN=<if-required>

# Sentinel-2 WMTS (prefer single-band; otherwise True Color)
S2_WMTS_B03=https://<wmts>/wms
S2_WMTS_B04=https://<wmts>/wms
S2_WMTS_B08=https://<wmts>/wms
# or (fallback)
S2_WMTS_TRUECOLOR=https://<wmts>/wms
```

---

## Usage

### 1) Resolve POIs

```python
from poi_lookup import batch_resolve

video_pois = [
  {"name": "Königssee", "hint": "lake"},
  {"name": "Kvernufoss", "hint": "waterfall"},
]
resolved = batch_resolve(video_pois)
```

### 2) Build similarity index & query

```python
from similarity import SimilarPOIFinder

finder = SimilarPOIFinder(alpha=0.7, radius_km=200)
finder.build_index(regional_pois, user_center=(47.63, 13.00))
alts = finder.find_for_video_pois(resolved, topk_each=5)
```

### 3) (Optional) Compute EU features for diagnostics

```python
from features import compute_features
print(compute_features(resolved[0]))  # {'relief_norm':..., 'water_clarity':..., ...}
```

---

## Notes & guarantees

* **No crashes on rate limits**: polite Nominatim usage (custom UA, delay, caching).
* **Deterministic outputs**: `poi_lookup` always returns the same 6 keys; `desc` is short and scenic.
* **Spatial constraints**: similarity always respects the **≤ 200 km** user radius you set when building the index.
* **Name-free embeddings**: avoids the “same-name == similar” trap.

---

## Roadmap (nice-to-haves)

* **Cross-encoder reranking** (e.g., `cross-encoder/ms-marco-MiniLM-L-6-v2`) for better top-5 separation.
* **Corridor filtering**: if you have A→B route, replace radius with a **buffered corridor**.
* **Shoreline geometry shape**: Overpass `out geom` → elongation / tortuosity to detect fjord-like lakes more reliably.
* **Seasonality**: Sentinel-2 recent tiles + local weather to avoid suggesting snow-covered passes in winter.
* **Tiny learned scorer** for “beauty” trained on editorial pairs.

---

## Compliance & data hygiene

* Respect **Nominatim** usage policy (custom UA, throttling).
* Cache responses; don’t hammer public infra.
* **Copernicus/Sentinel** endpoints differ by provider; keep your tokens secret.
* This project doesn’t store PII; only public geodata + EO features.

---

## FAQ

**Q: Why are similarity scores close (e.g., 0.63 vs 0.65)?**
A: Cosine for short, similar texts naturally clusters. Use reranking or feature blending for more separation.

**Q: Can I skip `poi_lookup` if I already have lat/lon?**
A: For a demo, yes—just build the input dict yourself. In production, you’ll need lookup to handle arbitrary video POI names.

**Q: Do I need Copernicus to run?**
A: No. If WMTS envs are unset, the EO features degrade gracefully to 0. It still works on embeddings alone.
