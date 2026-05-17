from aiogram.fsm.state import State, StatesGroup


class CompanyJobPostListStates(StatesGroup):
    waiting_for_choose_company = State()
    waiting_for_choose_job_post = State()
    waiting_for_choose_job_post_action = State()
