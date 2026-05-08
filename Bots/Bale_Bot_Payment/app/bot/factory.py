from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode

from app.config import settings
from app.bot.bale_api import BALE_API


def create_bot() -> Bot:
    session = AiohttpSession(api=BALE_API)

    bot = Bot(
        token=settings.BALE_BOT_TOKEN,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    return bot


def create_dispatcher() -> Dispatcher:
    return Dispatcher()
