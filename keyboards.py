from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, KeyboardButton, InlineKeyboardButton

menu_buttons = [
    [KeyboardButton(text="Расписание🗓"),
     KeyboardButton(text="Мой аккаунт👤")],
    [KeyboardButton(text="FAQℹ️"),
     KeyboardButton(text="Настройки⚙️")]
]

menu_markup = ReplyKeyboardMarkup(keyboard=menu_buttons, resize_keyboard=True)

settings_button = [
    [KeyboardButton(text="Уведомления🔔"),
     KeyboardButton(text="Сохранение📂")],
    [KeyboardButton(text="Главное меню🔙")]
]

settings_markup = ReplyKeyboardMarkup(keyboard=settings_button, resize_keyboard=True)

savings_button = [
    [KeyboardButton(text="Загрузить расписание♻️")],
    [KeyboardButton(text="Экспорт в .txt📄"),
     KeyboardButton(text="Экспорт в .xlsx📂")],
    [KeyboardButton(text="Назад🔙")]
]

savings_markup = ReplyKeyboardMarkup(keyboard=savings_button, resize_keyboard=True)

schedule_buttons = [
    [KeyboardButton(text="На сегодня📖"),
     KeyboardButton(text="На завтра📚"),
     KeyboardButton(text="На неделю🗂")],
    [KeyboardButton(text="Редактировать✏️"),
     KeyboardButton(text="Ближайшая пара🔜")],
    [KeyboardButton(text="Статистика📊"),
     KeyboardButton(text="Очистить🗑")],
    [KeyboardButton(text="Главное меню🔙")]
]

schedule_markup = ReplyKeyboardMarkup(keyboard=schedule_buttons, resize_keyboard=True)


next_lesson_button = [
    [KeyboardButton(text="Текущая🌅"),
     KeyboardButton(text="Следующая➡️")],
    [KeyboardButton(text="Назад🔙")]
]

next_lesson_markup = ReplyKeyboardMarkup(keyboard=next_lesson_button, resize_keyboard=True)


days_buttons = [
    [InlineKeyboardButton(text="Понедельник", callback_data="monday")],
    [InlineKeyboardButton(text="Вторник", callback_data="tuesday")],
    [InlineKeyboardButton(text="Среда", callback_data="wednesday")],
    [InlineKeyboardButton(text="Четверг", callback_data="thursday")],
    [InlineKeyboardButton(text="Пятница", callback_data="friday")],
    [InlineKeyboardButton(text="Суббота", callback_data="saturday")],
    [InlineKeyboardButton(text="Назад🔙", callback_data="back")]
]

days_markup = InlineKeyboardMarkup(inline_keyboard=days_buttons, resize_keyboard=True)

week_buttons = [
    [InlineKeyboardButton(text="Текущая🍒", callback_data="this_week"),
     InlineKeyboardButton(text="Следующая🍇", callback_data="next_week")]
]

week_markup = InlineKeyboardMarkup(inline_keyboard=week_buttons, resize_keyboard=True)

back_button_this = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Назад🔙", callback_data="back_to_week_this")]], resize_keyboard=True)

back_button_next = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Назад🔙", callback_data="back_to_week_next")]], resize_keyboard=True)

yes_no_button = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Да✅", callback_data="yes"),
                     InlineKeyboardButton(text="Нет❌", callback_data="no")]
                     ], resize_keyboard=True)

clear_button = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Да✅", callback_data="yes_clear"),
                     InlineKeyboardButton(text="Нет❌", callback_data="no_clear")]
                     ], resize_keyboard=True)

parity_buttons = [
    [InlineKeyboardButton(text="Чётная🍉", callback_data="even_week"),
     InlineKeyboardButton(text="Нечётная🍍", callback_data="odd_week")]
]

parity_markup = InlineKeyboardMarkup(inline_keyboard=parity_buttons, resize_keyboard=True)

manage_markup = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Удалить пару🗑", callback_data="delete_pair"),
                      InlineKeyboardButton(text="Назад🔙", callback_data="back_to_manage_day")]]
)


lesson_type = [
    [KeyboardButton(text="Практика💻"),
     KeyboardButton(text="Лекция✏️")],
    [KeyboardButton(text="Пропустить добавление♻️")]
]

lesson_type_markup = ReplyKeyboardMarkup(keyboard=lesson_type, resize_keyboard=True, one_time_keyboard=True)


lesson_priority_buttons = [
    [KeyboardButton(text="Зачёт🍎"),
     KeyboardButton(text="Экзамен🍊"),
     KeyboardButton(text="Зачёт с оценкой🍐")],
    [KeyboardButton(text="Пропустить добавление♻️")]
]

lesson_priority_markup = ReplyKeyboardMarkup(keyboard=lesson_priority_buttons,
                                             resize_keyboard=True, one_time_keyboard=True)

cancel_button = [
    [KeyboardButton(text="Пропустить добавление♻️")]
]

cancel_markup = ReplyKeyboardMarkup(keyboard=cancel_button, resize_keyboard=True, one_time_keyboard=True)
