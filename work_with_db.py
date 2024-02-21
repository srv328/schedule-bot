import sqlite3
import pytz
from datetime import datetime
from config import database_path


def add_lesson_to_schedule(user_id, week_parity_id, tutor_name, subject_name, is_practice,
                           subject_priority, subject_place, lesson_time_id):
    query = """
        INSERT INTO schedule (user_id, week_parity_id, tutor_name, subject_name, is_practice,
                              subject_priority, subject_place, lesson_time_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    execute_query(query, user_id, week_parity_id, tutor_name, subject_name, is_practice,
                  subject_priority, subject_place, lesson_time_id)


def get_existing_lessons(user_id, day, week_parity):
    query = """
        SELECT lesson_times.start_time, lesson_times.end_time
        FROM schedule
        INNER JOIN week_parity ON schedule.week_parity_id = week_parity.week_parity_id
        INNER JOIN lesson_times ON schedule.lesson_time_id = lesson_times.lesson_time_id
        WHERE schedule.user_id = ? 
            AND week_parity.is_odd_week = ?
            AND week_parity.day_of_week = ?
        ORDER BY lesson_times.start_time
    """
    result = execute_query(query, user_id, week_parity, day)
    return [(row[0], row[1]) for row in result]


def execute_query(query, *params):
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    try:
        cursor.execute(query, params)
        result = cursor.fetchall()
        connection.commit()
        return result
    finally:
        connection.close()


def get_lesson_by_params_with_user(user_id, subject_number, selected_day, week_parity):
    query = """
        SELECT schedule.*, lesson_times.start_time, lesson_times.end_time, lesson_times.lesson_time_id
        FROM schedule
        INNER JOIN week_parity ON schedule.week_parity_id = week_parity.week_parity_id
        INNER JOIN lesson_times ON schedule.lesson_time_id = lesson_times.lesson_time_id
        WHERE schedule.user_id = ? 
            AND schedule.lesson_time_id = ?
            AND week_parity.is_odd_week = ?
            AND week_parity.day_of_week = ?
        ORDER BY week_parity.is_odd_week, lesson_times.lesson_time_id
    """
    return execute_query(query, user_id, subject_number, week_parity, selected_day)


def delete_lesson_by_params(user_id, subject_number, selected_day, week_parity):
    query = """
        DELETE FROM schedule
        WHERE user_id = ? 
            AND lesson_time_id = ?
            AND week_parity_id IN (SELECT week_parity_id FROM week_parity WHERE is_odd_week = ? AND day_of_week = ?)
    """
    execute_query(query, user_id, subject_number, week_parity, selected_day)


def copy_schedule(referer_user_id, referred_user_id):
    delete_query = "DELETE FROM schedule WHERE user_id = ?"
    execute_query(delete_query, referred_user_id)

    select_query = "SELECT * FROM schedule WHERE user_id = ?"
    rows_to_copy = execute_query(select_query, referer_user_id)

    insert_query = "INSERT INTO schedule (user_id, week_parity_id, tutor_name, subject_name, is_practice, " \
                   "subject_priority, subject_place, lesson_time_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"

    for row in rows_to_copy:
        execute_query(insert_query, referred_user_id, row[1], row[2], row[3], row[4], row[5], row[6], row[7])


def get_total_users():
    query = "SELECT COUNT(*) FROM users"
    return execute_query(query)[0][0]


def check_user_exists(user_id):
    query = "SELECT COUNT(*) FROM users WHERE user_id = ?"
    return execute_query(query, user_id)[0][0] > 0


def add_user_to_database(user_id, username):
    local_timezone = pytz.timezone('Asia/Vladivostok')  # UTC+10
    current_time_local = datetime.now(local_timezone)

    query = "INSERT INTO users (user_id, username, registration_date) VALUES (?, ?, ?)"
    execute_query(query, user_id, username, current_time_local)


def get_user_value_by_id(user_id, column_name):
    query = f"SELECT {column_name} FROM users WHERE user_id = ?"
    result = execute_query(query, user_id)
    return result[0][0] if result else None


def get_current_notifications(user_id):
    return get_user_value_by_id(user_id, "minutes_before") or 10


def get_current_notifications_status(user_id):
    notifications_enabled = get_user_value_by_id(user_id, "notifications")
    return "Уведомления: *включены*🔔" if notifications_enabled else "Уведомления: *выключены*🔕" \
        if notifications_enabled is not None else "Данные о уведомлениях не найдены"


def update_user_status(user_id, column_name, new_status):
    query = f"UPDATE users SET {column_name} = ? WHERE user_id = ?"
    execute_query(query, new_status, user_id)


def update_notifications_status(user_id, new_status):
    update_user_status(user_id, "notifications", new_status)


def update_notifications(user_id, new_notifications):
    update_user_status(user_id, "minutes_before", new_notifications)


def get_schedule_by_day_offset(user_id, day_offset, week_parity):
    query = """
        SELECT schedule.*, lesson_times.start_time, lesson_times.end_time, lesson_times.lesson_time_id
            FROM schedule
            INNER JOIN week_parity ON schedule.week_parity_id = week_parity.week_parity_id
            INNER JOIN lesson_times ON schedule.lesson_time_id = lesson_times.lesson_time_id
            WHERE schedule.user_id = ? 
                AND week_parity.is_odd_week = ? 
                AND week_parity.day_of_week = ?
            ORDER BY week_parity.is_odd_week, lesson_times.lesson_time_id
    """
    return execute_query(query, user_id, week_parity, day_offset)


def has_schedule(user_id):
    query = "SELECT COUNT(*) FROM schedule WHERE user_id = ?"
    return execute_query(query, user_id)[0][0] > 0


def get_schedule_statistics(user_id):
    query = """
        SELECT
            week_parity.day_of_week,
            COUNT(*) as num,
            CASE
                WHEN week_parity.is_odd_week = 0 THEN 'even'
                WHEN week_parity.is_odd_week = 1 THEN 'odd'
            END AS week_type
        FROM
            schedule
            INNER JOIN week_parity ON schedule.week_parity_id = week_parity.week_parity_id
        WHERE
            schedule.user_id = ?
        GROUP BY
            week_parity.day_of_week, week_type
    """
    result = execute_query(query, user_id)

    even_schedule = {day: count for day, count, week_type in result if week_type == 'even'}
    odd_schedule = {day: count for day, count, week_type in result if week_type == 'odd'}

    return even_schedule, odd_schedule


def get_registration_date(user_id):
    query = "SELECT registration_date FROM users WHERE user_id = ?"
    result = execute_query(query, user_id)
    formatted_date = None
    if result:
        result = result[0][0].split(' ')[0]
        parsed_date = datetime.strptime(result, "%Y-%m-%d")
        formatted_date = parsed_date.strftime("%d.%m.%Y")
    else:
        result = "Нет данных о регистрации"

    return formatted_date if formatted_date else result
