"""P2: one-file dog passport for the vet (profile + allergies + health log + remembered facts)."""

from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.passport_pdf import generate_passport_pdf, passport_pdf_data

TODAY = date(2026, 11, 1)


def ev(id, kind, done, due):
    return SimpleNamespace(id=id, kind=kind, done_at=done, next_due_at=due)


PET = SimpleNamespace(
    id=7,
    name="Рекс",
    breed="Лабрадор",
    sex="кобель",
    age_category="Молодой (1–3 года)",
    birth_date=date(2024, 1, 10),
    weight_kg=28.5,
    size_category="Крупный (25–45 кг)",
    allergies=["курица"],
    chronic_conditions=["дисплазия"],
    health_notes="хромает после бега",
)


def test_data_collects_everything_a_vet_asks_for():
    events = [
        ev(1, "ticks", date(2026, 8, 1), date(2026, 8, 31)),
        ev(2, "ticks", date(2026, 10, 2), date(2026, 11, 1)),
        ev(3, "vaccine", date(2026, 1, 5), date(2027, 1, 5)),
    ]
    d = passport_pdf_data(PET, events, ["боится грома", "ест сухой корм"], TODAY)
    assert d["name"] == "Рекс" and d["weight"] == "28.5" and d["age"] == "2 г"
    assert d["allergies"] == ["курица"] and d["chronic"] == ["дисплазия"]
    assert [r["kind"] for r in d["schedule"]] == [
        "vaccine",
        "ticks",
    ]  # latest per kind, stable order
    assert len(d["history"]) == 3 and d["history"][0]["done"] == date(2026, 10, 2)  # newest first
    assert d["facts"] == ["боится грома", "ест сухой корм"]


def test_history_and_facts_are_capped():
    events = [ev(i, "ticks", date(2026, 1, 1), date(2026, 2, 1)) for i in range(60)]
    d = passport_pdf_data(PET, events, [f"факт {i}" for i in range(100)], TODAY)
    assert len(d["history"]) <= 30 and len(d["facts"]) <= 20


def test_missing_data_does_not_crash():
    bare = SimpleNamespace(
        id=1,
        name="Бобик",
        breed=None,
        sex=None,
        age_category=None,
        birth_date=None,
        weight_kg=None,
        size_category=None,
        allergies=None,
        chronic_conditions=None,
        health_notes=None,
    )
    d = passport_pdf_data(bare, [], [], TODAY)
    assert d["weight"] == "" and d["allergies"] == [] and d["schedule"] == []


@pytest.mark.parametrize("lang", ["ru", "en", "de", "es", "fr", "pt"])
def test_pdf_renders_in_every_language(lang):
    d = passport_pdf_data(
        PET, [ev(1, "ticks", date(2026, 10, 2), date(2026, 11, 1))], ["боится грома"], TODAY
    )
    pdf = generate_passport_pdf(d, lang)
    assert pdf[:5] == b"%PDF-" and len(pdf) > 2000


def test_hostile_and_huge_input_still_makes_a_pdf():
    pet = SimpleNamespace(
        **{
            **PET.__dict__,
            "name": "🐶" * 80 + "<b>&",
            "health_notes": "x" * 5000,
            "allergies": ["a" * 300] * 10,
        }
    )
    events = [
        ev(i, k, date(2026, 1, 1), date(2026, 2, 1))
        for i, k in enumerate(["ticks", "worms", "vaccine"] * 20)
    ]
    d = passport_pdf_data(pet, events, ["y" * 400] * 30, TODAY)
    pdf = generate_passport_pdf(d, "ru")
    assert pdf[:5] == b"%PDF-"


@pytest.mark.asyncio
async def test_handler_sends_pdf_document_for_own_dog():
    from app.bot.handlers import cards as ch

    usr = SimpleNamespace(id=1, language_code="ru", timezone="UTC")
    u_svc = MagicMock(get_or_create_telegram_user=AsyncMock(return_value=usr))
    p_svc = MagicMock(get_pet=AsyncMock(return_value=PET))
    health = MagicMock(
        for_pet=AsyncMock(return_value=[ev(1, "ticks", date(2026, 10, 2), date(2026, 11, 1))])
    )
    facts = MagicMock(list_active=AsyncMock(return_value=[SimpleNamespace(fact="боится грома")]))
    cb = MagicMock(data="pf_pdf")
    cb.answer = AsyncMock()
    cb.from_user.id = 5
    cb.message.answer_document = AsyncMock()
    cb.message.answer = AsyncMock()
    await ch.send_passport_pdf.__wrapped__(cb, u_svc, p_svc, health, facts)
    doc = cb.message.answer_document.await_args.args[0]
    assert doc.data[:5] == b"%PDF-" and doc.filename.endswith(".pdf")
    health.for_pet.assert_awaited_once_with(7)  # scoped to the user's own dog


@pytest.mark.asyncio
async def test_handler_without_a_dog_sends_nothing():
    from app.bot.handlers import cards as ch

    u_svc = MagicMock(
        get_or_create_telegram_user=AsyncMock(
            return_value=SimpleNamespace(id=1, language_code="ru", timezone="UTC")
        )
    )
    p_svc = MagicMock(get_pet=AsyncMock(return_value=None))
    cb = MagicMock(data="pf_pdf")
    cb.answer = AsyncMock()
    cb.from_user.id = 5
    cb.message.answer_document = AsyncMock()
    await ch.send_passport_pdf.__wrapped__(cb, u_svc, p_svc, MagicMock(), MagicMock())
    cb.message.answer_document.assert_not_awaited()


def test_profile_button_fits_in_every_language():
    from app.i18n import t

    for lg in ("ru", "en", "de", "es", "fr", "pt"):
        txt = t("profile.pdf.btn", lg)
        assert 0 < len(txt) <= 14 and "profile." not in txt, (lg, txt)
