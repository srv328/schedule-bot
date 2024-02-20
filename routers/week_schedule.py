from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.enums.parse_mode import ParseMode
from work_with_db import get_schedule_by_day_offset
from utils import generate_schedule_response, get_week_parity, get_week_title, \
    get_days_of_week, day_translation_form, bot
from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest
from keyboards import week_markup, schedule_markup, menu_markup, days_markup, back_button_this, back_button_next

router = Router()


class WeekSelectionState(StatesGroup):
    week = State()


@router.message(F.text == "Главное меню🔙")
async def schedule(message: Message):
    await message.answer("Возвращаемся в главное меню♻️", reply_markup=menu_markup)


@router.message(F.text == "На неделю🗂")
async def show_week(message: Message, state: FSMContext):
    await message.answer(text="Выберите период 🔎", reply_markup=week_markup)
    await state.set_state(WeekSelectionState.week)


@router.message(F.text == "Расписание🗓")
async def schedule(message: Message):
    await message.answer("Воспользуйтесь кнопками меню ниже🔽", reply_markup=schedule_markup)


@router.callback_query(lambda query: query.data == 'back', WeekSelectionState.week)
async def return_to_back(query: CallbackQuery, state: FSMContext):
    with suppress(TelegramBadRequest):
        await bot.edit_message_text(
            text="Выберите период 🔎",
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            reply_markup=week_markup
        )
        await state.set_state(WeekSelectionState.week)


@router.callback_query(lambda query: query.data in ['back_to_week_this', 'back_to_week_next'])
async def back_to_week(query: CallbackQuery, state: FSMContext):
    current_week = 'this_week' if query.data == 'back_to_week_this' else 'next_week'
    week_title = get_week_title(current_week)

    with suppress(TelegramBadRequest):
        await bot.edit_message_text(
            text=week_title,
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            reply_markup=days_markup,
            parse_mode=ParseMode.HTML
        )
        await state.set_state(WeekSelectionState.week)
        await state.update_data(week=current_week)


@router.callback_query(lambda query: query.data in ['this_week', 'next_week'], WeekSelectionState.week)
async def schedule_callback(query: CallbackQuery, state: FSMContext):

    current_week = query.data
    week_title = get_week_title(current_week)
    await state.update_data(week=current_week)

    with suppress(TelegramBadRequest):
        await bot.edit_message_text(
            text=week_title,
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            reply_markup=days_markup,
            parse_mode=ParseMode.HTML
        )


@router.callback_query(lambda query: query.data in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'],
                       WeekSelectionState.week)
async def handle_day_button(query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    selected_week = user_data.get('week', 'this_week')
    selected_day = query.data

    day_offset_base = {'monday': 1, 'tuesday': 2, 'wednesday': 3, 'thursday': 4, 'friday': 5, 'saturday': 6}
    day_offset_shifted = {'monday': 8, 'tuesday': 9, 'wednesday': 10, 'thursday': 11, 'friday': 12, 'saturday': 13}
    day_offset = day_offset_base[selected_day] if selected_week == 'this_week' else day_offset_shifted[selected_day]

    week_parity = get_week_parity() if selected_week == 'this_week' else (get_week_parity() + 1) % 2
    user_id = query.from_user.id
    all_week_dates = get_days_of_week()

    selected_date = all_week_dates[day_offset - 1] if selected_week == 'this_week' else all_week_dates[day_offset - 2]
    week_schedule = get_schedule_by_day_offset(user_id, day_offset % 7, week_parity)
    response_text = generate_schedule_response(week_schedule, day_translation_form[selected_day] + '\n'
                                               + f"{selected_date[:-5]}")
    button = back_button_this if selected_week == 'this_week' else back_button_next

    if 'Пара' not in response_text:
        response_text += 'В этот день занятий нет!'

    await state.clear()
    with suppress(TelegramBadRequest):
        await bot.edit_message_text(text=response_text,
                                    chat_id=query.message.chat.id,
                                    message_id=query.message.message_id,
                                    parse_mode=ParseMode.HTML,
                                    reply_markup=button)
