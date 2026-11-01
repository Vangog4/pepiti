from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.context import current_tg_id
from app.infrastructure.db.session import _session_var


class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        ctx_token = current_tg_id.set(getattr(user, "id", None))
        try:
            async with self.session_factory() as session:
                token = _session_var.set(session)
                try:
                    return await handler(event, data)
                finally:
                    _session_var.reset(token)
        finally:
            current_tg_id.reset(ctx_token)
