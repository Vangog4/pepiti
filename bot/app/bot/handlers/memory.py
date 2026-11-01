"""🧠 Memory screen: what the AI remembers about the dog; owner can add and delete."""

import logging

from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dependency_injector.wiring import Provide, inject

from app.bot.keyboards.main_menu import get_back_keyboard
from app.core.container import AppContainer
from app.i18n import normalize_locale, t
from app.infrastructure.db.repositories.pet_fact_repo import PetFactRepository
from app.services.pet_memory import MAX_FACTS_STORED, merge_new_facts
from app.services.pet_service import PetService
from app.services.user_service import UserService

logger = logging.getLogger(__name__)
router = Router(name="memory_router")

SHOWN = 10


class MemoryState(StatesGroup):
    adding = State()


def memory_text(name: str, facts: list, lang: str) -> str:
    if not facts:
        return t("memory.empty", lang, name=name)
    lines = [t("memory.title", lang, name=name)]
    lines += [f"{i}. {f.fact}" for i, f in enumerate(facts[:SHOWN], 1)]
    return "\n".join(lines)


def memory_kb(facts: list, lang: str) -> types.InlineKeyboardMarkup:
    shown = facts[:SHOWN]
    rows = []
    for i in range(0, len(shown), 5):
        rows.append(
            [
                types.InlineKeyboardButton(text=f"🗑 {i + j + 1}", callback_data=f"mem_del:{f.id}")
                for j, f in enumerate(shown[i : i + 5])
            ]
        )
    rows.append(
        [types.InlineKeyboardButton(text=t("memory.add.btn", lang), callback_data="mem_add")]
    )
    rows.append(
        [
            types.InlineKeyboardButton(
                text=t("common.back_menu.btn", lang), callback_data="menu_main"
            )
        ]
    )
    return types.InlineKeyboardMarkup(inline_keyboard=rows)


async def _render(target: types.Message, pet, repo: PetFactRepository, lang: str) -> None:
    facts = await repo.list_active(pet.id, SHOWN)
    await target.edit_text(
        memory_text(pet.name, facts, lang), reply_markup=memory_kb(facts, lang), parse_mode="HTML"
    )


@router.callback_query(F.data == "menu_memory")
@inject
async def show_memory(
    cb: types.CallbackQuery,
    state: FSMContext,
    u_svc: UserService = Provide[AppContainer.user_service],
    p_svc: PetService = Provide[AppContainer.pet_service],
    repo: PetFactRepository = Provide[AppContainer.pet_fact_repo],
) -> None:
    await state.clear()
    await cb.answer()
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)
    pet = await p_svc.get_pet(usr.id)
    if not pet:
        await cb.message.edit_text(t("error.no_pet", lang), reply_markup=get_back_keyboard(lang))
        return
    await _render(cb.message, pet, repo, lang)


@router.callback_query(F.data.startswith("mem_del:"))
@inject
async def delete_fact(
    cb: types.CallbackQuery,
    u_svc: UserService = Provide[AppContainer.user_service],
    p_svc: PetService = Provide[AppContainer.pet_service],
    repo: PetFactRepository = Provide[AppContainer.pet_fact_repo],
) -> None:
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)
    pet = await p_svc.get_pet(usr.id)
    try:
        fact_id = int(cb.data.split(":", 1)[1])
    except ValueError:
        await cb.answer()
        return
    if pet and await repo.soft_delete(fact_id, pet.id):
        await cb.answer(t("memory.deleted", lang))
    else:
        await cb.answer()
    if pet:
        await _render(cb.message, pet, repo, lang)


@router.callback_query(F.data == "mem_add")
@inject
async def ask_fact(
    cb: types.CallbackQuery,
    state: FSMContext,
    u_svc: UserService = Provide[AppContainer.user_service],
) -> None:
    await cb.answer()
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    await state.set_state(MemoryState.adding)
    await cb.message.edit_text(
        t("memory.add.prompt", normalize_locale(usr.language_code)),
        reply_markup=get_back_keyboard(normalize_locale(usr.language_code)),
    )


@router.message(StateFilter(MemoryState.adding), F.text)
@inject
async def save_fact(
    msg: types.Message,
    state: FSMContext,
    u_svc: UserService = Provide[AppContainer.user_service],
    p_svc: PetService = Provide[AppContainer.pet_service],
    repo: PetFactRepository = Provide[AppContainer.pet_fact_repo],
) -> None:
    usr = await u_svc.get_or_create_telegram_user(telegram_id=msg.from_user.id)
    lang = normalize_locale(usr.language_code)
    pet = await p_svc.get_pet(usr.id)
    text = " ".join((msg.text or "").split())
    if not pet or not 3 <= len(text) <= 160 or text.startswith("/"):
        await msg.answer(t("memory.add.invalid", lang))
        return
    known = [f.fact for f in await repo.list_active(pet.id, MAX_FACTS_STORED)]
    if len(known) < MAX_FACTS_STORED and merge_new_facts(known, [text]):
        await repo.add_many(pet.id, [text], source="user")
    await state.clear()
    facts = await repo.list_active(pet.id, SHOWN)
    await msg.answer(
        memory_text(pet.name, facts, lang), reply_markup=memory_kb(facts, lang), parse_mode="HTML"
    )
