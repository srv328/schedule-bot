from os import path
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, FSInputFile, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import admins, database_path, log_path
from utils.utilities import get_formatted_date
from aiogram.enums.parse_mode import ParseMode
from utils.keyboards import admin_actions, sender, yes_no_button
from aiogram.exceptions import TelegramBadRequest
from aiogram import Router
from utils.bot_entity import Bot
from utils.work_with_db import check_table_exists, create_table_if_not_exists, delete_campaign_table

router = Router()


class SenderAction(StatesGroup):
    getTableName = State()
    getMessage = State()
    q_button = State()
    get_text_button = State()
    get_url_button = State()
    confirm = State()
    decide = State()


@router.message(F.text == "Админ панель💀")
async def admin_panel(message: Message):
    if str(message.from_user.id) not in admins:
        gif = FSInputFile("media/админ.mp4")
        await message.answer('<b>Куда мы лезем?</b>', parse_mode=ParseMode.HTML)
        await message.answer_video(gif)
        return
    await message.answer("<b>Что делать то будем?</b>", parse_mode=ParseMode.HTML, reply_markup=admin_actions)


@router.message(F.text == "Начать рассылку📖")
async def start_sending(message: Message, state: FSMContext):
    if str(message.from_user.id) not in admins:
        gif = FSInputFile("media/админ.mp4")
        await message.answer('<b>Куда мы лезем?</b>', parse_mode=ParseMode.HTML)
        await message.answer_video(gif)
        return
    await state.clear()
    await state.set_state(SenderAction.getTableName)
    await message.answer("Введите название рассылки:")


@router.message(SenderAction.getTableName, F.text)
async def create_table(message: Message, state: FSMContext):
    await state.set_state(SenderAction.getMessage)
    table_name = message.text
    await state.update_data(table_name=table_name)
    if await check_table_exists(table_name):
        await message.answer(f"Таблица '{table_name}' уже существует. Продолжаем.")
    else:
        await message.answer(f"Таблицы '{table_name}' не существует. Создаем новую.")
        await create_table_if_not_exists(table_name)
    await message.answer("Отправьте рекламное сообщение, которое будет использовано в рассылке:")


@router.message(SenderAction.getMessage)
async def get_message(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(message_chat_id=message.chat.id)
    await state.update_data(message_id=message.message_id)
    await state.set_state(SenderAction.q_button)
    await message.answer('Кнопку добавлять будем?', reply_markup=sender)


@router.callback_query(lambda query: query.data == 'yes_sender', SenderAction.q_button)
async def handle_yes_button(query: CallbackQuery, state: FSMContext):
    await state.set_state(SenderAction.get_text_button)
    await query.message.answer("Введите текст для кнопки:")


@router.message(SenderAction.get_text_button)
async def get_text_button(message: Message, state: FSMContext):
    await state.set_state(SenderAction.get_url_button)
    text = message.text
    await state.update_data(text_button=text)
    await message.answer("Введите URL для кнопки:")


@router.message(SenderAction.get_url_button)
async def get_url_button(message: Message, state: FSMContext):
    await state.set_state(SenderAction.confirm)
    text = message.text
    await state.update_data(url=text)
    await message.answer('Подтвердите рассылку:', reply_markup=yes_no_button)


@router.callback_query(lambda query: query.data == 'no_sender', SenderAction.q_button)
async def handle_no_button(query: CallbackQuery, state: FSMContext):
    await state.set_state(SenderAction.confirm)
    await query.message.answer("Рассылка будет продолжена без кнопки.")
    await query.message.answer('Подтвердите рассылку:', reply_markup=yes_no_button)


@router.callback_query(lambda query: query.data in ['yes', 'no'], SenderAction.confirm)
async def decide(query: CallbackQuery, state: FSMContext, bot: Bot):
    if query.data == 'yes':
        await state.set_state(SenderAction.confirm)
        await query.message.answer('Рассылка была запущена!')
    else:
        data = await state.get_data()
        table_name = data.get('table_name')
        if delete_campaign_table(table_name):
            await query.message.answer('Рассылка отменена. Кампания была удалена.')
        else:
            await query.message.answer('Не верю. Проверь код.')
    await state.clear()


@router.message(SenderAction.confirm)
async def confirm(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    table_name = data.get('table_name')
    url = data.get('url') if data.get('url') else None
    text_button = data.get('text_button') if data.get('text_button') else None
    message_chat_id = data.get('message_chat_id')
    message_id = data.get('message_id')
    but = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=text_button, url=url)]]) \
        if url and text_button else None
    await bot.copy_message(message_chat_id, message_chat_id, message_id, reply_markup=but)


@router.message(F.text == "Выгрузить БД🗄")
async def export_database(message: Message):
    if str(message.from_user.id) not in admins:
        gif = FSInputFile("media/админ.mp4")
        await message.answer('<b>Куда мы лезем?</b>', parse_mode=ParseMode.HTML)
        await message.answer_video(gif)
        return
    if path.exists(database_path):
        try:
            db = FSInputFile(database_path, f"db_{get_formatted_date()}.sqlite3")
            await message.answer_document(db)
        except TelegramBadRequest:
            await message.answer("<b>БД пустая!</b>", parse_mode=ParseMode.HTML)
    else:
        await message.answer("<b>Не удалось выгрузить БД!</b>", parse_mode=ParseMode.HTML)


@router.message(F.text == "Выгрузить лог🗒")
async def export_log(message: Message):
    if str(message.from_user.id) not in admins:
        gif = FSInputFile("media/админ.mp4")
        await message.answer('<b>Куда мы лезем?</b>', parse_mode=ParseMode.HTML)
        await message.answer_video(gif)
        return
    if path.exists(log_path):
        try:
            log = FSInputFile(log_path, f"log_{get_formatted_date()}.log")
            await message.answer_document(log)
        except TelegramBadRequest:
            await message.answer("<b>Лог пустой!</b>", parse_mode=ParseMode.HTML)
    else:
        await message.answer("<b>Не удалось выгрузить лог!</b>", parse_mode=ParseMode.HTML)
