from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.enums.parse_mode import ParseMode
from datetime import timedelta
from work_with_db import get_schedule_by_day_offset
from utils import day_of_week_dict, generate_schedule_response, get_week_parity, get_local_time

router = Router()


@router.message(F.text == "На завтра📚")
async def get_schedule_tomorrow(message: Message):

    current_number_day = get_local_time()
    next_day_of_week = current_number_day + timedelta(days=1)
    next_day_of_week_number = next_day_of_week.isoweekday()

    user_id = message.from_user.id
    tomorrow_schedule = get_schedule_by_day_offset(user_id, next_day_of_week_number, get_week_parity())

    if next_day_of_week_number == 7:
        await message.answer("Сегодня суббота, а значит завтра <b>ВЫХОДНООООЙ!</b>\nПриятного времяпрепровождения!",
                             parse_mode=ParseMode.HTML)
        gif = FSInputFile("media/отдыхаем.mp4")
        await message.answer_video(gif)
        return

    if not tomorrow_schedule:
        await message.answer("Завтра у Вас нет занятий, <b>можете расслабиться!</b>", parse_mode=ParseMode.HTML)
        gif = FSInputFile("media/завтра отдыхаем.mp4")
        await message.answer_video(gif)
        return

    tomorrow_day_name = day_of_week_dict.get(next_day_of_week_number, "Недопустимый индекс")
    response_text = generate_schedule_response(tomorrow_schedule, f"завтра\n{tomorrow_day_name.capitalize()}"
                                                                  f" <i>{next_day_of_week.day:02d}."
                                                                  f"{next_day_of_week.month:02d}</i>")
    await message.answer(response_text, parse_mode=ParseMode.HTML)
