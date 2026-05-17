from aiogram import Router
from .main_menu.handlers import router  as company_main_menu_router
from .create_company_profile.router import router  as company_profile_router
from .create_job_post.router import router as company_jobposts_router
from .my_company_profile.router import router as my_company_profile_router
from .my_job_post.router import router as my_job_post_router
 
router = Router(name="company")
router.include_router(company_main_menu_router)
router.include_router(company_profile_router)
router.include_router(company_jobposts_router)
router.include_router(my_company_profile_router)
router.include_router(my_job_post_router)

