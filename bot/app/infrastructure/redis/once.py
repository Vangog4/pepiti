"""Send-at-most-once guard for notifications."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class OnceGuard:
    """``first(key)`` is True exactly once per key within the TTL.

    Fails CLOSED: if Redis is unreachable we report "not first", so a Redis outage can
    delay a reminder but can never make the bot message people repeatedly.
    """

    def __init__(self, client: Any) -> None:
        self._client = client

    async def first(self, key: str, ttl_sec: int) -> bool:
        try:
            return bool(await self._client.set(f"once:{key}", 1, nx=True, ex=ttl_sec))
        except Exception:
            logger.warning("OnceGuard: redis unavailable, skipping %s", key)
            return False
