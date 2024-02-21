from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.enums.parse_mode import ParseMode
from work_with_db import get_schedule_statistics
from utils import generate_schedule_statistics_message

router = Router()


@router.message(F.text == "Статистика📊")
async def schedule_statistics(message: Message):
    user_id = message.from_user.id
    even_schedule, odd_schedule = get_schedule_statistics("schedule", user_id)
    statistics_message = generate_schedule_statistics_message(even_schedule, odd_schedule)
    share = [[InlineKeyboardButton(
        text='Поделиться статистикой',
        switch_inline_query=f'Статистика')]]

    inline_markup = InlineKeyboardMarkup(inline_keyboard=share)
    if statistics_message == 'У вас пока нет занятий в расписании.':
        await message.answer('У вас пока <b>нет занятий</b>! Каникулы?)', parse_mode=ParseMode.HTML)
        gif = FSInputFile("media/копатыч.mp4")
        await message.answer_video(gif)
    else:
        await message.answer(statistics_message, reply_markup=inline_markup, parse_mode=ParseMode.HTML)
