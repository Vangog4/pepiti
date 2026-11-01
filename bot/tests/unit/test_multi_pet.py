"""P1.3: several dogs (Free 1, Premium 3) with an active-dog switcher."""

from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.pets import allowed_pets, can_add, pet_limit, resolve_active


def pets(*ids):
    return [
        SimpleNamespace(
            id=i,
            name=f"Пёс{i}",
            breed=None,
            sex=None,
            age_category=None,
            size_category=None,
            weight_kg=None,
            training_level=None,
            goal=None,
            behavior_issues=None,
            training_schedule=None,
            training_days=0,
            allergies=None,
            chronic_conditions=None,
        )
        for i in ids
    ]


def test_limits_from_rules():
    assert pet_limit(False) == 1 and pet_limit(True) == 3


@pytest.mark.parametrize(
    "count,premium,verdict",
    [
        (0, False, "ok"),
        (1, False, "need_premium"),
        (1, True, "ok"),
        (2, True, "ok"),
        (3, True, "max"),
        (5, True, "max"),
    ],
)
def test_can_add(count, premium, verdict):
    assert can_add(count, premium) == verdict


def test_allowed_pets_are_the_oldest_ones():
    p = pets(5, 2, 9)
    assert [x.id for x in allowed_pets(p, False)] == [2]
    assert [x.id for x in allowed_pets(p, True)] == [2, 5, 9]


def test_resolve_active_prefers_choice_but_only_among_allowed():
    p = pets(1, 2, 3)
    assert resolve_active(p, 3, True).id == 3
    assert resolve_active(p, 3, False).id == 1  # lapsed Premium: extra dogs are read-only
    assert resolve_active(p, None, True).id == 1
    assert resolve_active(p, 999, True).id == 1  # stale id (dog deleted)
    assert resolve_active([], 1, True) is None


def _session(user, pet_list):
    s = MagicMock()
    s.get = AsyncMock(return_value=user)
    res = MagicMock()
    res.scalars.return_value.all.return_value = pet_list
    s.execute = AsyncMock(return_value=res)
    return s


@pytest.mark.asyncio
async def test_repo_returns_the_active_dog_not_a_crash_with_two_dogs():
    from app.infrastructure.db.repositories.pet_repo import PetRepository

    exp = datetime.utcnow() + timedelta(days=5)
    user = SimpleNamespace(id=1, active_pet_id=2, is_premium=True, subscription_expires_at=exp)
    repo = PetRepository(_session(user, pets(1, 2)))
    assert (await repo.get_by_user_id(1)).id == 2

    free = SimpleNamespace(id=1, active_pet_id=2, is_premium=False, subscription_expires_at=None)
    assert (await PetRepository(_session(free, pets(1, 2))).get_by_user_id(1)).id == 1


@pytest.mark.asyncio
async def test_repo_with_no_dogs_and_with_one_dog():
    from app.infrastructure.db.repositories.pet_repo import PetRepository

    user = SimpleNamespace(id=1, active_pet_id=None, is_premium=False, subscription_expires_at=None)
    assert await PetRepository(_session(user, [])).get_by_user_id(1) is None
    assert (await PetRepository(_session(user, pets(7))).get_by_user_id(1)).id == 7


def _usr(premium=True, active=None):
    return SimpleNamespace(
        id=1,
        language_code="ru",
        timezone="UTC",
        active_pet_id=active,
        is_premium=premium,
        subscription_expires_at=datetime.utcnow() + timedelta(days=3) if premium else None,
    )


def _cb(data):
    cb = MagicMock(data=data)
    cb.answer = AsyncMock()
    cb.from_user.id = 5
    cb.message.edit_text = AsyncMock()
    return cb


def _svcs(usr, pet_list, active=None):
    u_svc = MagicMock(get_or_create_telegram_user=AsyncMock(return_value=usr))
    u_svc.repo.session.commit = AsyncMock()
    p_svc = MagicMock(
        list_pets=AsyncMock(return_value=pet_list),
        get_pet=AsyncMock(return_value=active or pet_list[0]),
    )
    return u_svc, p_svc


@pytest.mark.asyncio
async def test_switch_to_own_allowed_dog_updates_active():
    from app.bot.handlers import pets as ph

    usr = _usr(premium=True)
    u_svc, p_svc = _svcs(usr, pets(1, 2))
    await ph.switch_pet.__wrapped__(_cb("pet_sw:2"), u_svc, p_svc)
    assert usr.active_pet_id == 2


@pytest.mark.asyncio
@pytest.mark.parametrize("data", ["pet_sw:99", "pet_sw:abc", "pet_sw:"])
async def test_switch_to_foreign_or_garbage_id_is_ignored(data):
    from app.bot.handlers import pets as ph

    usr = _usr(premium=True, active=1)
    u_svc, p_svc = _svcs(usr, pets(1, 2))
    await ph.switch_pet.__wrapped__(_cb(data), u_svc, p_svc)
    assert usr.active_pet_id == 1


@pytest.mark.asyncio
async def test_lapsed_premium_cannot_switch_to_a_locked_dog():
    from app.bot.handlers import pets as ph

    usr = _usr(premium=False, active=1)
    u_svc, p_svc = _svcs(usr, pets(1, 2))
    await ph.switch_pet.__wrapped__(_cb("pet_sw:2"), u_svc, p_svc)
    assert usr.active_pet_id == 1


@pytest.mark.asyncio
async def test_add_dog_free_user_with_one_dog_gets_the_paywall_not_the_form():
    from app.bot.handlers import pets as ph

    usr = _usr(premium=False)
    u_svc, p_svc = _svcs(usr, pets(1))
    state = MagicMock(set_state=AsyncMock(), update_data=AsyncMock())
    cb = _cb("pet_add")
    await ph.add_pet.__wrapped__(cb, state, u_svc, p_svc)
    state.set_state.assert_not_awaited()
    kb = cb.message.edit_text.await_args.kwargs["reply_markup"]
    assert "buy:premium_1m" in str(kb)


@pytest.mark.asyncio
async def test_add_dog_premium_starts_the_name_step_in_adding_mode():
    from app.bot.handlers import pets as ph
    from app.bot.states.onboarding import OnboardingStates

    usr = _usr(premium=True)
    u_svc, p_svc = _svcs(usr, pets(1))
    state = MagicMock(set_state=AsyncMock(), update_data=AsyncMock())
    await ph.add_pet.__wrapped__(_cb("pet_add"), state, u_svc, p_svc)
    state.set_state.assert_awaited_with(OnboardingStates.collecting)
    state.update_data.assert_awaited_with(adding_pet=True)


@pytest.mark.asyncio
async def test_add_dog_at_the_maximum_is_refused():
    from app.bot.handlers import pets as ph

    usr = _usr(premium=True)
    u_svc, p_svc = _svcs(usr, pets(1, 2, 3))
    state = MagicMock(set_state=AsyncMock(), update_data=AsyncMock())
    cb = _cb("pet_add")
    await ph.add_pet.__wrapped__(cb, state, u_svc, p_svc)
    state.set_state.assert_not_awaited()
    assert cb.answer.await_args.kwargs.get("show_alert") is True


def test_profile_switcher_labels_fit_and_lock_extra_dogs():
    from app.bot.handlers.menu import build_profile_view

    p = [
        SimpleNamespace(
            id=i,
            name="Александр Македонский",
            breed=None,
            sex=None,
            age_category=None,
            size_category=None,
            weight_kg=None,
            training_level=None,
            goal=None,
            behavior_issues=None,
            training_schedule=None,
            training_days=0,
            allergies=None,
            chronic_conditions=None,
        )
        for i in (1, 2)
    ]
    for lg in ("ru", "en", "de", "es", "fr", "pt"):
        text, kb = build_profile_view(
            p[0], p, SimpleNamespace(is_premium=False, subscription_expires_at=None), lg
        )
        btns = [b for row in kb.inline_keyboard for b in row]
        sw = [b for b in btns if (b.callback_data or "").startswith("pet_")]
        assert sw and all(len(b.text) <= 14 for b in sw), (lg, [b.text for b in sw])
        assert any(b.callback_data == "pet_locked" for b in sw)  # dog #2 is locked on Free


@pytest.mark.asyncio
async def test_additional_dog_skips_the_new_user_ceremony(monkeypatch):
    from app.bot.handlers import onboarding as ob

    usr = SimpleNamespace(
        id=1,
        telegram_id=5,
        first_name="А",
        username=None,
        referrer_telegram_id=None,
        onboarding_completed_at="done",
        active_pet_id=None,
        language_code="ru",
    )
    user_svc = MagicMock(get_or_create_telegram_user=AsyncMock(return_value=usr))
    user_svc.repo.session.commit = AsyncMock()

    async def create(pet):
        pet.id = 42
        return pet

    pet_svc = MagicMock(repo=MagicMock(create=AsyncMock(side_effect=create)))
    ref_svc = MagicMock(award_if_eligible=AsyncMock())
    t_svc = MagicMock(get_or_create_today=AsyncMock(side_effect=RuntimeError("no ai in test")))
    loading = MagicMock(edit_text=AsyncMock())
    msg = MagicMock()
    msg.answer = AsyncMock(return_value=loading)
    msg.bot.send_message = AsyncMock()
    state = MagicMock(clear=AsyncMock())

    await ob._finish_onboarding(
        msg,
        5,
        state,
        {"name": "Луна", "breed": "Корги"},
        {"adding_pet": True},
        user_svc,
        pet_svc,
        ref_svc,
        t_svc,
        "ru",
    )
    assert usr.active_pet_id == 42
    ref_svc.award_if_eligible.assert_not_awaited()
    msg.bot.send_message.assert_not_awaited()  # no "new user" ping to admins
    assert usr.onboarding_completed_at == "done"
