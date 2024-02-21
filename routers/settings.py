from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from contextlib import suppress
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest
from work_with_db import (
    get_current_notifications_status, update_notifications, update_notifications_status,
    get_current_notifications, get_schedule_statistics, has_backup, create_backup, has_schedule,
    get_time_from_backup_schedule, delete_backup, load_schedule_from_backup
)
from keyboards import (
    settings_markup, savings_markup, backup_markup,
    create_text_button, create_keyboard_markup, confirm_backup
)
from utils import (
    export_schedule_to_txt, create_excel_schedule, bot,
    get_formatted_date, generate_schedule_statistics_message
)

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
    even_schedule, odd_schedule = get_schedule_statistics("schedule", user_id)
    await export_schedule_to_txt(message)


@router.message(F.text == "Экспорт в .xlsx📂")
async def xslx_schedule_sending(message: Message, state: FSMContext):
    await state.set_state(ReturnButton.return_to_settings)
    user_id = message.from_user.id
    even_schedule, odd_schedule = get_schedule_statistics("schedule", user_id)
    await create_excel_schedule(message)


@router.message(F.text == "Загрузить расписание♻️")
async def backup_schedule(message: Message, state: FSMContext):
    await state.set_state(ReturnButton.return_to_settings)
    user_id = message.from_user.id
    if not has_schedule(user_id) and not has_backup(user_id):
        await message.answer("У вас пока что нет расписания\n"
                             "<b>Вам нечего сохранять!</b>",
                             parse_mode=ParseMode.HTML)
        return
    if not has_backup(user_id):
        await message.answer("У вас пока что нет сохранённых бэкапов.\n"
                             "Хотите <b>сохранить текущее состояние</b>?",
                             parse_mode=ParseMode.HTML,
                             reply_markup=backup_markup)
    else:
        time_from_schedule = get_time_from_backup_schedule(user_id)

        button = create_keyboard_markup([[create_text_button(time_from_schedule, "backup")],
                                         [create_text_button("Обновить бэкап♻", "update")]], True)

        await bot.send_message(message.chat.id,
                               text="<b>У вас есть сохранённый бэкап:</b>",
                               parse_mode=ParseMode.HTML,
                               reply_markup=button)


@router.callback_query(lambda query: query.data == 'yes_save')
async def save_to_backup(query: CallbackQuery, state: FSMContext):
    await state.set_state(ReturnButton.return_to_settings)
    user_id = query.from_user.id

    time = get_formatted_date()
    create_backup(user_id, time)
    time_from_schedule = get_time_from_backup_schedule(user_id)
    button = create_keyboard_markup([[create_text_button(time_from_schedule, "backup")],
                                     [create_text_button("Обновить бэкап♻", "update")]], True)

    await bot.delete_message(query.message.chat.id, query.message.message_id)
    await bot.send_message(query.message.chat.id,
                           text="<b>Бэкап был успешно сохранён!🎉</b>",
                           parse_mode=ParseMode.HTML)

    await bot.send_message(query.message.chat.id,
                           text="<b>У вас есть сохранённый бэкап:</b>",
                           parse_mode=ParseMode.HTML,
                           reply_markup=button)


@router.callback_query(lambda query: query.data == 'no_save')
async def skip_action(query: CallbackQuery, state: FSMContext):
    await state.set_state(ReturnButton.return_to_settings)
    user_id = query.from_user.id
    await bot.delete_message(query.message.chat.id, query.message.message_id)
    await query.message.answer(text="<b>Действие отменено</b>♻",
                               parse_mode=ParseMode.HTML)


@router.callback_query(lambda query: query.data == 'update')
async def update_backup(query: CallbackQuery, state: FSMContext):
    await state.set_state(ReturnButton.return_to_settings)
    user_id = query.from_user.id
    if not has_schedule(user_id):
        await query.message.answer("<b>У вас пустое расписание!</b> Я не дам вам испортить бэкап!",
                                   parse_mode=ParseMode.HTML)
        return
    delete_backup(user_id)
    time = get_formatted_date()

    create_backup(user_id, time)

    time_from_schedule = get_time_from_backup_schedule(user_id)

    button = create_keyboard_markup([[create_text_button(time_from_schedule, "backup")],
                                     [create_text_button("Обновить бэкап♻", "update")]], True)

    await bot.delete_message(query.message.chat.id, query.message.message_id)
    await bot.send_message(query.message.chat.id,
                           text="<b>Бэкап был успешно обновлён!🎉</b>",
                           parse_mode=ParseMode.HTML)

    await bot.send_message(query.message.chat.id,
                           text="<b>У вас есть сохранённый бэкап:</b>",
                           parse_mode=ParseMode.HTML,
                           reply_markup=button)


@router.callback_query(lambda query: query.data == 'backup')
async def load_from_backup(query: CallbackQuery, state: FSMContext):
    await state.set_state(ReturnButton.return_to_settings)
    user_id = query.from_user.id

    even_schedule, odd_schedule = get_schedule_statistics("backup_schedule", user_id)
    statistics_message = generate_schedule_statistics_message(even_schedule, odd_schedule)
    statistics_message = statistics_message.replace('Статистика <b>вашего</b> расписания 📊:',
                                                    'Статистика <b>вашего бекапа</b> 📊:', -1)
    await query.message.answer(text=statistics_message+"\nХотите <b>загрузить</b> данное расписание?",
                               parse_mode=ParseMode.HTML,
                               reply_markup=confirm_backup)


@router.callback_query(lambda query: query.data == 'no_backup')
async def skip_backup(query: CallbackQuery, state: FSMContext):
    await state.set_state(ReturnButton.return_to_settings)
    user_id = query.from_user.id
    await bot.delete_message(query.message.chat.id, query.message.message_id)
    await query.message.answer(text="<b>Действие отменено</b>♻",
                               parse_mode=ParseMode.HTML)
    time_from_schedule = get_time_from_backup_schedule(user_id)
    button = create_keyboard_markup([[create_text_button(time_from_schedule, "backup")],
                                     [create_text_button("Обновить бэкап♻", "update")]], True)
    await bot.send_message(query.message.chat.id,
                           text="<b>У вас есть сохранённый бэкап:</b>",
                           parse_mode=ParseMode.HTML,
                           reply_markup=button)


@router.callback_query(lambda query: query.data == 'yes_backup')
async def add_backup(query: CallbackQuery, state: FSMContext):
    await state.set_state(ReturnButton.return_to_settings)
    user_id = query.from_user.id
    await bot.delete_message(query.message.chat.id, query.message.message_id)

    load_schedule_from_backup(user_id)

    await bot.send_message(user_id, text="<b>Бэкап успешно загружен!🔄</b>",
                           parse_mode=ParseMode.HTML)
