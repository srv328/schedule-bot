from aiogram.types import CallbackQuery, KeyboardButton, ReplyKeyboardMarkup
from aiogram import F
from aiogram.types import Message
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.utilities import (
    get_number_of_subject_emoji, day_translation, day_of_week_dict, get_lesson_info,
    day_translation_form, get_available_lesson_times
)
from utils.bot_entity import bot
from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest
from utils.work_with_db import get_schedule_by_day_offset, delete_lesson_by_params, add_lesson_to_schedule
from utils.keyboards import (
    parity_markup, days_markup, manage_markup, yes_no_button, lesson_type_markup,
    lesson_priority_markup, cancel_markup, schedule_markup
)
from aiogram import Router

router = Router()


class Edit(StatesGroup):
    parity = State()
    day = State()
    lesson = State()


class AddLesson(StatesGroup):
    Time = State()
    Subject = State()
    TeacherName = State()
    LessonType = State()
    Evaluation = State()
    Classroom = State()
    Final = State()


@router.message(F.text == "Пропустить добавление♻️")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    data = await state.get_data()
    query = data.get('query')
    await state.set_state(Edit.day)
    await select_week_day(message.from_user.id, message.chat.id, message.message_id, state, True)


@router.message(F.text == "Редактировать✏️")
async def edit_function(message: Message, state: FSMContext):
    await message.answer(text="<b>Выберите неделю для редактирования:</b>🔎",
                         parse_mode=ParseMode.HTML,
                         reply_markup=parity_markup)
    await state.set_state(Edit.parity)


@router.callback_query(lambda query: query.data == 'back')
async def return_to_back(query: CallbackQuery, state: FSMContext):
    with suppress(TelegramBadRequest):
        await bot.edit_message_text(
            text="<b>Выберите неделю для редактирования:</b>🔎",
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            reply_markup=parity_markup,
            parse_mode=ParseMode.HTML
        )
        await state.set_state(Edit.parity)


@router.callback_query(lambda query: query.data in ['even_week', 'odd_week'], Edit.parity)
async def select_week_parity(query: CallbackQuery, state: FSMContext):
    week_parity = query.data
    await state.update_data(week_parity=week_parity)

    week_name = "чётную" if query.data == 'even_week' else "нечётную"
    message_text = f"<i>Редактируем {week_name} неделю</i> 🍑"

    await bot.edit_message_text(text=message_text,
                                chat_id=query.message.chat.id,
                                message_id=query.message.message_id,
                                reply_markup=days_markup,
                                parse_mode=ParseMode.HTML)

    await state.set_state(Edit.day)


async def select_week_day(user_id: int, chat_id: int, message_id: int,
                          state: FSMContext, cancel=False, show=True, add=False):
    await state.set_state(Edit.day)
    data = await state.get_data()
    week_parity = data.get('week_parity')
    selected_day = data.get('day')
    day_offset_base = {'monday': 1, 'tuesday': 2, 'wednesday': 3, 'thursday': 4, 'friday': 5, 'saturday': 6}
    day_offset = day_offset_base[selected_day]

    week_parity_int = 0 if week_parity == 'even_week' else 1

    schedule_data = get_schedule_by_day_offset(user_id, day_offset % 7, week_parity_int)

    keyboard_buttons = []
    builder = InlineKeyboardBuilder()
    if not schedule_data:
        builder.button(
            text="Добавить пару ✳️",
            callback_data=f"add_lesson_{selected_day}_{week_parity}"
        )

        builder.button(
            text="Назад 🔙",
            callback_data=f"back_to_edit_week_{week_parity}"
        )

        builder.adjust(1)
        with suppress(TelegramBadRequest):
            if not cancel:
                await bot.edit_message_text(
                    text=f"<i>Расписание на {day_translation_form.get(selected_day)} "
                         f"({'четную' if week_parity == 'even_week' else 'нечетную'}) неделю:</i> 📅\n"
                         f"<b>В этот день нет пар! Хотите добавить?</b>",
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=builder.as_markup(),
                    parse_mode=ParseMode.HTML
                )
            else:
                if show:
                    await bot.send_message(
                        text=f"<b>Добавление отменено♻️</b>",
                        chat_id=chat_id,
                        parse_mode=ParseMode.HTML,
                        reply_markup=schedule_markup
                    )
                if add:
                    await bot.send_message(
                        text=f"<b>Пара успешно добавлена!🎉</b>",
                        chat_id=chat_id,
                        reply_markup=schedule_markup,
                        parse_mode=ParseMode.HTML
                    )
                await bot.send_message(
                    text=f"<i>Расписание на {day_translation_form.get(selected_day)} "
                         f"({'четную' if week_parity == 'even_week' else 'нечетную'}) неделю:</i> 📅\n"
                         f"<b>В этот день нет пар! Хотите добавить?</b>",
                    chat_id=chat_id,
                    reply_markup=builder.as_markup(),
                    parse_mode=ParseMode.HTML
                )

    else:

        for lesson in schedule_data:
            subject_number = lesson[-1]  # номер пары
            subject_emoji = get_number_of_subject_emoji(subject_number)

            start_time = lesson[-3]  # время начала пары
            end_time = lesson[-2]  # время окончания пары

            button_text = f"{subject_emoji} {start_time} - {end_time}"
            button_callback_data = f"lesson_{subject_number}_{selected_day}_{week_parity}"
            builder.button(text=button_text, callback_data=button_callback_data)

        # если еще нет 8 пар
        if len(schedule_data) != 8:
            builder.button(
                text="Добавить пару ✳️",
                callback_data=f"add_lesson_{selected_day}_{week_parity}"
            )

        builder.button(
            text="Назад 🔙",
            callback_data=f"back_to_edit_week_{week_parity}"
        )

        builder.adjust(1)

        with suppress(TelegramBadRequest):
            if not cancel:
                await bot.edit_message_text(
                    text=f"<i>Расписание на {day_translation_form.get(selected_day)} "
                         f"({'четную' if week_parity == 'even_week' else 'нечетную'}) неделю:</i> 📅",
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=builder.as_markup(),
                    parse_mode=ParseMode.HTML
                )
            else:
                if show:
                    await bot.send_message(
                        text=f"<b>Добавление отменено♻️</b>",
                        chat_id=chat_id,
                        parse_mode=ParseMode.HTML,
                        reply_markup=schedule_markup
                    )
                if add:
                    await bot.send_message(
                        text=f"<b>Пара успешно добавлена!🎉</b>",
                        chat_id=chat_id,
                        reply_markup=schedule_markup,
                        parse_mode=ParseMode.HTML
                    )
                await bot.send_message(
                    text=f"<i>Расписание на {day_translation_form.get(selected_day)} "
                         f"({'четную' if week_parity == 'even_week' else 'нечетную'}) неделю:</i> 📅",
                    chat_id=chat_id,
                    reply_markup=builder.as_markup(),
                    parse_mode=ParseMode.HTML
                )


@router.callback_query(lambda query: query.data in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'],
                       Edit.day)
async def edit_day(query: CallbackQuery, state: FSMContext):
    await state.update_data(day=query.data)
    await select_week_day(query.from_user.id, query.message.chat.id, query.message.message_id, state)


@router.callback_query(lambda query: query.data.startswith('back_to_edit_week'))
async def back_to_edit_week(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    week_parity = data.get('week_parity')
    message_text = f"<i>Редактируем " \
                   f"{'чётную' if week_parity == 'even_week' else 'нечётную'} неделю</i> 🍑"
    with suppress(TelegramBadRequest):
        await bot.edit_message_text(
            text=message_text,
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            reply_markup=days_markup,
            parse_mode=ParseMode.HTML
        )
        await state.set_state(Edit.day)


@router.callback_query(lambda query: query.data.startswith('lesson_'))
async def handle_lesson_button(query: CallbackQuery, state: FSMContext):
    # разбиваем callback_data
    await state.set_state(Edit.lesson)
    split_data = query.data.rsplit('_', 4)
    subject_number = split_data[1]
    day_in_english = split_data[2]
    week_parity = 0 if split_data[3] + '_' + split_data[4] == 'even_week' else 1
    await state.update_data(subject_number=subject_number)
    day_in_russian = day_translation.get(day_in_english)

    day_number = next((k for k, v in day_of_week_dict.items() if v == day_in_russian), None)

    lesson_info = get_lesson_info(query.from_user.id, subject_number, day_number, week_parity)

    await bot.edit_message_text(text=lesson_info,
                                chat_id=query.message.chat.id,
                                message_id=query.message.message_id,
                                reply_markup=manage_markup,
                                parse_mode=ParseMode.HTML)


@router.callback_query(lambda query: query.data == 'delete_pair', Edit.lesson)
async def delete_lesson(query: CallbackQuery, state: FSMContext):
    await bot.edit_message_text(text="<b>Вы уверены, что хотите удалить текущую пару?</b>\n"
                                     "<i>Это действие нельзя будет отменить!</i>",
                                chat_id=query.message.chat.id,
                                message_id=query.message.message_id,
                                reply_markup=yes_no_button,
                                parse_mode=ParseMode.HTML)


@router.callback_query(lambda query: query.data == 'back_to_manage_day')
async def back_to_manage_week(query: CallbackQuery, state: FSMContext):
    await select_week_day(query.from_user.id, query.message.chat.id, query.message.message_id, state)


@router.callback_query(lambda query: query.data == 'yes', Edit.lesson)
async def apply_delete(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    week_parity = data.get('week_parity')
    selected_day = data.get('day')
    subject_number = data.get('subject_number')

    day_offset_base = {'monday': 1, 'tuesday': 2, 'wednesday': 3, 'thursday': 4, 'friday': 5, 'saturday': 6}
    day_offset = day_offset_base[selected_day]

    week_parity_int = 0 if week_parity == 'even_week' else 1
    delete_lesson_by_params(int(query.from_user.id), subject_number, day_offset % 7, week_parity_int)

    await query.answer("Пара успешно удалена!")
    await select_week_day(query.from_user.id, query.message.chat.id, query.message.message_id, state)


@router.callback_query(lambda query: query.data == 'no', Edit.lesson)
async def cancel_delete(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    week_parity = data.get('week_parity')
    selected_day = data.get('day')
    subject_number = data.get('subject_number')

    day_offset_base = {'monday': 1, 'tuesday': 2, 'wednesday': 3, 'thursday': 4, 'friday': 5, 'saturday': 6}
    day_offset = day_offset_base[selected_day]

    week_parity_int = 0 if week_parity == 'even_week' else 1

    await query.answer("Удаление отменено!")
    lesson_info = get_lesson_info(query.from_user.id, subject_number, day_offset, week_parity_int)

    await bot.edit_message_text(text=lesson_info,
                                chat_id=query.message.chat.id,
                                message_id=query.message.message_id,
                                reply_markup=manage_markup,
                                parse_mode=ParseMode.HTML)


@router.callback_query(lambda query: query.data.startswith('add_lesson'), Edit.day)
async def add_lesson(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    week_parity = data.get('week_parity')
    selected_day = data.get('day')
    subject_number = data.get('subject_number')
    day_offset_base = {'monday': 1, 'tuesday': 2, 'wednesday': 3, 'thursday': 4, 'friday': 5, 'saturday': 6}
    day_offset = day_offset_base[selected_day]
    times = []
    week_parity_int = 0 if week_parity == 'even_week' else 1

    available_lesson_times = get_available_lesson_times(query.from_user.id, day_offset, week_parity_int)
    formatted_intervals = [f'{start} - {end}' for start, end in available_lesson_times]

    row_width = 4  # количество кнопок в одной строке
    for i in range(0, len(available_lesson_times), row_width):
        row = available_lesson_times[i:i + row_width]
        times.append([KeyboardButton(text=f"{start_time} - {end_time}") for start_time, end_time in row])

    await state.update_data(available_times=formatted_intervals)

    times.append([KeyboardButton(text="Пропустить добавление♻️")])
    times_markup = ReplyKeyboardMarkup(keyboard=times, resize_keyboard=True, one_time_keyboard=True)

    await query.message.answer(
        text="<b>Выберите время:</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=times_markup
    )
    await state.set_state(AddLesson.Time)


@router.message(AddLesson.Time, F.text.in_(['8:30 - 10:00',
                                            '10:10 - 11:40',
                                            '11:50 - 13:20',
                                            '13:30 - 15:00',
                                            '15:10 - 16:40',
                                            '16:50 - 18:20',
                                            '18:30 - 20:00',
                                            '20:10 - 21:40']))
async def process_time(message: Message, state: FSMContext):
    time = message.text
    data = await state.get_data()
    available_times = data.get('available_times')

    if time not in available_times:
        await message.answer(text="<b>Пожалуйста, выберите время из предоставленных вариантов.</b>",
                             parse_mode=ParseMode.HTML)
        return

    await state.update_data(time=time)
    await message.answer(
        text="<b>Введите название предмета:</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=cancel_markup
    )
    await state.set_state(AddLesson.Subject)


@router.message(AddLesson.Time)
async def incorrect_process_time(message: Message, state: FSMContext):
    data = await state.get_data()
    week_parity = data.get('week_parity')
    selected_day = data.get('day')
    subject_number = data.get('subject_number')
    day_offset_base = {'monday': 1, 'tuesday': 2, 'wednesday': 3, 'thursday': 4, 'friday': 5, 'saturday': 6}
    day_offset = day_offset_base[selected_day]
    times = []
    week_parity_int = 0 if week_parity == 'even_week' else 1

    available_lesson_times = get_available_lesson_times(message.from_user.id, day_offset, week_parity_int)

    row_width = 4  # количество кнопок в одной строке

    for i in range(0, len(available_lesson_times), row_width):
        row = available_lesson_times[i:i + row_width]
        times.append([KeyboardButton(text=f"{start_time} - {end_time}") for start_time, end_time in row])

    times.append([KeyboardButton(text="Пропустить добавление♻️")])
    times_markup = ReplyKeyboardMarkup(keyboard=times, resize_keyboard=True, one_time_keyboard=True)
    await message.answer(
            text="<b>Воспользуйся кнопками!</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=times_markup
    )


@router.message(AddLesson.Subject, F.text, F.text.len() < 100)
async def process_subject(message: Message, state: FSMContext):
    subject = message.text
    await state.update_data(subject=subject)

    await message.answer(
        text="<b>Введите ФИО преподавателя:</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=cancel_markup
    )
    await state.set_state(AddLesson.TeacherName)


@router.message(AddLesson.Subject)
async def incorrect_process_subject(message: Message, state: FSMContext):
    await message.answer(
        text="<b>Я не верю, что у предмета может быть такое длинное название!</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=cancel_markup
    )


@router.message(AddLesson.TeacherName, F.text, F.text.len() < 255)
async def process_teacher_name(message: Message, state: FSMContext):
    teacher_name = message.text
    await state.update_data(teacher_name=teacher_name)

    await message.answer(
        text="<b>Выберите тип занятия:</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=lesson_type_markup
    )
    await state.set_state(AddLesson.LessonType)


@router.message(AddLesson.TeacherName)
async def incorrect_process_teacher_name(message: Message, state: FSMContext):
    print(message.text)
    await message.answer(
        text="<b>Слишком длинное ФИО.....</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=cancel_markup
    )


@router.message(AddLesson.LessonType, F.text, F.text.in_(['Практика💻', 'Лекция✏️']))
async def process_lesson_type(message: Message, state: FSMContext):
    lesson_type = message.text
    # Здесь вы можете добавить валидацию и обработку введенных данных
    await state.update_data(lesson_type=lesson_type)

    await message.answer(
        text="<b>Выберите тип оценивания:</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=lesson_priority_markup
    )
    await state.set_state(AddLesson.Evaluation)


@router.message(AddLesson.LessonType)
async def incorrect_process_lesson_type(message: Message, state: FSMContext):
    await message.answer(
        text="<b>Выберите тип занятия из меню ниже!</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=lesson_type_markup
    )


@router.message(AddLesson.Evaluation, F.text, F.text.in_(['Зачёт🍎', 'Экзамен🍊', 'Зачёт с оценкой🍐']))
async def process_evaluation(message: Message, state: FSMContext):
    evaluation = message.text
    await state.update_data(evaluation=evaluation)

    await message.answer(
        text="<b>Введите номер аудитории:</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=cancel_markup
    )
    await state.set_state(AddLesson.Classroom)


@router.message(AddLesson.Evaluation)
async def incorrect_process_evaluation(message: Message, state: FSMContext):
    await message.answer(
        text="<b>Выберите тип оценивания из меню ниже!</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=lesson_priority_markup
    )


@router.message(AddLesson.Classroom, F.text, F.text.len() < 20)
async def process_classroom(message: Message, state: FSMContext):
    classroom = message.text
    await state.update_data(classroom=classroom)
    data = await state.get_data()
    selected_day = data.get('day')
    time = data.get('time')
    subject = data.get('subject')
    teacher_name = data.get('teacher_name')
    lesson_type = data.get('lesson_type')
    evaluation = data.get('evaluation')
    classroom = data.get('classroom')
    selected_day = day_translation.get(selected_day)
    lesson_info = f"<b>Добавляемая пара✅</b>\n\n" \
                  f"<b>День:</b> {selected_day.capitalize()}\n" \
                  f"<b>Время:</b> {time}\n" \
                  f"<b>Предмет:</b> {subject}\n" \
                  f"<b>Преподаватель:</b> {teacher_name}\n" \
                  f"<b>Тип занятия:</b> {lesson_type}\n" \
                  f"<b>Оценивание:</b> {evaluation}\n" \
                  f"<b>Аудитория:</b> {classroom}"
    final_button = [
        [KeyboardButton(text="Добавить пару🐣"),
         KeyboardButton(text="Пропустить добавление♻️")]
    ]

    final_markup = ReplyKeyboardMarkup(keyboard=final_button, resize_keyboard=True, one_time_keyboard=True)

    await message.answer(
        text=lesson_info,
        parse_mode=ParseMode.HTML,
        reply_markup=final_markup
    )
    await state.set_state(AddLesson.Final)


@router.message(AddLesson.Classroom)
async def incorrect_process_classroom(message: Message, state: FSMContext):
    await message.answer(
        text="<b>Слишком длинное название аудитории!</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=cancel_markup
    )


@router.message(AddLesson.Final, F.text == 'Добавить пару🐣')
async def adding_to_database(message: Message, state: FSMContext):
    data = await state.get_data()
    week_parity = data.get('week_parity')
    week_parity = 1 if week_parity == 'odd_week' else 0

    selected_day = data.get('day')
    day_offset_base = {'monday': 1, 'tuesday': 2, 'wednesday': 3, 'thursday': 4, 'friday': 5, 'saturday': 6}
    day_offset = day_offset_base[selected_day]
    week_parity_id = (day_offset, week_parity)
    week = [(1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1)]
    week_parity_id = week.index(week_parity_id) + 1
    time = data.get('time')
    lesson_times = ['8:30 - 10:00', '10:10 - 11:40', '11:50 - 13:20', '13:30 - 15:00',
                    '15:10 - 16:40', '16:50 - 18:20', '18:30 - 20:00', '20:10 - 21:40']
    lesson_number_for_time = lesson_times.index(time) + 1
    subject = data.get('subject')
    teacher_name = data.get('teacher_name')

    lesson_type = data.get('lesson_type')
    lesson_type = 0 if lesson_type == 'Лекция✏️' else 1

    evaluation = data.get('evaluation')

    evaluation_mapping = {'Зачёт🍎': 0, 'Экзамен🍊': 1, 'Зачёт с оценкой🍐': 2}

    evaluation = evaluation_mapping.get(evaluation, None)

    classroom = data.get('classroom')
    user_id = message.from_user.id
    add_lesson_to_schedule(user_id, week_parity_id, teacher_name, subject, lesson_type,
                           evaluation, classroom, lesson_number_for_time)
    await select_week_day(user_id, message.chat.id, message.message_id, state, True, False, True)
