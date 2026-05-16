from aiogram.fsm.state import State, StatesGroup


class EditProfileStates(StatesGroup):
    choosing_field = State()
    waiting_value = State()
