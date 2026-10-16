"""Unit tests for CoachService — thread context, exchange saving, background task flags."""

import time
from unittest.mock import MagicMock

import pytest

from app.services.coach_service import CoachService


def _make_thread(message_count=0, messages=None, title=None, summary=None, status="active"):
    t = MagicMock()
    t.message_count = message_count
    t.messages_json = messages if messages is not None else []
    t.title = title
    t.summary = summary
    t.status = status
    return t


@pytest.fixture
def svc():
    repo = MagicMock()
    return CoachService(repo=repo)


class TestBuildPromptContext:
    def test_empty_thread_returns_empty_string(self, svc):
        thread = _make_thread()
        assert svc.build_prompt_context(thread, is_premium=False) == ""

    def test_formats_user_and_coach_roles(self, svc):
        msgs = [
            {"role": "user", "content": "Как сидеть?", "ts": 0},
            {"role": "coach", "content": "Держи лакомство вверх.", "ts": 0},
        ]
        thread = _make_thread(messages=msgs, message_count=1)
        ctx = svc.build_prompt_context(thread, is_premium=False)
        assert "Хозяин: Как сидеть?" in ctx
        assert "Кинолог: Держи лакомство вверх." in ctx

    def test_free_truncates_to_context_limit(self, svc):
        # 12 messages → free limit is 10, so indices 0 and 1 are cut (messages[-10:] = indices 2..11)
        msgs = [
            {"role": "user" if i % 2 == 0 else "coach", "content": f"xmsg_{i:03d}_x", "ts": i}
            for i in range(12)
        ]
        thread = _make_thread(messages=msgs, message_count=6)
        ctx = svc.build_prompt_context(thread, is_premium=False)
        assert "xmsg_000_x" not in ctx  # trimmed (index 0)
        assert "xmsg_001_x" not in ctx  # trimmed (index 1)
        assert "xmsg_002_x" in ctx  # kept (index 2, within last 10)
        assert "xmsg_011_x" in ctx  # recent kept

    def test_premium_uses_wider_context(self, svc):
        msgs = [
            {"role": "user" if i % 2 == 0 else "coach", "content": f"msg{i}", "ts": i}
            for i in range(22)
        ]
        thread = _make_thread(messages=msgs, message_count=11)
        free_ctx = svc.build_prompt_context(thread, is_premium=False)
        prem_ctx = svc.build_prompt_context(thread, is_premium=True)
        assert len(prem_ctx) > len(free_ctx)

    def test_prepends_summary_when_messages_exceed_limit(self, svc):
        msgs = [
            {"role": "user" if i % 2 == 0 else "coach", "content": f"x{i}", "ts": i}
            for i in range(12)
        ]
        thread = _make_thread(
            messages=msgs, summary="Резюме: собака тянет поводок.", message_count=6
        )
        ctx = svc.build_prompt_context(thread, is_premium=False)
        assert "Резюме: собака тянет поводок." in ctx
        assert "---" in ctx

    def test_no_summary_when_messages_within_limit(self, svc):
        msgs = [{"role": "user", "content": "q", "ts": 0}]
        thread = _make_thread(messages=msgs, summary="Резюме", message_count=1)
        ctx = svc.build_prompt_context(thread, is_premium=False)
        assert "Резюме" not in ctx


class TestSaveExchange:
    def test_appends_user_and_coach_messages(self, svc):
        thread = _make_thread()
        svc.save_exchange(thread, "Вопрос", "Ответ")
        assert len(thread.messages_json) == 2
        assert thread.messages_json[0]["role"] == "user"
        assert thread.messages_json[0]["content"] == "Вопрос"
        assert thread.messages_json[1]["role"] == "coach"
        assert thread.messages_json[1]["content"] == "Ответ"

    def test_increments_message_count(self, svc):
        thread = _make_thread(message_count=3)
        svc.save_exchange(thread, "Q", "A")
        assert thread.message_count == 4

    def test_trims_to_max_stored(self, svc):
        msgs = [{"role": "user", "content": f"m{i}", "ts": i} for i in range(40)]
        thread = _make_thread(messages=msgs, message_count=20)
        svc.save_exchange(thread, "new_q", "new_a")
        assert len(thread.messages_json) == CoachService.MAX_STORED_MESSAGES
        assert thread.messages_json[-2]["content"] == "new_q"
        assert thread.messages_json[-1]["content"] == "new_a"

    def test_truncates_long_question(self, svc):
        thread = _make_thread()
        svc.save_exchange(thread, "x" * 2000, "answer")
        assert len(thread.messages_json[0]["content"]) <= 1000

    def test_has_timestamp(self, svc):
        thread = _make_thread()
        before = int(time.time()) - 1
        svc.save_exchange(thread, "q", "a")
        assert thread.messages_json[0]["ts"] >= before


class TestBackgroundFlags:
    def test_should_generate_title_after_first_exchange(self, svc):
        thread = _make_thread(message_count=1, title=None)
        assert svc.should_generate_title(thread) is True

    def test_no_title_generation_if_title_exists(self, svc):
        thread = _make_thread(message_count=1, title="Уже есть")
        assert svc.should_generate_title(thread) is False

    def test_no_title_generation_after_second_exchange(self, svc):
        thread = _make_thread(message_count=2, title=None)
        assert svc.should_generate_title(thread) is False

    def test_should_refresh_summary_at_10th_exchange(self, svc):
        thread = _make_thread(message_count=10)
        assert svc.should_refresh_summary(thread) is True

    def test_should_refresh_summary_at_20th(self, svc):
        thread = _make_thread(message_count=20)
        assert svc.should_refresh_summary(thread) is True

    def test_no_summary_refresh_at_5th(self, svc):
        thread = _make_thread(message_count=5)
        assert svc.should_refresh_summary(thread) is False

    def test_no_summary_refresh_at_zero(self, svc):
        thread = _make_thread(message_count=0)
        assert svc.should_refresh_summary(thread) is False


class TestResetKeepsThreads:
    """Verify reset handler expectation: active_coach_thread_id reset, threads not deleted."""

    def test_reset_py_does_not_import_coach_thread_delete(self):
        import inspect
        import app.bot.handlers.reset as reset_mod

        src = inspect.getsource(reset_mod)
        assert "coach_threads" not in src or "active_coach_thread_id" in src, (
            "reset.py must not delete coach_threads"
        )
        assert "active_coach_thread_id = None" in src, (
            "reset.py must set active_coach_thread_id = None"
        )
