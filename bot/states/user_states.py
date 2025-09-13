from aiogram.fsm.state import StatesGroup, State

class UserStates(StatesGroup):
    language = State()
    name = State()
    phone = State()

