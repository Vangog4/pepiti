"""Unit tests for referral milestone notifications (Stage 11)."""
import sys
from unittest.mock import AsyncMock, MagicMock

import pytest

sys.path.insert(0, ".")

from app.services.referral_service import (
    ReferralAwardResult,
    REFERRAL_MILESTONES,
    notify_referrer,
    milestone_label,
    milestone_reward,
)


# ── dataclass structure ────────────────────────────────────────────────────────

def test_result_has_referrer_telegram_id():
    r = ReferralAwardResult()
    assert r.referrer_telegram_id is None


def test_result_has_referrer_lang_default():
    r = ReferralAwardResult()
    assert r.referrer_lang == "ru"


def test_result_has_new_referral_count():
    r = ReferralAwardResult()
    assert r.new_referral_count == 0


# ── notify_referrer: no tid → early return ────────────────────────────────────

@pytest.mark.asyncio
async def test_notify_skips_when_no_tid():
    bot = MagicMock()
    bot.send_message = AsyncMock()
    result = ReferralAwardResult(base_awarded=True, referrer_telegram_id=None)
    await notify_referrer(bot, result, "ru")
    bot.send_message.assert_not_called()


# ── notify_referrer: base case (no milestone) ─────────────────────────────────

@pytest.mark.asyncio
async def test_notify_base_sends_message():
    bot = MagicMock()
    bot.send_message = AsyncMock()
    result = ReferralAwardResult(
        base_awarded=True,
        referrer_telegram_id=12345,
        new_referral_count=2,
        milestone=None,
    )
    await notify_referrer(bot, result, "ru")
    bot.send_message.assert_called_once()
    call_kwargs = bot.send_message.call_args
    assert call_kwargs[0][0] == 12345          # chat_id
    sent_text = call_kwargs[0][1] if len(call_kwargs[0]) > 1 else call_kwargs[1].get("text", "")
    # base notify mentions count
    assert "2" in sent_text


# ── notify_referrer: milestone reached ────────────────────────────────────────

@pytest.mark.asyncio
async def test_notify_milestone_sends_milestone_text():
    bot = MagicMock()
    bot.send_message = AsyncMock()
    milestone = REFERRAL_MILESTONES[0]  # 3 friends → +7 days
    result = ReferralAwardResult(
        base_awarded=True,
        referrer_telegram_id=99,
        new_referral_count=3,
        milestone=milestone,
    )
    await notify_referrer(bot, result, "ru")
    bot.send_message.assert_called_once()
    sent_text = bot.send_message.call_args[0][1] if len(bot.send_message.call_args[0]) > 1 \
        else bot.send_message.call_args[1].get("text", "")
    assert milestone_label(milestone, "ru") in sent_text
    assert milestone_reward(milestone, "ru") in sent_text


@pytest.mark.asyncio
async def test_notify_last_milestone_shows_all_done():
    """When the top tier is reached, the text contains 'all done' hint (no next goal)."""
    bot = MagicMock()
    bot.send_message = AsyncMock()
    last = REFERRAL_MILESTONES[-1]  # 25 friends → +90 days
    result = ReferralAwardResult(
        base_awarded=True,
        referrer_telegram_id=7,
        new_referral_count=25,
        milestone=last,
    )
    await notify_referrer(bot, result, "ru")
    sent_text = bot.send_message.call_args[0][1] if len(bot.send_message.call_args[0]) > 1 \
        else bot.send_message.call_args[1].get("text", "")
    # Should NOT contain a "next goal" since this is the final milestone
    assert "Следующая цель" not in sent_text
    assert "Все награды" in sent_text


# ── notify_referrer: exception → silent skip ──────────────────────────────────

@pytest.mark.asyncio
async def test_notify_forbidden_silently_skipped():
    """Any exception (e.g. user blocked the bot) must not propagate."""
    bot = MagicMock()
    bot.send_message = AsyncMock(side_effect=Exception("Forbidden: bot was blocked by the user"))
    result = ReferralAwardResult(
        base_awarded=True,
        referrer_telegram_id=42,
        new_referral_count=1,
        milestone=None,
    )
    # Must not raise
    await notify_referrer(bot, result, "ru")
