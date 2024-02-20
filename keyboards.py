from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, KeyboardButton, InlineKeyboardButton


def create_keyboard_markup(buttons, is_inline=False, times=False):
    return InlineKeyboardMarkup(inline_keyboard=buttons) if is_inline else ReplyKeyboardMarkup(keyboard=buttons,
                                                                                               resize_keyboard=True,
                                                                                               one_time_keyboard=times)


def create_text_button(text, callback_data=None):
    return InlineKeyboardButton(text=text, callback_data=callback_data) if callback_data else KeyboardButton(text=text)


menu_buttons = [
    [create_text_button("Расписание🗓"),
     create_text_button("Мой аккаунт👤")],
    [create_text_button("FAQℹ️"),
     create_text_button("Настройки⚙️")]
]

menu_markup = create_keyboard_markup(menu_buttons)
admin_markup = create_keyboard_markup([[create_text_button("Админ панель💀")]] + menu_buttons)

settings_button = [
    [create_text_button("Уведомления🔔"),
     create_text_button("Сохранение📂")],
    [create_text_button("Главное меню🔙")]
]

settings_markup = create_keyboard_markup(settings_button)

savings_button = [
    [create_text_button("Загрузить расписание♻️")],
    [create_text_button("Экспорт в .txt📄"),
     create_text_button("Экспорт в .xlsx📂")],
    [create_text_button("Назад🔙")]
]

savings_markup = create_keyboard_markup(savings_button)

schedule_buttons = [
    [create_text_button("На сегодня📖"),
     create_text_button("На завтра📚"),
     create_text_button("На неделю🗂")],
    [create_text_button("Редактировать✏️"),
     create_text_button("Ближайшая пара🔜")],
    [create_text_button("Статистика📊"),
     create_text_button("Очистить🗑")],
    [create_text_button("Главное меню🔙")]
]

schedule_markup = create_keyboard_markup(schedule_buttons)


next_lesson_button = [
    [create_text_button("Текущая🌅"),
     create_text_button("Следующая➡️")],
    [create_text_button("Назад🔙")]
]

next_lesson_markup = create_keyboard_markup(next_lesson_button)


days_buttons = [
    [create_text_button("Понедельник", "monday")],
    [create_text_button("Вторник", "tuesday")],
    [create_text_button("Среда", "wednesday")],
    [create_text_button("Четверг", "thursday")],
    [create_text_button("Пятница", "friday")],
    [create_text_button("Суббота", "saturday")],
    [create_text_button("Назад🔙", "back")]
]

days_markup = create_keyboard_markup(days_buttons, True)

week_buttons = [
    [create_text_button("Текущая🍒", "this_week"),
     create_text_button("Следующая🍇", "next_week")]
]

week_markup = create_keyboard_markup(week_buttons, True)

back_button_this = create_keyboard_markup([[create_text_button("Назад🔙", "back_to_week_this")]], True)
back_button_next = create_keyboard_markup([[create_text_button("Назад🔙", "back_to_week_next")]], True)


yes_no_button = create_keyboard_markup([[create_text_button("Да✅", "yes"), create_text_button("Нет❌", "no")]], True)

clear_button = create_keyboard_markup([[create_text_button("Да✅", "yes_clear"),
                                        create_text_button("Нет❌", "no_clear")]], True)

parity_buttons = [[create_text_button("Чётная🍉", "even_week"), create_text_button("Нечётная🍍", "odd_week")]]

parity_markup = create_keyboard_markup(parity_buttons, True)

manage_markup = create_keyboard_markup([[create_text_button("Удалить пару🗑", "delete_pair"),
                                         create_text_button("Назад🔙", "back_to_manage_day")]], True)

lesson_type = [
    [create_text_button("Практика💻"), create_text_button("Лекция✏️")],
    [create_text_button("Пропустить добавление♻️")]
]

lesson_type_markup = create_keyboard_markup(lesson_type, False, True)


lesson_priority_buttons = [
    [create_text_button("Зачёт🍎"),
     create_text_button("Экзамен🍊"),
     create_text_button("Зачёт с оценкой🍐")],
    [create_text_button("Пропустить добавление♻️")]
]

lesson_priority_markup = create_keyboard_markup(lesson_priority_buttons, False, True)

cancel_button = [[create_text_button("Пропустить добавление♻️")]]

cancel_markup = create_keyboard_markup(cancel_button, False, True)
