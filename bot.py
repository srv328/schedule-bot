import sys
import asyncio
import logging
from utils.anti_flood import ThrottlingMiddleware
from aiogram.fsm.storage.redis import RedisStorage
from aiogram import Dispatcher
from routers import (
    start_command, inline, accont_info, faq,
    statistic, today_schedule, tomorrow_schedule, settings,
    week_schedule, clear_schedule, next_lesson, editing, admin_panel,
    other_messages
)
from utils.bot_entity import bot


async def main():
    storage = RedisStorage.from_url('redis://localhost:6379/0')
    dp = Dispatcher(storage=storage)
    dp.message.middleware.register(ThrottlingMiddleware(storage=storage))
    dp.include_routers(start_command.router,
                       accont_info.router,
                       faq.router,
                       today_schedule.router,
                       tomorrow_schedule.router,
                       inline.router,
                       statistic.router,
                       settings.router,
                       week_schedule.router,
                       clear_schedule.router,
                       next_lesson.router,
                       editing.router,
                       admin_panel.router,
                       other_messages.router)
    try:
        await dp.start_polling(bot)
    except Exception as ex:
        logging.error(f"[!!! Exception] - {ex}", exc_info=True)
    finally:
        await bot.session.close()
        await dp.storage.close()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        stream=sys.stdout,
                        format='%(asctime)s - %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S')
    asyncio.run(main())
