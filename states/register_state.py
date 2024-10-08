from aiogram.fsm.state import State, StatesGroup

class RegisterStates(StatesGroup):
    type = State()
    fish = State()
    phone = State()
