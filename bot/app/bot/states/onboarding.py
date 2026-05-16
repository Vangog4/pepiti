from aiogram.fsm.state import State, StatesGroup


class OnboardingStates(StatesGroup):
    collecting = State()   # waiting for free-form intro message
    clarifying = State()   # waiting for follow-up on missing_fields
