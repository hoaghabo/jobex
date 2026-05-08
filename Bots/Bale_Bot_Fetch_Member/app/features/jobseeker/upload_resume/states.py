from aiogram.fsm.state import State, StatesGroup


class ResumeJobSeekerUploadStates(StatesGroup):
    waiting_for_resume_upload = State()