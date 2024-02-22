from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode

router = Router()


@router.message()
async def not_handled_messages(message: Message):
    await message.answer(text="Прости, но я <b>тебя не понимаю</b>🧸\n"
                              "Напиши /start для корректной работы бота🤖",
                         parse_mode=ParseMode.HTML)


@router.callback_query()
async def not_handled_queries(query: CallbackQuery):
    await query.message.answer(text="Прости, но я <b>тебя не понимаю</b>🧸\n"
                                    "Напиши /start для корректной работы бота🤖",
                               parse_mode=ParseMode.HTML)
