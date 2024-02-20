from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from contextlib import suppress
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest
from work_with_db import get_current_notifications_status, update_notifications, update_notifications_status, \
    get_current_notifications, get_schedule_statistics
from keyboards import settings_markup, savings_markup
from utils import export_schedule_to_txt, create_excel_schedule, bot

router = Router()


class ReturnButton(StatesGroup):
    return_to_settings = State()


@router.message(F.text == "Настройки⚙️")
async def settings_command(message: Message, state: FSMContext):
    await state.set_state(ReturnButton.return_to_settings)
    await message.answer(text="<b>Что будем настраивать?</b>",
                         reply_markup=settings_markup,
                         parse_mode=ParseMode.HTML)


@router.message(F.text == "Уведомления🔔")
async def set_notifications_command(message: Message, state: FSMContext):
    await state.set_state(ReturnButton.return_to_settings)
    notifications = generate_notifications_keyboard(message.from_user.id)
    await message.answer(text="За сколько минут до начала пары присылать уведомления:",
                         reply_markup=notifications)


@router.message(F.text == "Сохранение📂")
async def saving_command(message: Message, state: FSMContext):
    await state.set_state(ReturnButton.return_to_settings)
    await message.answer(text="<b>Используйте раздел меню ниже:</b>",
                         reply_markup=savings_markup,
                         parse_mode=ParseMode.HTML)


@router.message(F.text == "Назад🔙", ReturnButton.return_to_settings)
async def back_to_settings(message: Message):
    await message.answer(text="<b>Что будем настраивать?</b>",
                         reply_markup=settings_markup,
                         parse_mode=ParseMode.HTML)


def generate_notifications_keyboard(user_id):
    notifications_buttons = [
        [InlineKeyboardButton(text="-", callback_data="decrease_notifications"),
         InlineKeyboardButton(text=f"{get_current_notifications(user_id)} минут",
                              callback_data="current_notifications"),
         InlineKeyboardButton(text="+", callback_data="increase_notifications")],
        [InlineKeyboardButton(text=f'{get_current_notifications_status(user_id)}', callback_data="notifications",
                              parse_mode=ParseMode.HTML)]
    ]
    notifications = InlineKeyboardMarkup(inline_keyboard=notifications_buttons, resize_keyboard=True)
    return notifications


@router.callback_query(lambda query: query.data == 'notifications')
async def process_notifications_status_callback(query: CallbackQuery):
    user_id = query.from_user.id
    current_status = get_current_notifications_status(user_id)
    new_status = 1 if current_status == "Уведомления: *выключены*🔕" else 0
    update_notifications_status(user_id, new_status)

    status_message = f"Вы успешно {'включили' if new_status else 'выключили'} " \
                     f"уведомления о парах {'🔔' if new_status else '🔕'}"
    await bot.answer_callback_query(query.id, text=status_message)

    with suppress(TelegramBadRequest):
        await bot.edit_message_text(
            chat_id=user_id,
            message_id=query.message.message_id,
            text="За сколько минут до начала пары присылать уведомления:",
            reply_markup=generate_notifications_keyboard(user_id)
        )


@router.callback_query(lambda query: query.data.startswith(('increase_notifications', 'decrease_notifications')))
async def process_notifications_callback(query: CallbackQuery):
    user_id = query.from_user.id
    current_notifications = get_current_notifications(user_id)
    new_notifications = 0

    if query.data == 'increase_notifications' and current_notifications < 60:
        new_notifications = min(current_notifications + 5, 60)
    elif query.data == 'decrease_notifications' and current_notifications > 5:
        new_notifications = max(current_notifications - 5, 5)
    else:
        limit_message = "Нельзя увеличить время уведомлений свыше 60 минут⚠️"\
            if query.data == 'increase_notifications' else "Нельзя уменьшить время уведомлений меньше 5 минут⚠️"
        await query.answer(limit_message, show_alert=True)
        return

    update_notifications(user_id, new_notifications)

    with suppress(TelegramBadRequest):
        await bot.edit_message_text(
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            text="За сколько минут до начала пары присылать уведомления:",
            reply_markup=generate_notifications_keyboard(user_id)
        )


@router.message(F.text == "Экспорт в .txt📄")
async def txt_schedule_sending(message: Message, state: FSMContext):
    await state.set_state(ReturnButton.return_to_settings)
    user_id = message.from_user.id
    even_schedule, odd_schedule = get_schedule_statistics(user_id)
    await export_schedule_to_txt(message)


@router.message(F.text == "Экспорт в .xlsx📂")
async def xslx_schedule_sending(message: Message, state: FSMContext):
    await state.set_state(ReturnButton.return_to_settings)
    user_id = message.from_user.id
    even_schedule, odd_schedule = get_schedule_statistics(user_id)
    await create_excel_schedule(message)
