# main.py
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User
import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Настройка SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создание таблиц (если они еще не созданы)
Base.metadata.create_all(bind=engine)

# Функция для форматирования имени пользователя с кликабельной ссылкой
def format_user_link(user: User) -> str:
    # Формируем полное имя
    full_name = user.first_name
    if user.last_name:
        full_name += f" {user.last_name}"
    
    if user.username:
        # Если есть username, используем ссылку на профиль
        link = f"https://t.me/{user.username}"
    else:
        # Если нет username, используем схему tg://user?id=USER_ID
        link = f"tg://user?id={user.user_id}"
    
    # Возвращаем Markdown-ссылку
    return f"[{full_name}]({link})"

# Хэндлер на команду /start
@dp.message(Command(commands=["start"]))
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я бот для управления вариантами. Используй /help для списка команд.")
    # Добавление пользователя в базу данных, если его еще нет
    session = SessionLocal()
    user = session.query(User).filter(User.user_id == message.from_user.id).first()
    if not user:
        new_user = User(
            user_id=message.from_user.id,
            first_name=message.from_user.first_name,  # Может быть None
            last_name=message.from_user.last_name,    # Может быть None
            username=message.from_user.username,      # Может быть None
            variant_number=0                           # Дефолтное значение
        )

        session.add(new_user)
        session.commit()
        await message.reply("Вы успешно зарегистрированы!")
    else:
        await message.reply("Вы уже зарегистрированы.")
    session.close()

# Хэндлер на команду /help
@dp.message(Command(commands=["help"]))
async def help_command(message: types.Message):
    help_text = (
        "/change_variant - Изменить номер вашего варианта.\n"
        "/list_all - Показать всех участников.\n"
        "/list_my_variant - Показать участников вашего варианта."
    )
    await message.reply(help_text)

# Команда для изменения номера варианта
@dp.message(Command(commands=["change_variant"]))
async def change_variant(message: types.Message, command: Command):
    args = command.args
    if not args:
        await message.reply("Пожалуйста, укажите номер варианта. Пример: /change_variant 2")
        return
    try:
        var_num = int(args)
        if var_num < 1 or var_num > 30:
            raise ValueError
        new_variant = var_num
    except ValueError:
        await message.reply("Неверный формат номера варианта. Пожалуйста, укажите целое число от 1 до 30.")
        return

    session = SessionLocal()
    user = session.query(User).filter(User.user_id == message.from_user.id).first()
    if user:
        user.variant_number = new_variant
        session.commit()
        await message.reply(f"Ваш номер варианта успешно изменен на {new_variant}.")
    else:
        # Создание нового пользователя, если пользователя нет в базе
        new_user = User(
            user_id=message.from_user.id,
            first_name=message.from_user.first_name,  # Может быть None
            last_name=message.from_user.last_name,    # Может быть None
            username=message.from_user.username,      # Может быть None
            variant_number=new_variant
        )

        session.add(new_user)
        session.commit()
        await message.reply(f"Ваш номер варианта установлен на {new_variant}.")
    session.close()

# Команда для вывода всех участников
@dp.message(Command(commands=["list_all"]))
async def list_all(message: types.Message):
    session = SessionLocal()
    users = session.query(User).all()
    if not users:
        await message.reply("Список участников пуст.")
        session.close()
        return

    response = "Список всех участников:\n"
    for user in users:
        user_link = format_user_link(user)
        response += f"{user_link}, Вариант: {user.variant_number}\n"
    
    await message.reply(response, parse_mode=types.ParseMode.MARKDOWN, disable_notification=True)
    session.close()

# Команда для вывода участников своего варианта
@dp.message(Command(commands=["list_my_variant"]))
async def list_my_variant(message: types.Message):
    session = SessionLocal()
    user = session.query(User).filter(User.user_id == message.from_user.id).first()
    if not user:
        await message.reply("Вы не зарегистрированы в системе. Используйте /start для регистрации.")
        session.close()
        return

    variant = user.variant_number
    users = session.query(User).filter(User.variant_number == variant).all()
    if not users:
        await message.reply(f"Нет участников с вариантом {variant}.")
        session.close()
        return

    response = f"Участники вашего варианта ({variant}):\n"
    for u in users:
        user_link = format_user_link(u)
        response += f"{user_link}\n"
    
    await message.reply(response, parse_mode=types.ParseMode.MARKDOWN, disable_notification=True)
    session.close()

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
