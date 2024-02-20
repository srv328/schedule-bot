import sys
import asyncio
import logging
from config import token
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher
from routers import start_command, inline, accont_info, faq, statistic, today_schedule, tomorrow_schedule, settings, \
    week_schedule, clear_schedule, next_lesson, editing


async def main():
    bot = Bot(token=token)
    dp = Dispatcher(storage=MemoryStorage())
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
                       editing.router)

    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        stream=sys.stdout,
                        format='%(asctime)s - %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S')
    asyncio.run(main())
