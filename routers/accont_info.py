from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from work_with_db import get_registration_date
from aiogram.enums.parse_mode import ParseMode

router = Router()


def generate_share_keyboard():
    return [[InlineKeyboardButton(
        text='Поделиться расписанием',
        switch_inline_query=f'Расписание')]]


async def send_user_info(message: Message, user_id, full_name, registration_date):
    inline_markup = InlineKeyboardMarkup(inline_keyboard=generate_share_keyboard())

    await message.answer(
        f"<b>Информация об аккаунте:</b>\n"
        f"<b>🆔:</b> <code>{user_id}</code>\n"
        f"<b>Имя:</b> <i>{full_name}</i>\n"
        f"<b>Дата регистрации</b>: {registration_date}\n"
        f"<b>Ваша персональная ссылка: 🔗</b> "
        f"<a href='https://t.me/FEFUDVFU_bot?start={user_id}'>ссылка</a>\n"
        f"Воспользуйтесь ей, чтобы <b>поделиться своим расписанием!</b>",
        reply_markup=inline_markup,
        parse_mode=ParseMode.HTML
    )


@router.message(F.text == "Мой аккаунт👤")
async def userinfo(message: Message):
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    registration_date = get_registration_date(user_id)

    await send_user_info(message, user_id, full_name, registration_date)
