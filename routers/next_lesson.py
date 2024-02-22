from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
import re
from aiogram.enums.parse_mode import ParseMode
from work_with_db import get_schedule_by_day_offset
from utils import get_local_time, get_week_parity, generate_schedule_response, format_time_str, get_next_two_weeks_dates
from datetime import datetime
from keyboards import next_lesson_markup, schedule_markup


router = Router()


class ReturnButton(StatesGroup):
    return_to_schedule = State()


@router.message(F.text == "Ближайшая пара🔜")
async def nearest_lesson(message: Message, state: FSMContext):
    await state.set_state(ReturnButton.return_to_schedule)
    await message.answer(text='<b>Выберите пару:</b>', parse_mode=ParseMode.HTML, reply_markup=next_lesson_markup)


@router.message(F.text == "Назад🔙", ReturnButton.return_to_schedule)
async def back_btn(message: Message):
    await message.answer("Воспользуйтесь кнопками меню ниже🔽", reply_markup=schedule_markup)


def format_current_lesson_text(pair):
    lesson = generate_schedule_response([pair], '')
    lesson = lesson.replace('Расписание на 🗓', f'Текущая пара: ', -1)
    return lesson


@router.message(F.text == "Текущая🌅")
async def current_lesson(message: Message, state: FSMContext):
    await state.set_state(ReturnButton.return_to_schedule)
    user_id = message.from_user.id

    current_time = get_local_time()
    current_day_of_week = current_time.isoweekday()
    time_now = current_time.time()

    schedule = []
    day = get_schedule_by_day_offset(user_id, current_day_of_week, get_week_parity())

    if not day:
        return await message.answer('<b>У вас сегодня вообще нет пар!</b>', parse_mode=ParseMode.HTML)

    for data in day:
        lesson_start_time = datetime.strptime(data[-3], "%H:%M").time()
        lesson_end_time = datetime.strptime(data[-2], "%H:%M").time()

        if lesson_end_time >= time_now >= lesson_start_time:
            schedule.append(data)

    if len(schedule) == 1:
        current_pair = schedule[0]
        current_lesson_text = format_current_lesson_text(current_pair)

        # определение времени окончания пары
        lesson_end_time = datetime.strptime(current_pair[-2], "%H:%M").time()

        # вычисление времени до окончания пары в секундах
        time_until_end_seconds = (lesson_end_time.hour * 3600 + lesson_end_time.minute * 60 -
                                  (time_now.hour * 3600 + time_now.minute * 60 + time_now.second))

        if time_until_end_seconds > 0:
            # форматирование времени до конца пары
            hours, remainder = divmod(time_until_end_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_until_end_str = format_time_str(0, hours, minutes, seconds)

            # добавление времени до конца пары в текст сообщения
            current_lesson_text += f"\n<b>До конца пары осталось:</b> {time_until_end_str}"

        await message.answer(text=current_lesson_text, parse_mode=ParseMode.HTML)

    elif len(schedule) > 1:
        # обработка случая, когда у пользователя две или более пары в одно и то же время
        await message.answer('<b>У вас две или более пары в данный момент.</b>\nНеобходимо уточнение.'
                             '\nЕсли Вы получили это сообщение, то <a href="https://t.me/shevelev_rv">'
                             'обратитесь ко мне</a>',
                             parse_mode=ParseMode.HTML,
                             disable_web_page_preview=True)
    else:
        await message.answer(text='<b>Сейчас не идёт никакая пара!</b>', parse_mode=ParseMode.HTML)


@router.message(F.text == "Следующая➡️")
async def next_lesson(message: Message, state: FSMContext):
    await state.set_state(ReturnButton.return_to_schedule)
    user_id = message.from_user.id

    current_time = get_local_time()
    current_day_of_week = current_time.isoweekday()
    time_now = current_time.time()

    schedule = []
    date = get_next_two_weeks_dates()
    index = -1
    # добавляем пары, начиная с текущего дня до конца недели
    for i in range(current_day_of_week, 7):
        day = get_schedule_by_day_offset(user_id, i, get_week_parity())
        index += 1
        if not day:
            continue
        for data in day:
            lesson_start_time = datetime.strptime(data[-3], "%H:%M").time()
            if i == current_day_of_week and time_now >= lesson_start_time:
                continue  # пропускаем пары, которые уже начались
            schedule.append((data, date[index]))

    # добавляем пары с начала следующей недели
    for i in range(1, 7):
        day = get_schedule_by_day_offset(user_id, i, (get_week_parity() + 1) % 2)
        index += 1
        if not day:
            continue
        for data in day:
            schedule.append((data, date[index]))

    # добавляем пары, начиная с понедельника до текущего дня
    for i in range(1, current_day_of_week + 1):
        day = get_schedule_by_day_offset(user_id, i, get_week_parity())
        index += 1
        if not day:
            continue
        for data in day:
            lesson_start_time = datetime.strptime(data[-3], "%H:%M").time()
            if i == current_day_of_week + 1 and time_now >= lesson_start_time:
                continue  # Пропускаем пары, которые уже начались
            schedule.append((data, date[index]))

    day_of_week_dict = {1: "понедельник", 2: "вторник", 3: "среда", 4: "четверг", 5: "пятница", 6: "суббота",
                        7: "понедельник", 8: "вторник", 9: "среда", 10: "четверг", 11: "пятница", 12: "суббота"}

    try:
        pair = schedule[0][0]

        day = day_of_week_dict.get(int(pair[1]))
        lesson = generate_schedule_response([pair], '')

        lesson_info = lesson.split('\n')[-2]
        time_start_match = re.search(r'<b>Время:</b>\s+(\d{1,2}:\d{2})', lesson_info)

        if time_start_match:
            time_start = time_start_match.group(1)

            timezone_info = current_time.tzinfo

            date_time_str = schedule[0][1] + ' ' + time_start
            date_time_format = '%d.%m.%Y %H:%M'

            date_time = datetime.strptime(date_time_str, date_time_format).replace(tzinfo=timezone_info)
            time_left = date_time - current_time
            days = time_left.days

            hours, remainder = divmod(time_left.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            time_left_str = format_time_str(days, hours, minutes, seconds)

            new_date_str = schedule[0][1][:-5]
            lesson = lesson.replace('Расписание на 🗓', f'Следующая пара будет: {new_date_str}🗓\n({day})', -1)

            await message.answer(text=f"{lesson}\n<b>До начала следующей пары:</b> {time_left_str}",
                                 parse_mode=ParseMode.HTML)
        else:
            await message.answer(text='<b>У вас произошла ошибка при попытке найти время следующей пары.</b>\n'
                                 'Необходимо уточнение.'
                                 '\nЕсли Вы получили это сообщение, то <a href="https://t.me/shevelev_rv">'
                                 'обратитесь ко мне</a>',
                                 parse_mode=ParseMode.HTML,
                                 disable_web_page_preview=True)
    except IndexError:  # пар нет
        await message.answer(text=f"<b>У вас больше нет пар!</b> Уже выпустились?", parse_mode=ParseMode.HTML)
