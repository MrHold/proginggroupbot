# setup_db.py
import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Конфигурация подключения к PostgreSQL как суперпользователь
SUPERUSER = os.getenv('SUPERUSER')
SUPERUSER_PASSWORD = os.getenv('SUPERUSER_PASSWORD')
HOST = os.getenv('DB_HOST', 'localhost')
PORT = os.getenv('DB_PORT', '5432')
connection = None

# Данные для новой базы данных и пользователя
NEW_DB_NAME = os.getenv('DB_NAME', 'telegram_bot_db')
NEW_DB_USER = os.getenv('DB_USER', 'telegram_user')
NEW_DB_PASSWORD = os.getenv('DB_PASSWORD', 'your_password')

def create_database_and_user():
    try:
        # Подключение к базе данных 'postgres' как суперпользователь
        connection = psycopg2.connect(
            dbname='postgres',
            user=SUPERUSER,
            password=SUPERUSER_PASSWORD,
            host=HOST,
            port=PORT
        )
        connection.autocommit = True  # Необходимо для создания базы данных и пользователя
        cursor = connection.cursor()

        # Создание пользователя
        cursor.execute(
            sql.SQL("SELECT 1 FROM pg_roles WHERE rolname = %s"),
            [NEW_DB_USER]
        )
        if cursor.fetchone():
            print(f"Пользователь '{NEW_DB_USER}' уже существует.")
        else:
            cursor.execute(
                sql.SQL("CREATE USER {} WITH PASSWORD %s").format(sql.Identifier(NEW_DB_USER)),
                [NEW_DB_PASSWORD]
            )
            print(f"Пользователь '{NEW_DB_USER}' успешно создан.")

        # Создание базы данных
        cursor.execute(
            sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"),
            [NEW_DB_NAME]
        )
        if cursor.fetchone():
            print(f"База данных '{NEW_DB_NAME}' уже существует.")
        else:
            cursor.execute(
                sql.SQL("CREATE DATABASE {} OWNER {}").format(
                    sql.Identifier(NEW_DB_NAME),
                    sql.Identifier(NEW_DB_USER)
                )
            )
            print(f"База данных '{NEW_DB_NAME}' успешно создана и принадлежит пользователю '{NEW_DB_USER}'.")

        # Предоставление всех привилегий пользователю на базу данных
        cursor.execute(
            sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(
                sql.Identifier(NEW_DB_NAME),
                sql.Identifier(NEW_DB_USER)
            )
        )
        print(f"Все привилегии на базу данных '{NEW_DB_NAME}' предоставлены пользователю '{NEW_DB_USER}'.")

    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == '__main__':
    create_database_and_user()
