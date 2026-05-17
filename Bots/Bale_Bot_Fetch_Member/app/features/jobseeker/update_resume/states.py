from aiogram.fsm.state import State, StatesGroup


class ResumeJobSeekerUpdateStates(StatesGroup):
    waiting_for_degree = State()
    waiting_for_work_enthusiasts = State()
    waiting_for_salary_range = State()
    waiting_for_work_location_priority = State()
    waiting_for_success = State()