from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from utils import bot
from aiogram.enums.parse_mode import ParseMode
from keyboards import clear_button, schedule_markup
from work_with_db import has_schedule, execute_query


router = Router()


@router.message(F.text == "Очистить🗑")
async def clear_schedule(message: Message):
    if has_schedule(message.from_user.id):
        await message.answer(text="Вы уверены, что хотите очистить расписание?\n"
                                  "<b>Внимание</b>❗️\nЭто действие <b>нельзя отменить</b>⚠", reply_markup=clear_button,
                             parse_mode=ParseMode.HTML)
    else:
        await message.answer(text="<b>Расписание пустое, нечего очищать!</b>",
                             parse_mode=ParseMode.HTML,
                             reply_markup=schedule_markup)
        gif = FSInputFile("media/лосяш.mp4")
        await message.answer_video(gif)


@router.callback_query(lambda query: query.data == 'yes_clear')
async def clear_yes(query: CallbackQuery):
    delete_query = "DELETE FROM schedule WHERE user_id = ?"
    execute_query(delete_query, query.from_user.id)
    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    await query.message.answer(text="<b>Расписание успешно очищено!</b>",
                               parse_mode=ParseMode.HTML,
                               reply_markup=schedule_markup)


@router.callback_query(lambda query: query.data == 'no_clear')
async def clear_no(query: CallbackQuery):
    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    await query.message.answer(text="<b>Действие отменено</b>♻",
                               parse_mode=ParseMode.HTML,
                               reply_markup=schedule_markup)
