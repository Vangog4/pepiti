from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from dependency_injector.wiring import Provide, inject

from app.bot.keyboards.edit_profile import (
    TIMEZONE_OPTIONS,
    get_age_inline,
    get_edit_profile_keyboard,
    get_size_inline,
    get_timezone_inline,
    get_training_level_inline,
    translate_option,
)
from app.bot.keyboards.main_menu import get_back_keyboard
from app.bot.states.edit_profile import EditProfileStates
from app.core.container import AppContainer
from app.i18n import normalize_locale, t
from app.services.pet_service import PetService
from app.services.user_service import UserService

router = Router(name="edit_profile_router")

# Maps field name → (i18n_prompt_key, keyboard_factory | None)
FIELD_LABELS: dict[str, tuple[str, object]] = {
    "name": ("edit_profile.field.name.prompt", None),
    "breed": ("edit_profile.field.breed.prompt", None),
    "goal": ("edit_profile.field.goal.prompt", None),
    "training_level": ("edit_profile.field.level.prompt", get_training_level_inline),
    "age_category": ("edit_profile.field.age.prompt", get_age_inline),
    "size_category": ("edit_profile.field.size.prompt", get_size_inline),
    "timezone": ("edit_profile.field.timezone.prompt", get_timezone_inline),
}

# Fields that belong to UserModel (not PetModel)
USER_FIELDS = {"timezone"}

# VALUE_MAP maps callback_data → stored DB value.
# Size/age values are stored as Russian strings (data model constraint; migration required to change).
VALUE_MAP = {
    "set_size_small": "Маленький (до 10 кг)",
    "set_size_medium": "Средний (10–25 кг)",
    "set_size_large": "Крупный (25–45 кг)",
    "set_size_giant": "Гигант (45+ кг)",
    "set_age_1": "Щенок (до 4 мес)",
    "set_age_2": "Щенок (4–12 мес)",
    "set_age_3": "Молодой (1–3 года)",
    "set_age_4": "Взрослый (3–7 лет)",
    "set_age_5": "Пожилой (7+ лет)",
}
for i in range(1, 6):
    VALUE_MAP[f"set_level_{i}"] = str(i)
for i, (tz_code, _, _) in enumerate(TIMEZONE_OPTIONS):
    VALUE_MAP[f"set_tz_{i}"] = tz_code


@router.callback_query(F.data == "menu_edit_profile")
@inject
async def start_edit_profile(
    cb: types.CallbackQuery,
    state: FSMContext,
    u_svc: UserService = Provide[AppContainer.user_service],
) -> None:
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)
    await state.set_state(EditProfileStates.choosing_field)
    await cb.message.edit_text(
        t("edit_profile.title", lang),
        reply_markup=get_edit_profile_keyboard(lang),
        parse_mode="HTML",
    )
    await cb.answer()


@router.callback_query(EditProfileStates.choosing_field, F.data.startswith("edit_field_"))
@inject
async def choose_profile_field(
    cb: types.CallbackQuery,
    state: FSMContext,
    u_svc: UserService = Provide[AppContainer.user_service],
) -> None:
    field_name = cb.data.replace("edit_field_", "")
    if field_name not in FIELD_LABELS:
        await cb.answer()
        return

    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)

    prompt_key, keyboard_factory = FIELD_LABELS[field_name]
    await state.update_data(field_name=field_name)
    await state.set_state(EditProfileStates.waiting_value)

    reply_markup = keyboard_factory(lang) if keyboard_factory else get_back_keyboard(lang)
    await cb.message.edit_text(
        f"✏️ {t(prompt_key, lang)}",
        reply_markup=reply_markup,
        parse_mode="HTML",
    )
    await cb.answer()


@router.callback_query(EditProfileStates.waiting_value, F.data.startswith("set_"))
@inject
async def save_profile_field_inline(
    cb: types.CallbackQuery,
    state: FSMContext,
    u_svc: UserService = Provide[AppContainer.user_service],
    p_svc: PetService = Provide[AppContainer.pet_service],
) -> None:
    new_value = VALUE_MAP.get(cb.data)
    if not new_value:
        await cb.answer()
        return

    data = await state.get_data()
    field_name = data.get("field_name")

    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)

    if field_name in USER_FIELDS:
        setattr(usr, field_name, new_value)
        await u_svc.repo.session.commit()
    else:
        pet = await p_svc.get_pet(usr.id)
        if not pet:
            await state.clear()
            await cb.message.edit_text(
                t("error.no_pet", lang), reply_markup=get_back_keyboard(lang)
            )
            await cb.answer()
            return
        setattr(pet, field_name, new_value)
        await p_svc.repo.session.commit()
    await state.clear()

    display_value = translate_option(new_value, lang)
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=t("edit_profile.edit_more.btn", lang), callback_data="menu_edit_profile"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text=t("common.back_menu.btn", lang), callback_data="menu_main"
                )
            ],
        ]
    )
    await cb.message.edit_text(
        t("edit_profile.saved", lang, value=display_value),
        reply_markup=kb,
        parse_mode="HTML",
    )
    await cb.answer()


@router.message(EditProfileStates.waiting_value)
@inject
async def save_profile_field_text(
    msg: types.Message,
    state: FSMContext,
    u_svc: UserService = Provide[AppContainer.user_service],
    p_svc: PetService = Provide[AppContainer.pet_service],
) -> None:
    data = await state.get_data()
    field_name = data.get("field_name")
    if not msg.text or not field_name:
        return

    usr = await u_svc.get_or_create_telegram_user(telegram_id=msg.from_user.id)
    lang = normalize_locale(usr.language_code)

    text = msg.text.strip()
    if not text:
        await msg.answer(t("edit_profile.error.empty", lang))
        return
    if len(text) > 50:
        await msg.answer(t("edit_profile.error.too_long", lang, n=len(text)))
        return

    try:
        await msg.delete()
    except Exception:
        pass

    if field_name in USER_FIELDS:
        setattr(usr, field_name, text)
        await u_svc.repo.session.commit()
    else:
        pet = await p_svc.get_pet(usr.id)
        if not pet:
            await state.clear()
            await msg.answer(t("error.no_pet", lang), reply_markup=get_back_keyboard(lang))
            return
        setattr(pet, field_name, text)
        await p_svc.repo.session.commit()
    await state.clear()

    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=t("edit_profile.edit_more.btn", lang), callback_data="menu_edit_profile"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text=t("common.back_menu.btn", lang), callback_data="menu_main"
                )
            ],
        ]
    )
    await msg.answer(
        t("edit_profile.saved", lang, value=text),
        reply_markup=kb,
        parse_mode="HTML",
    )
