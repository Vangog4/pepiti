"""Fire-and-forget tasks that cannot be garbage-collected mid-flight and never fail silently."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Coroutine
from typing import Any

logger = logging.getLogger(__name__)
_tasks: set[asyncio.Task] = set()


def spawn(coro: Coroutine[Any, Any, Any], name: str | None = None) -> asyncio.Task:
    """Schedule ``coro`` and keep a strong reference until it finishes.

    The event loop only holds weak references to tasks, so a bare ``create_task``
    can be collected and cancelled before it completes.
    """
    task = asyncio.get_running_loop().create_task(coro, name=name)
    _tasks.add(task)
    task.add_done_callback(_done)
    return task


def _done(task: asyncio.Task) -> None:
    _tasks.discard(task)
    if task.cancelled():
        return
    exc = task.exception()
    if exc is not None:
        logger.error("background task %s failed: %r", task.get_name(), exc, exc_info=exc)
