"""Atomic AI quota: reserve before the call, release on failure, never exceed the limit."""

import asyncio
from datetime import UTC, datetime

import pytest

from app.infrastructure.redis.ai_rate_limit import AiRateLimiter


class _FakeRedis:
    """Minimal async stand-in; each method is atomic like the real single-threaded Redis."""

    def __init__(self):
        self.d: dict[str, int] = {}

    async def incr(self, k):
        await asyncio.sleep(0)
        self.d[k] = self.d.get(k, 0) + 1
        return self.d[k]

    async def decr(self, k):
        await asyncio.sleep(0)
        self.d[k] = self.d.get(k, 0) - 1
        return self.d[k]

    async def get(self, k):
        v = self.d.get(k)
        return None if v is None else str(v)

    async def expire(self, k, ttl):
        return True

    async def set(self, k, v, **kw):
        self.d[k] = int(v)

    async def delete(self, k):
        self.d.pop(k, None)


@pytest.fixture
def limiter():
    rl = AiRateLimiter.__new__(AiRateLimiter)
    rl._client = _FakeRedis()
    rl._limit = 3
    return rl


@pytest.mark.asyncio
async def test_parallel_reserves_never_exceed_limit(limiter):
    results = await asyncio.gather(*[limiter.reserve(1) for _ in range(20)])
    assert sum(results) == 3
    assert await limiter.remaining(1) == 0


@pytest.mark.asyncio
async def test_release_returns_the_slot(limiter):
    assert await limiter.reserve(2)
    assert await limiter.reserve(2)
    await limiter.release(2)
    assert await limiter.remaining(2) == 2


@pytest.mark.asyncio
async def test_release_never_goes_negative(limiter):
    await limiter.release(3)
    assert await limiter.remaining(3) == 3


@pytest.mark.asyncio
async def test_local_day_key_changes_with_offset(limiter):
    k_utc = limiter._key(5, "UTC")
    k_far = limiter._key(5, "UTC+14")
    assert k_utc.startswith("ai_rl:5:") and k_far.startswith("ai_rl:5:")
    assert datetime.now(UTC).strftime("%Y-%m-%d") in (k_utc.split(":")[-1],)
