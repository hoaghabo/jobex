from aiogram.fsm.state import State, StatesGroup


class RegisterStates(StatesGroup):
    waiting_for_full_name = State()
    waiting_for_phone_number = State()
    choose_type_of_customer = State()
