import time

import redis.asyncio as aioredis


class BotMetrics:
    """Global Redis counters for bot observability. No TTL — cumulative totals."""

    MARK_DONE    = "pepito:metrics:va_mark_done"
    PREMIUM_GATE = "pepito:metrics:va_premium_gate"
    FALLBACK     = "pepito:metrics:va_fallback"

    PREMIUM_SCREEN  = "pepito:metrics:premium_screen"
    PREMIUM_CLICK   = "pepito:metrics:premium_click"
    REFERRAL_SCREEN = "pepito:metrics:referral_screen"
    SHARE_CLICK     = "pepito:metrics:share_click"
    COPY_CLICK      = "pepito:metrics:copy_click"

    CAMPAIGNS_SET   = "pepito:bc_campaigns"

    def __init__(self, redis_url: str) -> None:
        self._client: aioredis.Redis = aioredis.from_url(redis_url, decode_responses=True)

    async def inc(self, key: str) -> None:
        await self._client.incr(key)

    async def get_voice_stats(self) -> dict:
        pipe = self._client.pipeline()
        pipe.get(self.MARK_DONE)
        pipe.get(self.PREMIUM_GATE)
        pipe.get(self.FALLBACK)
        results = await pipe.execute()
        return {
            "va_mark_done":    int(results[0] or 0),
            "va_premium_gate": int(results[1] or 0),
            "va_fallback":     int(results[2] or 0),
        }

    async def create_campaign(
        self, camp_id: str, url: str, button_text: str, sent: int
    ) -> None:
        pipe = self._client.pipeline()
        pipe.hset(f"pepito:bc:{camp_id}", mapping={
            "url":         url,
            "button_text": button_text,
            "sent":        str(sent),
            "clicks":      "0",
            "created":     str(int(time.time())),
        })
        pipe.sadd(self.CAMPAIGNS_SET, camp_id)
        await pipe.execute()

    async def track_click(self, camp_id: str) -> str | None:
        """Increment click counter. Returns target URL, or None if campaign not found."""
        key = f"pepito:bc:{camp_id}"
        url = await self._client.hget(key, "url")
        if not url:
            return None
        await self._client.hincrby(key, "clicks", 1)
        return url

    async def get_all_campaigns(self) -> list[dict]:
        camp_ids = await self._client.smembers(self.CAMPAIGNS_SET)
        if not camp_ids:
            return []
        cids = sorted(camp_ids)
        pipe = self._client.pipeline()
        for cid in cids:
            pipe.hgetall(f"pepito:bc:{cid}")
        results = await pipe.execute()
        campaigns = []
        for cid, data in zip(cids, results):
            if not data:
                continue
            sent   = int(data.get("sent",   0))
            clicks = int(data.get("clicks", 0))
            campaigns.append({
                "camp_id":     cid,
                "url":         data.get("url", ""),
                "button_text": data.get("button_text", ""),
                "sent":        sent,
                "clicks":      clicks,
                "ctr":         round(clicks / sent * 100, 1) if sent else 0.0,
                "created":     int(data.get("created", 0)),
            })
        campaigns.sort(key=lambda x: x["created"], reverse=True)
        return campaigns

    async def get_growth_counters(self) -> dict:
        pipe = self._client.pipeline()
        pipe.get(self.PREMIUM_SCREEN)
        pipe.get(self.PREMIUM_CLICK)
        pipe.get(self.REFERRAL_SCREEN)
        pipe.get(self.SHARE_CLICK)
        pipe.get(self.COPY_CLICK)
        r = await pipe.execute()
        share = int(r[3] or 0)
        copy  = int(r[4] or 0)
        return {
            "premium_screen":     int(r[0] or 0),
            "premium_click":      int(r[1] or 0),
            "referral_screen":    int(r[2] or 0),
            "share_click":        share,
            "copy_click":         copy,
            "share_intent_total": share + copy,
        }
