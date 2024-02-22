from aiogram import Router, F
from aiogram.types import Message
from aiogram.enums.parse_mode import ParseMode
from config import admins
from work_with_db import get_total_users
from keyboards import menu_markup, admin_markup

router = Router()


async def send_bot_info(message: Message):
    creation_date = "<b>Дата создания бота:</b> <i>1 марта 2024 года</i>🎉"
    total_users = f"<b>Всего пользователей:</b> {get_total_users()}📊"
    problems = "<b>Возник вопрос или нашли баг/ошибку❓</b>\n<b>Есть предложения по улучшению❓</b>"
    contact_me = "<b>Напишите мне❕</b> <a href='https://t.me/shevelev_rv'>👉🏻 тык</a>"
    overheard_channel = "<b>Подслушка ДВФУ:</b> <a href='https://t.me/overheardfefu'>👂 тык</a>"
    map_link = "<b>Потерялся в D корпусе?</b> <a href='https://map.dvfu.ru'>🗺 тык</a>"
    voluntary_note = "<i>Бот был создан для студентов ДВФУ на добровольных началах</i>"
    if str(message.from_user.id) in admins:
        markup = admin_markup
    else:
        markup = menu_markup
    await message.answer(
        f"{creation_date}\n"
        f"{total_users}\n"
        f"{problems}\n"
        f"{contact_me}\n"
        f"{overheard_channel}\n"
        f"{map_link}\n"
        f"{voluntary_note}",
        reply_markup=markup,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )


@router.message(F.text == "FAQℹ️")
async def bot_info(message: Message):
    await send_bot_info(message)
