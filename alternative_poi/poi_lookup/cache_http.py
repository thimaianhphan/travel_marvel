import json, time, requests
from diskcache import Cache
from .config import USER_AGENT

CACHE = Cache("./.cache/osm")

def cached_get(url, params=None, ttl=86400):
    key = ("GET", url, tuple(sorted((params or {}).items())))
    if key in CACHE:
        return CACHE[key]
    r = requests.get(url, params=params, headers={"User-Agent": USER_AGENT}, timeout=30)
    if r.status_code in (403, 429):
        time.sleep(1.2)
        r = requests.get(url, params=params, headers={"User-Agent": USER_AGENT}, timeout=30)
    r.raise_for_status()
    data = r.json()
    CACHE.set(key, data, expire=ttl)
    time.sleep(1.0)
    return data

def cached_post(url, data, ttl=86400):
    key = ("POST", url, json.dumps(data, sort_keys=True))
    if key in CACHE:
        return CACHE[key]
    r = requests.post(url, data=data, headers={"User-Agent": USER_AGENT}, timeout=60)
    r.raise_for_status()
    payload = r.json()
    CACHE.set(key, payload, expire=ttl)
    time.sleep(1.0)
    return payload
