from os import path
from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from config import admins, database_path, log_path
from utils import get_formatted_date
from aiogram.enums.parse_mode import ParseMode
from keyboards import admin_actions
from aiogram.exceptions import TelegramBadRequest

router = Router()


@router.message(F.text == "Админ панель💀")
async def admin_panel(message: Message):
    if str(message.from_user.id) not in admins:
        gif = FSInputFile("media/admin.mp4")
        await message.answer('<b>Куда мы лезем?</b>', parse_mode=ParseMode.HTML)
        await message.answer_video(gif)
        return
    await message.answer("<b>Что делать то будем?</b>", parse_mode=ParseMode.HTML, reply_markup=admin_actions)


@router.message(F.text == "Начать рассылку📖")
async def start_sending(message: Message):
    if str(message.from_user.id) not in admins:
        gif = FSInputFile("media/admin.mp4")
        await message.answer('<b>Куда мы лезем?</b>', parse_mode=ParseMode.HTML)
        await message.answer_video(gif)
        return
    pass


@router.message(F.text == "Выгрузить БД🗄")
async def export_database(message: Message):
    if str(message.from_user.id) not in admins:
        gif = FSInputFile("media/admin.mp4")
        await message.answer('<b>Куда мы лезем?</b>', parse_mode=ParseMode.HTML)
        await message.answer_video(gif)
        return
    if path.exists(database_path):
        try:
            db = FSInputFile(database_path, f"db_{get_formatted_date()}.db")
            await message.answer_document(db)
        except TelegramBadRequest:
            await message.answer("<b>БД пустая!</b>", parse_mode=ParseMode.HTML)
    else:
        await message.answer("<b>Не удалось выгрузить БД!</b>", parse_mode=ParseMode.HTML)


@router.message(F.text == "Выгрузить лог🗒")
async def export_database(message: Message):
    if str(message.from_user.id) not in admins:
        gif = FSInputFile("media/admin.mp4")
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

