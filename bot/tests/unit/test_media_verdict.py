"""P1.8: strict MediaVerdict, one free media trial, and no positional Part.from_text (prod bug)."""

import pathlib
import re
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import ValidationError

from app.logic.schemas import MediaVerdict
from app.services.ai_service import AiService, AiUnavailableError
from app.services.media_verdict import render_verdict


def _v(**kw):
    base = dict(summary="Собака тянет поводок на прогулке", urgency="low", steps=["Стой на месте"])
    base.update(kw)
    return MediaVerdict(**base)


def test_schema_is_strict():
    assert _v().urgency == "low"
    with pytest.raises(ValidationError):
        _v(urgency="maybe")
    with pytest.raises(ValidationError):
        _v(steps=[f"шаг номер {i}" for i in range(6)])
    with pytest.raises(ValidationError):
        _v(summary="")
    with pytest.raises(ValidationError):
        MediaVerdict(summary="достаточно длинно", urgency="low", steps=[], extra_field=1)


def test_render_escapes_html_and_sections():
    out = render_verdict(_v(summary="Тянет <b>сильно</b> & рычит", steps=["раз", "два"]), "ru")
    assert "&lt;b&gt;" in out and "&amp;" in out
    assert "1. раз" in out and "2. два" in out


def test_vet_now_is_prominent_and_never_truncated():
    long_steps = ["x" * 190] * 5
    out = render_verdict(_v(urgency="vet_now", steps=long_steps, summary="s" * 600), "ru")
    assert out.startswith("🚨")
    assert out.count("x" * 190) == 5  # nothing cut


def test_vet_soon_marker_and_low_has_none():
    assert "⚠️" in render_verdict(_v(urgency="vet_soon"), "ru")
    low = render_verdict(_v(), "ru")
    assert "🚨" not in low and "⚠️" not in low


@pytest.mark.asyncio
async def test_analyze_returns_html_and_raises_when_ai_fails():
    svc = AiService.__new__(AiService)
    svc._metrics = None
    svc._generate_structured = AsyncMock(return_value=_v(urgency="vet_now"))
    pet = SimpleNamespace(name="Рекс", breed=None, age_category=None)
    out = await svc.analyze_media_question(pet, b"x", "image/jpeg", None, "", lang="ru")
    assert out.startswith("🚨")
    svc._generate_structured = AsyncMock(return_value=None)
    with pytest.raises(AiUnavailableError):
        await svc.analyze_media_question(pet, b"x", "image/jpeg", None, "", lang="ru")


def test_no_positional_part_from_text():
    """genai Part.from_text is keyword-only; positional calls crashed every media request."""
    src = pathlib.Path("app/services/ai_service.py").read_text()
    for m in re.finditer(r"Part\.from_text\(\s*([^)\s][^,)]*)", src):
        assert m.group(1).startswith("text="), m.group(0)


@pytest.mark.asyncio
async def test_trial_claim_and_release_in_repo():
    from app.infrastructure.db.repositories.user_repo import UserRepository

    session = MagicMock()
    session.commit = AsyncMock()
    session.execute = AsyncMock(return_value=SimpleNamespace(rowcount=1))
    repo = UserRepository(session)
    assert await repo.claim_media_trial(1) is True
    session.execute = AsyncMock(return_value=SimpleNamespace(rowcount=0))
    assert await repo.claim_media_trial(1) is False
    await repo.release_media_trial(1)
    session.commit.assert_awaited()


# ── handler gating ──────────────────────────────────────────────────────────


def _handler_env(trial_used: bool, premium: bool = False, analyze=None):
    from datetime import datetime, timedelta

    usr = SimpleNamespace(
        id=1,
        language_code="ru",
        timezone="UTC",
        is_premium=premium,
        subscription_expires_at=(datetime.utcnow() + timedelta(days=5)) if premium else None,
        media_trial_used_at=datetime.utcnow() if trial_used else None,
        active_coach_thread_id=None,
    )
    repo = MagicMock(
        claim_media_trial=AsyncMock(return_value=True), release_media_trial=AsyncMock()
    )
    u_svc = MagicMock(get_or_create_telegram_user=AsyncMock(return_value=usr), repo=repo)
    u_svc.repo.session.commit = AsyncMock()
    p_svc = MagicMock(
        get_pet=AsyncMock(
            return_value=SimpleNamespace(id=7, name="Рекс", breed=None, age_category=None)
        )
    )
    thread = SimpleNamespace(id=1, status="active", messages_json=[], summary=None, title=None)
    coach = MagicMock(
        repo=MagicMock(
            get_by_id=AsyncMock(return_value=thread), create=AsyncMock(return_value=thread)
        ),
        build_prompt_context=MagicMock(return_value=""),
        save_exchange=MagicMock(),
        should_generate_title=MagicMock(return_value=False),
        should_refresh_summary=MagicMock(return_value=False),
    )
    a_svc = MagicMock(analyze_media_question=analyze or AsyncMock(return_value="<b>ok</b>"))
    msg = MagicMock(caption=None)
    msg.from_user.id = 5
    msg.photo = [object()]
    msg.answer = AsyncMock(return_value=MagicMock(edit_text=AsyncMock()))
    msg.bot.download = AsyncMock()
    state = MagicMock(clear=AsyncMock())
    return (
        dict(
            msg=msg,
            state=state,
            u_svc=u_svc,
            p_svc=p_svc,
            a_svc=a_svc,
            conv_repo=MagicMock(create=AsyncMock()),
            rate_limiter=MagicMock(),
            coach_svc=coach,
            session_fac=MagicMock(),
        ),
        repo,
        usr,
    )


@pytest.mark.asyncio
async def test_photo_after_trial_is_paywalled_before_download():
    from app.bot.handlers.menu import process_coach_photo

    kw, repo, _ = _handler_env(trial_used=True)
    await process_coach_photo.__wrapped__(**kw)
    kw["msg"].bot.download.assert_not_awaited()
    kw["a_svc"].analyze_media_question.assert_not_awaited()
    repo.claim_media_trial.assert_not_awaited()


@pytest.mark.asyncio
async def test_first_photo_uses_trial_and_keeps_it_on_success():
    from app.bot.handlers.menu import process_coach_photo

    kw, repo, _ = _handler_env(trial_used=False)
    await process_coach_photo.__wrapped__(**kw)
    repo.claim_media_trial.assert_awaited_once_with(1)
    repo.release_media_trial.assert_not_awaited()
    kw["a_svc"].analyze_media_question.assert_awaited_once()


@pytest.mark.asyncio
async def test_failed_analysis_gives_the_trial_back():
    from app.bot.handlers.menu import process_coach_photo

    kw, repo, _ = _handler_env(
        trial_used=False, analyze=AsyncMock(side_effect=AiUnavailableError("x"))
    )
    await process_coach_photo.__wrapped__(**kw)
    repo.release_media_trial.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_premium_photo_never_touches_the_trial():
    from app.bot.handlers.menu import process_coach_photo

    kw, repo, _ = _handler_env(trial_used=True, premium=True)
    await process_coach_photo.__wrapped__(**kw)
    repo.claim_media_trial.assert_not_awaited()
    kw["a_svc"].analyze_media_question.assert_awaited_once()
