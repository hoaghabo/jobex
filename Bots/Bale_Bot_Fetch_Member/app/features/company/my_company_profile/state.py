from aiogram.fsm.state import State, StatesGroup


class EditMyCompanyProfileStates(StatesGroup):
    waiting_for_choose_company = State()
    waiting_for_choose_Edit_action = State()
    waiting_for_edit_company_name = State()
    waiting_for_edit_company_role = State()
    waiting_for_edit_organization_size = State()
    waiting_for_edit_city = State()
    waiting_for_edit_industry = State()
    waiting_for_edit_full_address = State()
    waiting_for_edit_website = State()
    waiting_for_edit_landline_phone = State()
