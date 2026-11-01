from datetime import UTC, datetime, timedelta

import redis.asyncio as aioredis
from app.core.tz_utils import _parse_offset
from app.logic.rules import rule

# Back-compat alias — value comes from app/logic/rules.json
FREE_DAILY_LIMIT = int(rule("ai.free_daily_limit", 5))


class AiRateLimiter:
    def __init__(self, redis_url: str) -> None:
        self._client: aioredis.Redis = aioredis.from_url(redis_url, decode_responses=True)
        self._limit = int(rule("ai.free_daily_limit", 5))

    @staticmethod
    def _local_now(tz: str | None) -> datetime:
        return datetime.now(UTC) + timedelta(hours=_parse_offset(tz))

    def _key(self, telegram_id: int, tz: str | None = None) -> str:
        today = self._local_now(tz).strftime("%Y-%m-%d")
        return f"ai_rl:{telegram_id}:{today}"

    def _ttl_to_midnight(self, tz: str | None = None) -> int:
        now = self._local_now(tz)
        tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        # +1h grace so the key outlives the local day boundary on clock skew
        return max(1, int((tomorrow - now).total_seconds())) + 3600

    async def reserve(self, telegram_id: int, tz: str | None = None) -> bool:
        """Atomically take one slot. INCR is atomic, so parallel callers can never
        collectively exceed the limit; an over-limit INCR is rolled back at once."""
        key = self._key(telegram_id, tz)
        n = await self._client.incr(key)
        if n == 1:
            await self._client.expire(key, self._ttl_to_midnight(tz))
        if n > self._limit:
            await self._client.decr(key)
            return False
        return True

    async def release(self, telegram_id: int, tz: str | None = None) -> None:
        """Give a reserved slot back (AI failed). Never goes below zero."""
        key = self._key(telegram_id, tz)
        if await self._client.decr(key) < 0:
            await self._client.set(key, 0)

    async def is_allowed(self, telegram_id: int, tz: str | None = None) -> bool:
        count = await self._client.get(self._key(telegram_id, tz))
        return count is None or int(count) < self._limit

    async def increment(self, telegram_id: int, tz: str | None = None) -> None:
        key = self._key(telegram_id, tz)
        pipe = self._client.pipeline()
        pipe.incr(key)
        pipe.expire(key, self._ttl_to_midnight(tz))
        await pipe.execute()

    async def remaining(self, telegram_id: int, tz: str | None = None) -> int:
        count = await self._client.get(self._key(telegram_id, tz))
        used = int(count) if count else 0
        return max(0, self._limit - used)

    async def reset(self, telegram_id: int, tz: str | None = None) -> None:
        await self._client.delete(self._key(telegram_id, tz))
