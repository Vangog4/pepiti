"""Unit tests for app/services/broadcast_service.run_broadcast — 4 cases."""
import asyncio
import sys
sys.path.insert(0, ".")

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.broadcast_service import run_broadcast


# ---------------------------------------------------------------------------
# Fake exception classes — avoid constructing real aiogram exception internals
# ---------------------------------------------------------------------------
class _Forbidden(Exception):
    pass


class _RetryAfter(Exception):
    def __init__(self, retry_after: int = 1):
        self.retry_after = retry_after


_PATCHES = dict(
    TelegramForbiddenError=_Forbidden,
    TelegramRetryAfter=_RetryAfter,
)


def _make_bot():
    bot = MagicMock()
    bot.send_message = AsyncMock()
    return bot


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_all_sent():
    """All IDs succeed: N user messages + 1 admin report sent."""
    bot = _make_bot()

    with patch("asyncio.sleep", new_callable=AsyncMock), \
         patch("app.services.broadcast_service.TelegramForbiddenError", _Forbidden), \
         patch("app.services.broadcast_service.TelegramRetryAfter", _RetryAfter):
        await run_broadcast(bot, [1, 2, 3], "Hello", admin_telegram_id=999)

    # 3 user sends + 1 admin completion report
    assert bot.send_message.call_count == 4


@pytest.mark.asyncio
async def test_forbidden_skipped():
    """User who blocked the bot is silently skipped; others still receive the message."""
    bot = _make_bot()

    async def _side(chat_id, **kw):
        if chat_id == 2:
            raise _Forbidden()

    bot.send_message = AsyncMock(side_effect=_side)

    with patch("asyncio.sleep", new_callable=AsyncMock), \
         patch("app.services.broadcast_service.TelegramForbiddenError", _Forbidden), \
         patch("app.services.broadcast_service.TelegramRetryAfter", _RetryAfter):
        await run_broadcast(bot, [1, 2, 3], "Hello", admin_telegram_id=999)

    # 3 attempts (one raised) + 1 admin report = 4 calls
    assert bot.send_message.call_count == 4
    report_text = bot.send_message.call_args_list[-1].kwargs.get("text", "")
    assert "2" in report_text   # 2 sent
    assert "1" in report_text   # 1 failed


@pytest.mark.asyncio
async def test_retry_after_then_success():
    """RetryAfter causes sleep(retry_after) then one successful retry."""
    bot = _make_bot()
    _retried = {"done": False}

    async def _side(chat_id, **kw):
        if chat_id == 2 and not _retried["done"]:
            _retried["done"] = True
            raise _RetryAfter(retry_after=5)

    bot.send_message = AsyncMock(side_effect=_side)

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep, \
         patch("app.services.broadcast_service.TelegramForbiddenError", _Forbidden), \
         patch("app.services.broadcast_service.TelegramRetryAfter", _RetryAfter):
        await run_broadcast(bot, [1, 2], "Hello", admin_telegram_id=999)

    # id=1 once + id=2 twice (initial raise + retry) + admin report = 4 calls
    assert bot.send_message.call_count == 4
    mock_sleep.assert_any_call(5)


@pytest.mark.asyncio
async def test_empty_list():
    """No IDs: only the admin completion report is sent."""
    bot = _make_bot()

    with patch("asyncio.sleep", new_callable=AsyncMock), \
         patch("app.services.broadcast_service.TelegramForbiddenError", _Forbidden), \
         patch("app.services.broadcast_service.TelegramRetryAfter", _RetryAfter):
        await run_broadcast(bot, [], "Hello", admin_telegram_id=999)

    assert bot.send_message.call_count == 1
    report_text = bot.send_message.call_args_list[0].kwargs.get("text", "")
    assert "0" in report_text
