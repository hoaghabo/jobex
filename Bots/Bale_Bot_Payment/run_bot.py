import asyncio

from app.bot.factory import create_bot, create_dispatcher
from app.core.logging import setup_logging
from app.routers.main import setup_routers


async def main():
    setup_logging()

    bot = create_bot()
    dp = create_dispatcher()

    setup_routers(dp)

    me = await bot.get_me()
    print(f"Bot started: @{me.username} ({me.id})")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
