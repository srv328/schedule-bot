from aiogram import Router
from aiogram.types import InlineQueryResultArticle, InlineQuery, InputTextMessageContent
from aiogram.enums.parse_mode import ParseMode
from work_with_db import get_schedule_statistics
from utils import generate_schedule_statistics_message

router = Router()


@router.inline_query(lambda query: query.query.startswith(''))
async def default(query: InlineQuery):
    user_id = query.from_user.id

    even_schedule, odd_schedule = get_schedule_statistics("schedule", user_id)
    replacements = (
        (f'Статистика <b>вашего</b> расписания 📊:', ''),
        ('В ДВФУ вы проведёте', 'В ДВФУ я проведу'),
    )

    ref_mes = generate_schedule_statistics_message(even_schedule, odd_schedule)

    if ref_mes != 'У вас пока нет занятий в расписании.':
        base_message = f"<b>Моя статистика расписания</b>📊:{ref_mes}" \
                       f"\n<b>Переходи в бота</b> и планируй свою учёбу с комфортом! " \
                       f"<a href='https://t.me/FEFUDVFU_bot'>тык</a>"
    else:
        base_message = f"У меня пока что нет статистики!📊\n<b>Нужно добавить пары!</b>\n" \
                       f"Переходи в бота и планируй свою учёбу с комфортом! <a href='https://t.me/FEFUDVFU_bot'>тык</a>"

    for old, new in replacements:
        base_message = base_message.replace(old, new)

    schedule_result = [
        InlineQueryResultArticle(
            id='1',
            title="Поделиться ссылкой на бота",
            description="Нажмите, чтобы поделиться ссылкой",
            input_message_content=InputTextMessageContent(
                message_text=f"Настрой своё расписание в несколько кликов! "
                             f"<a href='https://t.me/FEFUDVFU_bot'>@FEFUDVFU_bot</a>",
                parse_mode=ParseMode.HTML
            ),
            thumb_url="https://sun1-83.userapi.com/s/v1/ig2/GAG4M-nEEH2uw43iclrQMZNG-_8vRfm23f_Ol5Tv-xerA8bTF94BMIXTVhB"
                      "km41UV2Fpo3iUN2Jh6hljOEPWl7VR.jpg?size=100x100&quality=95&crop=0,0,1080,1080&ava=1"
        ),
        InlineQueryResultArticle(
            id='2',
            title="Поделиться расписанием",
            description="Нажмите, чтобы отправить ваше расписание",
            input_message_content=InputTextMessageContent(
                message_text=f"Используй моё расписание: <a href='https://t.me/FEFUDVFU_bot?start={user_id}'>тык</a>",
                parse_mode=ParseMode.HTML
            ),
            thumb_url="https://e7.pngegg.com/pngimages/529/122/png-clipart-computer-icons-calendar-"
                      "date-google-calendar-calendar-icon-purple-violet.png"
        ),
        InlineQueryResultArticle(
            id='3',
            title="Поделиться статистикой",
            description="Нажмите, чтобы отправить вашу статистику",
            input_message_content=InputTextMessageContent(
                    message_text=base_message,
                    parse_mode=ParseMode.HTML
                ),
            thumb_url="https://ladys-room.ru/wp-content/uploads/2022/09/086bcbc460826f25e9de443db73fc4c0-429x425.png"
        )
    ]

    await query.answer(schedule_result, cache_time=10, is_personal=True)
