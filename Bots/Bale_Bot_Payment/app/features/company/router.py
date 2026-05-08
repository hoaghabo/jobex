from aiogram import Router
from .profile.router import router  as company_profile_routert
from .creatjobpost.router import router as company_jobposts_router
 
router = Router(name="company")
router.include_router(company_profile_routert)
router.include_router(company_jobposts_router)

