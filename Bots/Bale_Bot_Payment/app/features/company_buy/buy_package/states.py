from aiogram.fsm.state import State, StatesGroup


class ResumeJobSeekerCreateStates(StatesGroup):
    waiting_for_city = State()
    waiting_for_day_birthday = State()
    waiting_for_month_birthday = State()
    waiting_for_year_birthday = State()
    waiting_for_degree = State()
    waiting_for_email = State()
    waiting_for_work_enthusiasts = State()
    waiting_for_salary_range = State()
    waiting_for_work_location_priority = State()
    waiting_for_campaign_request = State()
    waiting_for_success = State()