from datetime import UTC, datetime, timedelta

import redis.asyncio as aioredis
from app.logic.rules import rule

# Back-compat alias — value comes from app/logic/rules.json
FREE_DAILY_LIMIT = int(rule("ai.free_daily_limit", 5))


class AiRateLimiter:
    def __init__(self, redis_url: str) -> None:
        self._client: aioredis.Redis = aioredis.from_url(redis_url, decode_responses=True)
        self._limit = int(rule("ai.free_daily_limit", 5))

    def _key(self, telegram_id: int) -> str:
        today = datetime.now(UTC).strftime("%Y-%m-%d")
        return f"ai_rl:{telegram_id}:{today}"

    def _ttl_to_midnight(self) -> int:
        now = datetime.now(UTC)
        tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        return max(1, int((tomorrow - now).total_seconds()))

    async def is_allowed(self, telegram_id: int) -> bool:
        count = await self._client.get(self._key(telegram_id))
        return count is None or int(count) < self._limit

    async def increment(self, telegram_id: int) -> None:
        key = self._key(telegram_id)
        pipe = self._client.pipeline()
        pipe.incr(key)
        pipe.expire(key, self._ttl_to_midnight())
        await pipe.execute()

    async def remaining(self, telegram_id: int) -> int:
        count = await self._client.get(self._key(telegram_id))
        used = int(count) if count else 0
        return max(0, self._limit - used)

    async def reset(self, telegram_id: int) -> None:
        await self._client.delete(self._key(telegram_id))
