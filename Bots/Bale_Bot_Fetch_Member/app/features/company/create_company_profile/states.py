from aiogram.fsm.state import State, StatesGroup


class CompanyProfileCreateStates(StatesGroup):
    waiting_for_company_name = State()
    waiting_for_company_role = State()
    waiting_for_organization_size = State()
    waiting_for_city = State()
    waiting_for_industry = State()
    waiting_for_full_address = State()
    waiting_for_website = State()
    waiting_for_landline_phone = State()
