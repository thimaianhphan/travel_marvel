import hashlib, json, pathlib, time, os
from typing import Any, Optional
import numpy as np
import diskcache  # pip install diskcache
import atexit
import logging

logger = logging.getLogger(__name__)

CACHE_DIR = pathlib.Path(__file__).resolve().parents[1] / ".cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Initialize cache with retry logic to handle file locks during hot-reload
_cache_instance = None
_cache_path = str(CACHE_DIR / "kv")

def _get_cache():
    """Get or create cache instance with retry logic for file locks."""
    global _cache_instance
    if _cache_instance is not None:
        return _cache_instance
    
    # Try to create cache, with retry on lock errors
    max_retries = 3
    for attempt in range(max_retries):
        try:
            _cache_instance = diskcache.Cache(_cache_path, size_limit=2**30)  # 1GB limit
            # Register cleanup on exit
            atexit.register(_cleanup_cache)
            return _cache_instance
        except (OSError, PermissionError) as e:
            if attempt < max_retries - 1:
                logger.warning(f"Cache initialization failed (attempt {attempt+1}/{max_retries}): {e}. Retrying...")
                time.sleep(0.5 * (attempt + 1))  # Exponential backoff
            else:
                logger.error(f"Failed to initialize cache after {max_retries} attempts: {e}")
                # Fallback: create a temporary cache in a different location
                fallback_path = str(CACHE_DIR / "kv_fallback")
                _cache_instance = diskcache.Cache(fallback_path, size_limit=2**30)
                atexit.register(_cleanup_cache)
                return _cache_instance

def _cleanup_cache():
    """Clean up cache on exit."""
    global _cache_instance
    if _cache_instance is not None:
        try:
            _cache_instance.close()
        except Exception as e:
            logger.debug(f"Error closing cache: {e}")
        _cache_instance = None

# Lazy initialization - cache is created on first use
def DC():
    """Get cache instance (lazy initialization)."""
    return _get_cache()

SCORER_VERSION = "v1.0"  # bump when you change scoring

def norm_coords(coords):
    return [[round(float(lon), 5), round(float(lat), 5)] for lon, lat in coords]

def route_key(coords, profile: str, buffer_m: int, res_m: int, extra: dict | None = None) -> str:
    payload = {
        "coords": norm_coords(coords),
        "profile": profile,
        "buffer_m": buffer_m,
        "res_m": res_m,
        "v": SCORER_VERSION,
        "extra": extra or {},
    }
    s = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha1(s.encode("utf-8")).hexdigest()

def mosaic_path(key: str) -> str:
    p = CACHE_DIR / "mosaics"
    p.mkdir(parents=True, exist_ok=True)
    return str(p / f"{key}.npz")

def save_mosaic_npz(key: str, rgb8: np.ndarray, scl: np.ndarray | None, transform: Any, crs: Any) -> str:
    path = mosaic_path(key)
    np.savez_compressed(path, rgb8=rgb8, scl=scl, transform=str(transform), crs=str(crs), ts=time.time())
    return path

def load_mosaic_npz(key: str):
    path = mosaic_path(key)
    if not os.path.exists(path): return None
    dat = np.load(path, allow_pickle=True)
    return dat["rgb8"], (dat["scl"] if "scl" in dat.files else None), dat["transform"].item(), dat["crs"].item()

# Small KV helpers with retry logic
def get_job(job_id: str):
    try:
        return DC().get(f"job:{job_id}")
    except Exception as e:
        logger.warning(f"Error getting job {job_id}: {e}")
        return None

def set_job(job_id: str, val, ttl):
    try:
        DC().set(f"job:{job_id}", val, expire=ttl)
    except Exception as e:
        logger.warning(f"Error setting job {job_id}: {e}")

def get_result(job_id: str):
    try:
        return DC().get(f"route:{job_id}")
    except Exception as e:
        logger.warning(f"Error getting result {job_id}: {e}")
        return None

def set_result(job_id: str, val):
    try:
        DC().set(f"route:{job_id}", val, expire=7*24*3600)
    except Exception as e:
        logger.warning(f"Error setting result {job_id}: {e}")