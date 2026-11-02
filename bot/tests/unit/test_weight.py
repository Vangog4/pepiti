"""P2: weight log, trend vs the dog's OWN history (no invented breed norms), monthly nudge."""

from datetime import UTC, date, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.weight import weight_trend

T = date(2026, 11, 1)


def e(days_ago, kg):
    return SimpleNamespace(weight_kg=kg, local_date=T - timedelta(days=days_ago))


def test_no_or_single_entry_has_no_trend():
    assert weight_trend([], T)["last"] is None
    one = weight_trend([e(0, 10.0)], T)
    assert one["last"] == 10.0 and one["delta_kg"] is None and one["alert"] is None


def test_trend_against_the_entry_about_30_days_ago():
    tr = weight_trend([e(60, 9.0), e(31, 10.0), e(10, 10.5), e(0, 11.0)], T)
    assert tr["last"] == 11.0 and tr["prev"] == 10.0  # closest to 30 days back (31), not 60 or 10
    assert tr["delta_kg"] == 1.0 and tr["delta_pct"] == 10.0
    assert tr["alert"] == "gain"


@pytest.mark.parametrize(
    "old,new,alert",
    [(10.0, 10.5, None), (10.0, 11.0, "gain"), (10.0, 9.0, "loss"), (10.0, 9.1, None)],
)
def test_alert_threshold_is_ten_percent_either_way(old, new, alert):
    assert weight_trend([e(30, old), e(0, new)], T)["alert"] == alert


def test_too_recent_history_is_not_compared():
    """A weigh-in 2 days ago says nothing about a monthly trend (needs >= 7 days apart)."""
    tr = weight_trend([e(2, 10.0), e(0, 14.0)], T)
    assert tr["delta_kg"] is None and tr["alert"] is None


def test_order_of_input_does_not_matter_and_bad_rows_are_ignored():
    rows = [
        e(0, 11.0),
        e(30, 10.0),
        SimpleNamespace(weight_kg=None, local_date=T),
        SimpleNamespace(weight_kg=-3, local_date=T),
    ]
    tr = weight_trend(rows, T)
    assert tr["last"] == 11.0 and tr["prev"] == 10.0


def _cb(data="wt_open"):
    cb = MagicMock(data=data)
    cb.answer = AsyncMock()
    cb.from_user.id = 5
    cb.message.edit_text = AsyncMock()
    return cb


def _usr():
    return SimpleNamespace(
        id=1, language_code="ru", timezone="UTC", is_premium=False, subscription_expires_at=None
    )


@pytest.mark.asyncio
async def test_open_screen_shows_trend_and_asks_for_weight():
    from app.bot.handlers import weight as wh

    pet = SimpleNamespace(id=7, name="Рекс", weight_kg=11.0)
    u_svc = MagicMock(get_or_create_telegram_user=AsyncMock(return_value=_usr()))
    p_svc = MagicMock(get_pet=AsyncMock(return_value=pet))
    repo = MagicMock(recent=AsyncMock(return_value=[e(30, 10.0), e(0, 11.0)]))
    state = MagicMock(set_state=AsyncMock())
    cb = _cb()
    await wh.open_weight.__wrapped__(cb, state, u_svc, p_svc, repo)
    text = cb.message.edit_text.await_args.args[0]
    assert "11" in text and "10" in text
    state.set_state.assert_awaited_with(wh.WeightState.waiting)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "raw,ok", [("12,5", True), ("12.5 кг", True), ("abc", False), ("0", False), ("500", False)]
)
async def test_receiving_weight_validates_and_stores(raw, ok):
    from app.bot.handlers import weight as wh

    pet = SimpleNamespace(id=7, name="Рекс", weight_kg=11.0)
    u_svc = MagicMock(get_or_create_telegram_user=AsyncMock(return_value=_usr()))
    u_svc.repo.session.commit = AsyncMock()
    p_svc = MagicMock(
        get_pet=AsyncMock(return_value=pet), repo=MagicMock(session=MagicMock(commit=AsyncMock()))
    )
    repo = MagicMock(add=AsyncMock(), recent=AsyncMock(return_value=[]))
    state = MagicMock(clear=AsyncMock())
    msg = MagicMock(text=raw)
    msg.from_user.id = 5
    msg.answer = AsyncMock()
    await wh.receive_weight.__wrapped__(msg, state, u_svc, p_svc, repo)
    assert repo.add.await_count == (1 if ok else 0)
    if ok:
        assert pet.weight_kg == 12.5  # passport stays in sync
        state.clear.assert_awaited()


@pytest.mark.asyncio
async def test_monthly_nudge_only_when_overdue_and_once(monkeypatch):
    from app.infrastructure.redis.once import OnceGuard
    from app.services import nudges as n
    from tests.unit.test_nudges import FakeRedis

    now = datetime(2026, 11, 10, 7, 0, tzinfo=UTC)
    user = SimpleNamespace(
        id=1,
        telegram_id=99,
        language_code="ru",
        timezone="UTC",
        reminder_time="10:00",
        is_premium=False,
        subscription_expires_at=None,
    )
    pet = SimpleNamespace(id=7, name="Рекс")
    monkeypatch.setattr(n, "due_users", AsyncMock(return_value=[user]))
    monkeypatch.setattr(n, "_first_pet", AsyncMock(return_value=pet))

    def ctx(last):
        r = MagicMock()
        r.scalar.return_value = last
        s = MagicMock(execute=AsyncMock(return_value=r))
        return MagicMock(
            return_value=MagicMock(
                __aenter__=AsyncMock(return_value=s), __aexit__=AsyncMock(return_value=False)
            )
        )

    bot, guard = MagicMock(send_message=AsyncMock()), OnceGuard(FakeRedis())
    assert (
        await n.send_weigh_in_nudges(ctx(date(2026, 11, 5)), bot, guard, now_utc=now) == 0
    )  # weighed 5 days ago
    assert (
        await n.send_weigh_in_nudges(ctx(date(2026, 9, 1)), bot, guard, now_utc=now) == 1
    )  # 70 days ago
    assert "wt_open" in str(bot.send_message.await_args.kwargs["reply_markup"])
    assert await n.send_weigh_in_nudges(ctx(date(2026, 9, 1)), bot, guard, now_utc=now) == 0  # once


def test_texts_and_buttons_exist_and_fit():
    from app.bot.handlers.health import health_kb
    from app.i18n import t

    for lg in ("ru", "en", "de", "es", "fr", "pt"):
        wt = [b for r in health_kb(lg).inline_keyboard for b in r if b.callback_data == "wt_open"]
        assert len(wt) == 1 and len(wt[0].text) <= 14, lg
        assert "weight." not in t("weight.nudge", lg, pet="Рекс")
        assert "weight." not in t("weight.alert.gain", lg)


def test_scheduler_registers_weigh_in_job():
    from app.scheduler.setup import create_scheduler

    assert create_scheduler(MagicMock(), MagicMock()).get_job("weigh_in_nudge")


@pytest.mark.asyncio
async def test_weight_edited_in_the_profile_also_feeds_the_trend():
    from app.bot.handlers import edit_profile as ep

    pet = SimpleNamespace(id=7, name="Рекс", weight_kg=None)
    usr = SimpleNamespace(id=1, language_code="ru", timezone="UTC")
    u_svc = MagicMock(get_or_create_telegram_user=AsyncMock(return_value=usr))
    p_svc = MagicMock(
        get_pet=AsyncMock(return_value=pet), repo=MagicMock(session=MagicMock(commit=AsyncMock()))
    )
    w_repo = MagicMock(add=AsyncMock())
    state = MagicMock(
        get_data=AsyncMock(return_value={"field_name": "weight_kg"}), clear=AsyncMock()
    )
    msg = MagicMock(text="13,2")
    msg.from_user.id = 5
    msg.answer = AsyncMock()
    msg.delete = AsyncMock()
    await ep.save_profile_field_text.__wrapped__(msg, state, u_svc, p_svc, w_repo)
    assert pet.weight_kg == 13.2
    w_repo.add.assert_awaited_once()
    assert w_repo.add.await_args.args[:2] == (7, 13.2)
