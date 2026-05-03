from aiogram import Dispatcher

from app.features.auth.router import router as auth_router
from app.features.event.router import router as event_router
from app.features.my_event.router import router as my_event_router
from app.features.adminpanel.registeredlist.router import router as registeredlist_router



def setup_routers(dp: Dispatcher):
    dp.include_router(auth_router)
    dp.include_router(event_router)
    dp.include_router(my_event_router)
    dp.include_router(registeredlist_router)
