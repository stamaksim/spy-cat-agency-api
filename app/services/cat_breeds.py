"""
TheCatAPI breed validation helper.

We validate a cat's breed against TheCatAPI `/v1/breeds` endpoint.
To avoid calling the external API on every request, we cache the set of breed
names in memory for a configurable TTL.
"""

import time

import httpx

from app.core.config import settings

# In-memory cache of normalized breed names (lowercased, trimmed).
_CACHE: set[str] | None = None

# Unix timestamp (seconds) when the cache was last refreshed.
_CACHE_TS: float = 0.0


async def _fetch_breeds() -> set[str]:
    """
    Fetch all breed names from TheCatAPI.

    Returns:
        A set of normalized breed names (lowercased, trimmed).

    Raises:
        httpx.HTTPError: If the request fails or returns non-2xx status.
    """
    headers: dict[str, str] = {}
    if settings.thecatapi_key:
        headers["x-api-key"] = settings.thecatapi_key

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get("https://api.thecatapi.com/v1/breeds", headers=headers)
        response.raise_for_status()
        data = response.json()

    # TheCatAPI returns a list of objects with "name" as the breed label.
    return {
        item["name"].strip().lower() for item in data if isinstance(item, dict) and item.get("name")
    }


async def validate_breed(breed: str) -> bool:
    """
    Validate a breed name using TheCatAPI with TTL caching.

    The function uses an in-memory cache to reduce third-party API calls.

    Args:
        breed: The breed name provided by the user.

    Returns:
        True if the breed exists in TheCatAPI list, otherwise False.

    Notes:
        - If TheCatAPI is rate-limited or temporarily unavailable, your API layer
          may choose to return 400 (invalid breed) or 503 (validation service unavailable).
          This function simply raises on request failure; the caller decides how to respond.
    """
    global _CACHE, _CACHE_TS

    normalized = breed.strip().lower()
    now = time.time()

    cache_expired = (_CACHE is None) or ((now - _CACHE_TS) > settings.breed_cache_ttl_seconds)
    if cache_expired:
        _CACHE = await _fetch_breeds()
        _CACHE_TS = now

    # `_CACHE` is guaranteed to be a set here, because we refresh if it's None.
    return normalized in _CACHE  # type: ignore[operator]
