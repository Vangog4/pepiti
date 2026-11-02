from aiogram.fsm.state import State, StatesGroup


class OnboardingStates(StatesGroup):
    collecting = State()  # step 1: waiting for the dog's name (text)
    age = State()  # step 2: age buttons
    breed = State()  # step 3: breed buttons / photo / "other"
    breed_text = State()  # step 3b: breed typed or photographed
    goal = State()  # step 4: goal buttons
