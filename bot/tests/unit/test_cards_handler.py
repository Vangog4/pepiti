from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.bot.handlers import cards as ch
from app.bot.handlers.tracker import tracker_kb
from app.cards.render import render_card
from app.services.tracker import WeekSummary

LOCALES = ("ru", "en", "de", "es", "fr", "pt")


def snap(streak=3, badges=None, task_days=2, walks=1, minutes=30):
    return {
        "streak": streak,
        "badges": badges if badges is not None else {"streak_7"},
        "week": WeekSummary(task_days=task_days, walk_count=walks, walk_minutes=minutes),
    }


PET = SimpleNamespace(
    id=7,
    name="Рекс",
    breed="Лабрадор",
    age_category="Молодой (1–3 года)",
    weight_kg=28.5,
    allergies=["курица"],
)


def test_nothing_to_share_returns_none():
    assert ch.build_payload("streak", PET, snap(streak=0), "ru") is None
    assert ch.build_payload("badge", PET, snap(badges=set()), "ru") is None
    assert ch.build_payload("week", PET, snap(task_days=0, walks=0), "ru") is None
    assert ch.build_payload("nope", PET, snap(), "ru") is None


def test_badge_card_uses_highest_badge():
    kind, data = ch.build_payload(
        "badge", PET, snap(badges={"streak_7", "streak_30", "walks_10"}), "ru"
    )
    assert kind == "badge" and data["big"] == "30"


@pytest.mark.asyncio
@pytest.mark.parametrize("lang", LOCALES)
@pytest.mark.parametrize("kind", ch.KINDS)
async def test_every_card_renders_in_every_locale(kind, lang):
    payload = ch.build_payload(kind, PET, snap(), lang)
    png = await render_card(*payload, scale=0.25)  # small: 24 combos, layout is scale-free
    assert png[:8] == b"\x89PNG\r\n\x1a\n"


def test_share_buttons_fit_14_chars():
    for lg in LOCALES:
        row = tracker_kb(lg).inline_keyboard[1]
        assert [b.callback_data for b in row] == ["card:streak", "card:week", "card:badge"]
        assert all(len(b.text) <= 14 for b in row), lg


def _env(rows=(), pet=PET):
    usr = SimpleNamespace(
        id=1, language_code="ru", timezone="UTC", is_premium=False, subscription_expires_at=None
    )
    u_svc = MagicMock(get_or_create_telegram_user=AsyncMock(return_value=usr))
    p_svc = MagicMock(get_pet=AsyncMock(return_value=pet))
    repo = MagicMock(rows=AsyncMock(return_value=list(rows)))
    cb = MagicMock()
    cb.answer = AsyncMock()
    cb.from_user.id = 5
    cb.message.answer_document = AsyncMock()
    cb.message.answer = AsyncMock()
    return cb, u_svc, p_svc, repo


@pytest.mark.asyncio
async def test_sends_png_document_for_passport():
    cb, u, p, r = _env()
    cb.data = "card:passport"
    await ch.send_card.__wrapped__(cb, u, p, r)
    doc = cb.message.answer_document.await_args.args[0]
    assert doc.data[:8] == b"\x89PNG\r\n\x1a\n" and doc.filename == "pepito-passport.png"


@pytest.mark.asyncio
async def test_empty_streak_shows_alert_and_sends_nothing():
    cb, u, p, r = _env()
    cb.data = "card:streak"
    await ch.send_card.__wrapped__(cb, u, p, r)
    cb.message.answer_document.assert_not_awaited()
    assert cb.answer.await_args.kwargs.get("show_alert") is True


@pytest.mark.asyncio
async def test_unknown_kind_and_render_failure_are_handled(monkeypatch):
    cb, u, p, r = _env()
    cb.data = "card:evil"
    await ch.send_card.__wrapped__(cb, u, p, r)
    cb.message.answer_document.assert_not_awaited()

    cb, u, p, r = _env()
    cb.data = "card:passport"
    monkeypatch.setattr(ch, "render_card", AsyncMock(side_effect=RuntimeError("boom")))
    await ch.send_card.__wrapped__(cb, u, p, r)
    cb.message.answer.assert_awaited_once()  # friendly error, no crash
    cb.message.answer_document.assert_not_awaited()


@pytest.mark.asyncio
async def test_real_streak_rows_make_a_card():
    cb, u, p, r = _env(
        rows=[SimpleNamespace(kind="task", local_date=date.today(), duration_min=None)]
    )
    cb.data = "card:streak"
    await ch.send_card.__wrapped__(cb, u, p, r)
    cb.message.answer_document.assert_awaited_once()
