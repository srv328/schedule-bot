from aiogram import Router
from config import admins
from keyboards import menu_markup, yes_no_button, admin_markup
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.enums.parse_mode import ParseMode
from work_with_db import check_user_exists, add_user_to_database, has_schedule, copy_schedule
from utils import extract_unique_code, bot
from aiogram.fsm.state import State
from aiogram.fsm.state import StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import types


class Share(StatesGroup):
    ans = State()


router = Router()


async def start_command(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    user_exists = check_user_exists(user_id)
    if user_exists is None or not user_exists:
        add_user_to_database(user_id, message.from_user.full_name)

    unique_code = extract_unique_code(message.text)
    if unique_code:
        return await handle_unique_code(message, state, int(unique_code))

    if str(message.from_user.id) in admins:
        await message.answer(f"<b>{message.from_user.full_name}, добро пожаловать в ФЕФУ расписание!</b>",
                             reply_markup=admin_markup, parse_mode=ParseMode.HTML)
    else:
        await message.answer(f"<b>{message.from_user.full_name}, добро пожаловать в ФЕФУ расписание!</b>",
                             reply_markup=menu_markup, parse_mode=ParseMode.HTML)


async def handle_unique_code(message: Message, state: FSMContext, unique_code: int):
    referred_user_exists = check_user_exists(unique_code)
    user_id = message.from_user.id
    if str(user_id) in admins:
        markup = admin_markup
    else:
        markup = menu_markup
    if user_id == unique_code:
        await message.answer("<b>Нельзя скопировать расписание самому себе!</b>", reply_markup=markup,
                             parse_mode=ParseMode.HTML)
        return

    if not referred_user_exists:
        await message.answer("<b>Расписание по данной ссылке не найдено!</b>", reply_markup=markup,
                             parse_mode=ParseMode.HTML)
        return

    if not has_schedule(unique_code):
        await message.answer(f"В этой ссылке пустое расписание🗓\nЛучше его не копировать :)\n"
                             f"Если вы хотите очистить расписание, сделайте это через меню бота.☑️",
                             reply_markup=markup,
                             parse_mode=ParseMode.HTML)
        return
    await state.set_state(Share.ans)
    await state.update_data(ans=unique_code)
    await message.answer(f"Ты уверен, что хочешь <b>скопировать</b> расписание человека с 🆔 {unique_code}?\n"
                         f"ВНИМАНИЕ❗️\n"
                         f"Это действие <b>обновит ваше расписание!</b>\n"
                         f"Его <b>нельзя</b> будет <b>отменить</b>⚠️\n"
                         f"Перед переходом по ссылке <b>настоятельно рекомендуется</b> сохранить ваше текущее "
                         f"расписание в <b>настройках</b>",
                         reply_markup=yes_no_button,
                         parse_mode=ParseMode.HTML)


@router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext):
    await start_command(message, state)


@router.callback_query(lambda query: query.data == 'yes', Share.ans)
async def process_share_yes(query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    referer = user_data.get('ans')
    await state.clear()
    copy_schedule(int(referer), int(query.from_user.id))
    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    if str(query.from_user.id) in admins:
        markup = admin_markup
    else:
        markup = menu_markup
    await query.message.answer(text="<b>Расписание успешно скопировано!</b>",
                               parse_mode=ParseMode.HTML,
                               reply_markup=markup)


@router.callback_query(lambda query: query.data == 'no', Share.ans)
async def process_share_no(query: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    if str(query.from_user.id) in admins:
        markup = admin_markup
    else:
        markup = menu_markup
    await query.message.answer(text="<b>Действие отменено</b>♻",
                               parse_mode=ParseMode.HTML,
                               reply_markup=markup)
