"""Unit tests for ThrottlingMiddleware — 4 cases."""

import sys

sys.path.insert(0, ".")

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import redis.asyncio as aioredis

from app.bot.middlewares.throttle import ThrottlingMiddleware


# ── Helpers ────────────────────────────────────────────────────────────────────


def _mw(redis_mock, admin_ids=None):
    with patch.object(aioredis, "from_url", return_value=redis_mock):
        return ThrottlingMiddleware(
            redis_url="redis://fake",
            admin_ids=admin_ids if admin_ids is not None else set(),
        )


def _msg_update(uid: int = 100):
    u = MagicMock()
    u.message = MagicMock()
    u.message.from_user.id = uid
    u.callback_query = None
    return u


def _cb_update(uid: int = 100):
    u = MagicMock()
    u.message = None
    u.callback_query = MagicMock()
    u.callback_query.from_user.id = uid
    u.callback_query.answer = AsyncMock()
    return u


# ── Tests ──────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_first_message_allowed():
    """First message in window: Redis SET NX returns True → handler called."""
    redis_mock = AsyncMock()
    redis_mock.set = AsyncMock(return_value=True)
    handler = AsyncMock()

    mw = _mw(redis_mock)
    await mw(handler, _msg_update(), data={})

    handler.assert_awaited_once()
    redis_mock.set.assert_awaited_once()


@pytest.mark.asyncio
async def test_throttled_message_dropped():
    """Message within window: Redis SET NX returns None → handler NOT called."""
    redis_mock = AsyncMock()
    redis_mock.set = AsyncMock(return_value=None)
    handler = AsyncMock()

    mw = _mw(redis_mock)
    await mw(handler, _msg_update(), data={})

    handler.assert_not_awaited()


@pytest.mark.asyncio
async def test_throttled_callback_answers():
    """Throttled callback: answer() clears spinner; handler NOT called."""
    redis_mock = AsyncMock()
    redis_mock.set = AsyncMock(return_value=None)
    handler = AsyncMock()

    update = _cb_update()
    mw = _mw(redis_mock)
    await mw(handler, update, data={})

    handler.assert_not_awaited()
    update.callback_query.answer.assert_awaited_once()


@pytest.mark.asyncio
async def test_admin_bypasses():
    """Admin user always passes through; Redis.set is never called."""
    redis_mock = AsyncMock()
    redis_mock.set = AsyncMock(return_value=None)  # would throttle a regular user
    handler = AsyncMock()

    mw = _mw(redis_mock, admin_ids={100})
    await mw(handler, _msg_update(uid=100), data={})

    handler.assert_awaited_once()
    redis_mock.set.assert_not_awaited()
