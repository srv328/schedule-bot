from aiogram.filters import Command
from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from config import admins
from utils import bot
from aiogram.enums.parse_mode import ParseMode
from keyboards import clear_button, schedule_markup
from work_with_db import has_schedule, execute_query

router = Router()


@router.message(F.text == "Админ панель💀")
async def admin_panel(message: Message):
    if str(message.from_user.id) not in admins:
        gif = FSInputFile("media/admin.mp4")
        await message.answer('<b>Куда мы лезем?</b>', parse_mode=ParseMode.HTML)
        await message.answer_video(gif)
        return
    await message.answer("<b>Что делать то будем?</b>", parse_mode=ParseMode.HTML)
