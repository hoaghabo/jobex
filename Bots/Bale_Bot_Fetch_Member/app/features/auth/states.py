from aiogram.fsm.state import State, StatesGroup


class RegisterStates(StatesGroup):
    waiting_for_first_name = State()
    waiting_for_last_name = State()
    waiting_for_phone_number = State()
    waiting_for_email = State()
    waiting_for_gender = State()
    waiting_for_city = State()
    waiting_for_day_birthdate = State()
    waiting_for_month_birthdate = State()
    waiting_for_year_birthdate = State()
    choose_type_of_customer = State()
