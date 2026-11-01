"""P1.5: 'we walked for half an hour' (text or voice) logs a walk; never invents minutes."""

from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.tz_utils import local_now
from app.logic.schemas import TrainingIntentSchema


def schema(**kw):
    base = {"action": "log_walk", "walk_minutes": 30, "message": "Класс!"}
    base.update(kw)
    return TrainingIntentSchema.model_validate(base)


def test_valid_walk_is_kept():
    s = schema()
    assert s.action == "log_walk" and s.walk_minutes == 30


@pytest.mark.parametrize("raw,expected", [("40", 40), (45.0, 45), ("  25 ", 25)])
def test_minutes_are_coerced(raw, expected):
    assert schema(walk_minutes=raw).walk_minutes == expected


@pytest.mark.parametrize("bad", [None, 0, 3, 241, 9999, -5, "много", "", True])
def test_missing_or_absurd_minutes_downgrade_to_none_action(bad):
    s = schema(walk_minutes=bad)
    assert s.action == "none" and s.walk_minutes is None


def test_other_actions_unchanged():
    assert schema(action="mark_done", walk_minutes=None).action == "mark_done"
    assert schema(action="whatever").action == "none"


def _env(intent, premium=True):
    from datetime import datetime, timedelta

    usr = SimpleNamespace(
        id=1,
        language_code="ru",
        timezone="UTC",
        is_premium=premium,
        subscription_expires_at=datetime.utcnow() + timedelta(days=3) if premium else None,
        media_trial_used_at=None,
    )
    pet = SimpleNamespace(id=7, name="Рекс")
    sent = MagicMock(edit_text=AsyncMock())
    msg = MagicMock(text="погуляли полчаса", photo=None, voice=None, caption=None)
    msg.from_user.id = 5
    msg.answer = AsyncMock(return_value=sent)
    rows_today = [SimpleNamespace(kind="walk", local_date=local_now("UTC").date(), duration_min=30)]
    act = MagicMock(log_walk=AsyncMock(), rows=AsyncMock(return_value=rows_today))
    return (
        dict(
            msg=msg,
            u_svc=MagicMock(
                get_or_create_telegram_user=AsyncMock(return_value=usr), repo=MagicMock()
            ),
            p_svc=MagicMock(get_pet=AsyncMock(return_value=pet)),
            a_svc=MagicMock(detect_training_intent=AsyncMock(return_value=intent)),
            t_svc=MagicMock(plan_repo=MagicMock(get_active_plan=AsyncMock(return_value=None))),
            conv_repo=MagicMock(create=AsyncMock()),
            rate_limiter=MagicMock(),
            metrics=MagicMock(inc=AsyncMock()),
            act_repo=act,
        ),
        act,
        sent,
    )


@pytest.mark.asyncio
async def test_handler_logs_the_walk_and_confirms():
    from app.bot.handlers.menu import handle_voice_action

    kw, act, sent = _env({"action": "log_walk", "walk_minutes": 30, "message": "Класс!"})
    await handle_voice_action.__wrapped__(**kw)
    pet_id, day, minutes = act.log_walk.await_args.args
    assert (pet_id, minutes) == (7, 30) and isinstance(day, date)
    text = sent.edit_text.await_args.args[0]
    assert "30" in text and "Класс" in text


@pytest.mark.asyncio
@pytest.mark.parametrize("minutes", [None, 0, 1000, "abc"])
async def test_handler_never_logs_bogus_minutes(minutes):
    from app.bot.handlers.menu import handle_voice_action

    kw, act, sent = _env({"action": "log_walk", "walk_minutes": minutes, "message": "ок"})
    await handle_voice_action.__wrapped__(**kw)
    act.log_walk.assert_not_awaited()


def test_confirmation_text_exists_in_all_locales():
    from app.i18n import t

    for lg in ("ru", "en", "de", "es", "fr", "pt"):
        txt = t("voice_action.walk", lg, m=30, n=5)
        assert "30" in txt and "voice_action." not in txt, lg


@pytest.mark.asyncio
async def test_heartbeat_first_beat_is_due_immediately_not_after_30s():
    from datetime import UTC, datetime, timedelta

    from app.scheduler.setup import create_scheduler

    sched = create_scheduler(MagicMock(), MagicMock())
    sched.start(paused=True)  # compute schedules without running any job
    try:
        first = sched.get_job("heartbeat").next_run_time
        assert first <= datetime.now(UTC) + timedelta(seconds=2)
    finally:
        sched.shutdown(wait=False)
