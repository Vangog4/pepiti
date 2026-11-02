"""AI failures must raise (so handlers release quota), never return error text to the user."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.ai_service import AiService, AiUnavailableError


def _svc(side_effect=None, text="ok"):
    svc = AiService.__new__(AiService)
    svc._metrics = None
    svc._generate_text = AsyncMock(side_effect=side_effect, return_value=text)
    return svc


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "call",
    [
        lambda s: s.answer_coach_question(MagicMock(), "q", lang="ru"),
        lambda s: s.explain_exercise("sit", "desc", lang="ru"),
        lambda s: s.summarize_progress(MagicMock(), 3, lang="ru"),
        lambda s: s.premium_deep_analysis(MagicMock(), 3, lang="ru"),
    ],
)
async def test_failure_raises_and_leaks_nothing(call):
    svc = _svc(side_effect=RuntimeError("secret-api-key-details"))
    with pytest.raises(AiUnavailableError):
        await call(svc)


def test_coach_text_handler_ignores_media():
    """Photo/voice/video in the coach state must not match the text handler."""
    from types import SimpleNamespace

    from app.bot.handlers import menu

    h = next(
        h for h in menu.router.message.handlers if h.callback.__name__ == "process_coach_question"
    )
    magic = [f.callback for f in h.filters if getattr(f.callback, "__name__", "") == "resolve"]
    assert magic, "text handler has no content filter"

    def matches(**attrs):
        base = dict(text=None, photo=None, voice=None, video=None, video_note=None)
        base.update(attrs)
        return all(m(SimpleNamespace(**base)) for m in magic)

    assert matches(text="Привет")
    assert not matches(photo=[object()])
    assert not matches(voice=object())
    assert not matches(video=object())
