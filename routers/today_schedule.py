from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.enums.parse_mode import ParseMode
from work_with_db import get_schedule_by_day_offset
from utils import day_of_week_dict, generate_schedule_response, get_week_parity, get_local_time

router = Router()


@router.message(F.text == "На сегодня📖")
async def get_schedule_today(message: Message):

    current_time = get_local_time()
    current_day_of_week = current_time.isoweekday()

    if current_day_of_week == 7:
        await message.answer("Сегодня воскресенье, а значит <b>ВЫХОДНООООЙ!</b>\nСильно не расслабляемся,"
                             " ведь завтра понедельник :)", parse_mode=ParseMode.HTML)
        gif = FSInputFile("media/отдыхаем.mp4")
        await message.answer_video(gif)
        return

    user_id = message.from_user.id
    current_schedule = get_schedule_by_day_offset(user_id, current_day_of_week, get_week_parity())

    if not current_schedule:
        await message.answer("Сегодня у Вас нет занятий, <b>отдыхаем!</b>", parse_mode=ParseMode.HTML)
        gif = FSInputFile("media/сегодня отдыхаем.mp4")
        await message.answer_video(gif)
        return

    current_day_name = day_of_week_dict.get(current_day_of_week, "Недопустимый индекс")
    response_text = generate_schedule_response(current_schedule, f"сегодня\n{current_day_name.capitalize()}"
                                                                 f" <i>{current_time.day:02d}"
                                                                 f".{current_time.month:02d}</i>")
    await message.answer(response_text, parse_mode=ParseMode.HTML)
