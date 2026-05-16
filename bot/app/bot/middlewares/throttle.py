from typing import Any, Awaitable, Callable

import redis.asyncio as aioredis
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update


class ThrottlingMiddleware(BaseMiddleware):
    _MSG_WINDOW_MS = 1000
    _CB_WINDOW_MS  = 500

    def __init__(self, redis_url: str, admin_ids: set[int]) -> None:
        self._redis = aioredis.from_url(redis_url)
        self._admin_ids = admin_ids

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        if event.message:
            user_id = event.message.from_user and event.message.from_user.id
            key_type, window_ms = "msg", self._MSG_WINDOW_MS
        elif event.callback_query:
            user_id = event.callback_query.from_user.id
            key_type, window_ms = "cb", self._CB_WINDOW_MS
        else:
            return await handler(event, data)

        if not user_id or user_id in self._admin_ids:
            return await handler(event, data)

        allowed = await self._redis.set(
            f"throttle:{key_type}:{user_id}", 1, nx=True, px=window_ms
        )
        if not allowed:
            if event.callback_query:
                await event.callback_query.answer()
            return

        return await handler(event, data)
