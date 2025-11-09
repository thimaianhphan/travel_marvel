"""
HTTP caching utilities for external geodata services.

These helpers wrap `requests` calls with a persistent on-disk cache using
`diskcache` so we avoid re-fetching the same responses during experimentation.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Tuple

import requests
from diskcache import Cache

from backend.services.alternatives_discovery.config import (
    CACHE_ROOT,
    DEFAULT_REQUEST_DELAY,
    DEFAULT_REQUEST_TIMEOUT,
    REQUEST_USER_AGENT,
)

_CACHE_DIRECTORY = Path(CACHE_ROOT) / "http"
_CACHE_DIRECTORY.mkdir(parents=True, exist_ok=True)

HTTP_CACHE = Cache(str(_CACHE_DIRECTORY))


def _make_key(
    method: str,
    url: str,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Any] = None,
) -> Tuple[str, str, Tuple[Tuple[str, Any], ...], Optional[str]]:
    ordered_params: Iterable[Tuple[str, Any]] = ()
    if params:
        ordered_params = tuple(sorted(params.items()))
    serialized_data: Optional[str] = None
    if data is not None:
        if isinstance(data, (str, bytes)):
            serialized_data = data if isinstance(data, str) else data.decode("utf-8", "ignore")
        else:
            serialized_data = json.dumps(data, sort_keys=True)
    return method.upper(), url, tuple(ordered_params), serialized_data


def cached_get(
    url: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    ttl: int = 24 * 60 * 60,
    timeout: Optional[float] = None,
) -> Any:
    """
    Execute a cached HTTP GET request.

    Args:
        url: Target URL.
        params: Optional query parameters.
        ttl: Cache lifetime in seconds (default: 24h).
        timeout: Optional individual request timeout.
    """
    key = _make_key("GET", url, params=params)
    if key in HTTP_CACHE:
        return HTTP_CACHE[key]

    timeout = timeout or DEFAULT_REQUEST_TIMEOUT
    response = requests.get(
        url,
        params=params,
        headers={"User-Agent": REQUEST_USER_AGENT},
        timeout=timeout,
    )
    if response.status_code in (403, 429):
        # Simple retry with backoff — keep polite for public services
        time.sleep(1.0)
        response = requests.get(
            url,
            params=params,
            headers={"User-Agent": REQUEST_USER_AGENT},
            timeout=timeout,
        )
    response.raise_for_status()
    payload = response.json()
    HTTP_CACHE.set(key, payload, expire=ttl)
    # Respect public API rate limits with a short delay
    time.sleep(DEFAULT_REQUEST_DELAY)
    return payload


def cached_post(
    url: str,
    data: Any,
    *,
    ttl: int = 24 * 60 * 60,
    timeout: Optional[float] = None,
) -> Any:
    """
    Execute a cached HTTP POST request.

    Args:
        url: Target URL.
        data: Request body (dict or str).
        ttl: Cache lifetime in seconds (default: 24h).
        timeout: Optional request timeout.
    """
    key = _make_key("POST", url, data=data)
    if key in HTTP_CACHE:
        return HTTP_CACHE[key]

    timeout = timeout or DEFAULT_REQUEST_TIMEOUT
    response = requests.post(
        url,
        data=data,
        headers={"User-Agent": REQUEST_USER_AGENT},
        timeout=timeout,
    )
    response.raise_for_status()
    payload = response.json()
    HTTP_CACHE.set(key, payload, expire=ttl)
    time.sleep(DEFAULT_REQUEST_DELAY)
    return payload


__all__ = ["HTTP_CACHE", "cached_get", "cached_post"]

