"""Conversion funnel on unique users: paywall -> plans -> invoice -> paid.

One HyperLogLog per stage per UTC day (~12 KB each, 120-day TTL). ``PFCOUNT`` over several
keys is a true union, so a user seen on two days counts once in a window. Metrics must never
break the bot: every Redis failure is swallowed.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)

STAGES = ("paywall", "plans", "invoice", "paid")
TTL_SEC = 120 * 86400
_funnel: Funnel | None = None


class Funnel:
    def __init__(self, client: Any) -> None:
        self._client = client

    @staticmethod
    def _key(stage: str, day: datetime, variant: str | None = None) -> str:
        v = f":{variant}" if variant else ""
        return f"pepito:funnel:{stage}{v}:{day:%Y-%m-%d}"

    async def track(
        self, stage: str, user_id: int, now: datetime | None = None, variant: str | None = None
    ) -> None:
        if stage not in STAGES:
            raise ValueError(f"unknown funnel stage: {stage}")
        day = now or datetime.now(UTC)
        try:
            # overall counter always; per-variant counter only when an A/B variant is known
            for key in (
                {self._key(stage, day), self._key(stage, day, variant)}
                if variant
                else {self._key(stage, day)}
            ):
                await self._client.pfadd(key, str(user_id))
                await self._client.expire(key, TTL_SEC)
        except Exception:
            logger.debug("funnel track failed", exc_info=True)

    async def summary(
        self, days: int, now: datetime | None = None, variant: str | None = None
    ) -> dict[str, int]:
        now = now or datetime.now(UTC)
        out = dict.fromkeys(STAGES, 0)
        try:
            for stage in STAGES:
                keys = [self._key(stage, now - timedelta(days=i), variant) for i in range(days)]
                out[stage] = int(await self._client.pfcount(*keys))
        except Exception:
            logger.debug("funnel summary failed", exc_info=True)
            return dict.fromkeys(STAGES, 0)
        return out


def _pct(a: int, b: int) -> float:
    return round(a / b * 100, 1) if b else 0.0


def conversion_rates(s: dict[str, int]) -> dict[str, float]:
    return {
        "plans_from_paywall": _pct(s["plans"], s["paywall"]),
        "invoice_from_plans": _pct(s["invoice"], s["plans"]),
        "paid_from_invoice": _pct(s["paid"], s["invoice"]),
        "paid_from_paywall": _pct(s["paid"], s["paywall"]),
    }


def get_funnel() -> Funnel:
    global _funnel
    if _funnel is None:
        import redis.asyncio as aioredis
        from app.core.config import settings

        _funnel = Funnel(aioredis.from_url(settings.REDIS_URL))
    return _funnel


def track_soon(stage: str, user_id: int | None) -> None:
    """Fire-and-forget from sync or async code; silent without a loop or a user."""
    if not user_id:
        return
    try:
        from app.core.tasks import spawn
        from app.services.pricing import ab_enabled, variant_for

        variant = variant_for(user_id) if ab_enabled() else None
        spawn(get_funnel().track(stage, user_id, variant=variant), name=f"funnel:{stage}")
    except RuntimeError:
        pass  # no running event loop (e.g. a sync unit test)
