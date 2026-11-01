from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.bot.handlers import memory as mh
from app.bot.handlers import menu


def _usr():
    return MagicMock(
        get_or_create_telegram_user=AsyncMock(
            return_value=SimpleNamespace(language_code="ru", id=1)
        )
    )


def _pets(pet_id=7):
    return MagicMock(get_pet=AsyncMock(return_value=SimpleNamespace(id=pet_id, name="Рекс")))


def _cb(data):
    cb = MagicMock(data=data)
    cb.answer = AsyncMock()
    cb.from_user.id = 5
    cb.message.edit_text = AsyncMock()
    return cb


@pytest.mark.asyncio
async def test_delete_is_scoped_to_the_users_own_pet():
    repo = MagicMock(
        soft_delete=AsyncMock(return_value=False), list_active=AsyncMock(return_value=[])
    )
    await mh.delete_fact.__wrapped__(_cb("mem_del:99"), _usr(), _pets(7), repo)
    repo.soft_delete.assert_awaited_once_with(99, 7)  # pet id comes from the DB, never the callback


@pytest.mark.asyncio
async def test_delete_garbage_callback_is_ignored():
    repo = MagicMock(soft_delete=AsyncMock(), list_active=AsyncMock(return_value=[]))
    await mh.delete_fact.__wrapped__(_cb("mem_del:abc"), _usr(), _pets(), repo)
    repo.soft_delete.assert_not_awaited()


@pytest.mark.asyncio
async def test_user_fact_saved_once_and_deduped():
    st = MagicMock(clear=AsyncMock())
    repo = MagicMock(
        list_active=AsyncMock(return_value=[SimpleNamespace(id=1, fact="Боится грома")]),
        add_many=AsyncMock(),
    )
    msg = MagicMock(text="боится  ГРОМА")
    msg.from_user.id = 5
    msg.answer = AsyncMock()
    await mh.save_fact.__wrapped__(msg, st, _usr(), _pets(), repo)
    repo.add_many.assert_not_awaited()
    msg.text = "ест сухой корм"
    await mh.save_fact.__wrapped__(msg, st, _usr(), _pets(), repo)
    repo.add_many.assert_awaited_once_with(7, ["ест сухой корм"], source="user")


def test_keyboard_has_delete_per_fact_and_fits():
    facts = [SimpleNamespace(id=i, fact=f"факт {i}") for i in range(1, 8)]
    kb = mh.memory_kb(facts, "ru")
    dels = [
        b.callback_data
        for r in kb.inline_keyboard
        for b in r
        if b.callback_data.startswith("mem_del:")
    ]
    assert dels == [f"mem_del:{i}" for i in range(1, 8)]
    assert all(
        len(b.text) <= 14
        for r in kb.inline_keyboard
        for b in r
        if b.callback_data != "menu_main"  # shared back button is shortened in P1.9
    )


@pytest.mark.asyncio
async def test_bg_extract_saves_only_new_and_never_raises():
    session = MagicMock()
    ctx = MagicMock(
        __aenter__=AsyncMock(return_value=session), __aexit__=AsyncMock(return_value=False)
    )
    fac = MagicMock(return_value=ctx)
    repo = MagicMock(
        list_active=AsyncMock(return_value=[SimpleNamespace(fact="боится грома")]),
        add_many=AsyncMock(),
    )
    a_svc = MagicMock(extract_facts=AsyncMock(return_value=["Боится грома", "аллергия на курицу"]))
    menu.PetFactRepository = lambda s: repo  # type: ignore[assignment]
    await menu._bg_extract_facts(7, "q", "a", fac, a_svc)
    repo.add_many.assert_awaited_once_with(7, ["аллергия на курицу"], source="ai")

    a_svc.extract_facts = AsyncMock(side_effect=RuntimeError("boom"))
    await menu._bg_extract_facts(7, "q", "a", fac, a_svc)  # must swallow


def test_single_alembic_head():
    import pathlib
    import re

    revs, downs = set(), set()
    for f in pathlib.Path("alembic/versions").glob("*.py"):
        src = f.read_text()
        r = re.search(r"^revision(?:: str)? = ['\"](\w+)['\"]", src, re.M)
        d = re.search(r"^down_revision[^=]*= ['\"](\w+)['\"]", src, re.M)
        if r:
            revs.add(r.group(1))
        if d:
            downs.add(d.group(1))
    assert revs - downs == {"b8c9d0e1f2a3"}
