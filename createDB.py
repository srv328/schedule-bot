import sqlite3
from config import path, sql_path


def execute_query(query_path):
    with open(query_path, 'r', encoding='utf-8') as file:
        queries = file.read().split(';')

    connection = sqlite3.connect(path)
    cursor = connection.cursor()

    try:
        for query in queries:
            if query.strip():
                cursor.execute(query)
        connection.commit()
    finally:
        connection.close()


if __name__ == "__main__":
    execute_query(sql_path)
