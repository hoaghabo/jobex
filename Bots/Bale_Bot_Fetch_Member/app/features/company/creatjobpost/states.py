from aiogram.fsm.state import State, StatesGroup


class CompanyJobPostCreateStates(StatesGroup):
    waiting_for_job_title = State()
    waiting_for_cooperation_type = State()
    waiting_for_degree = State()
    waiting_for_minimum_work_experience = State()
    waiting_for_required_skills = State()
    waiting_for_job_description = State()
    waiting_for_attendance_type = State()
    waiting_for_working_days = State()
    waiting_for_has_overtime = State()
    waiting_for_working_hours = State()
    waiting_for_working_hours_description = State()
    waiting_for_is_salary_negotiable = State()
    waiting_for_is_salary_description = State()
    waiting_for_is_benefits = State()
