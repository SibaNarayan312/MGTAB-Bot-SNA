import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class SimpleMemoryCache:
    """
    In-memory key-value cache with optional TTL expiration.
    Used by API services to instantly serve graph statistics,
    user metrics, communities, and network subgraphs.
    """

    def __init__(self, default_ttl: int = 3600):
        self._cache: Dict[str, Any] = {}
        self._expirations: Dict[str, float] = {}
        self.default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        if key not in self._cache:
            return None
        if time.time() > self._expirations.get(key, 0):
            self.delete(key)
            return None
        return self._cache[key]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        duration = ttl if ttl is not None else self.default_ttl
        self._cache[key] = value
        self._expirations[key] = time.time() + duration

    def delete(self, key: str) -> None:
        self._cache.pop(key, None)
        self._expirations.pop(key, None)

    def clear(self) -> None:
        self._cache.clear()
        self._expirations.clear()
