import json
from datetime import datetime, timezone

import redis.asyncio as aioredis

_KEY = "pepito:admin:actions"
_MAX_ENTRIES = 100


class AdminLog:
    def __init__(self, redis_url: str) -> None:
        self._client = aioredis.from_url(redis_url, decode_responses=True)

    async def log(self, admin_id: int, action: str, target: str = "", detail: str = "") -> None:
        entry = json.dumps({
            "ts": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"),
            "admin": admin_id,
            "action": action,
            "target": target,
            "detail": detail,
        })
        pipe = self._client.pipeline()
        pipe.lpush(_KEY, entry)
        pipe.ltrim(_KEY, 0, _MAX_ENTRIES - 1)
        await pipe.execute()

    async def get_recent(self, n: int = 30) -> list[dict]:
        entries = await self._client.lrange(_KEY, 0, n - 1)
        result = []
        for e in entries:
            try:
                result.append(json.loads(e))
            except Exception:
                pass
        return result
