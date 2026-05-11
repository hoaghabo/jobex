from aiogram.fsm.state import State, StatesGroup


class RegisterStates(StatesGroup):
    waiting_for_phone_number = State()
