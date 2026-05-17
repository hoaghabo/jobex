from aiogram.fsm.state import State, StatesGroup


class ResumeJobSeekerAskCampaignsStates(StatesGroup):
    waiting_for_choose_campaign = State()