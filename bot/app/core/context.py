"""Per-update context: who is acting. Set by DbSessionMiddleware, read by lightweight hooks."""

from contextvars import ContextVar

current_tg_id: ContextVar[int | None] = ContextVar("current_tg_id", default=None)
