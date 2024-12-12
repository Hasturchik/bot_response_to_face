import random
import re
import string
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import aiohttp
from telebot.async_telebot import AsyncTeleBot
import cv2
import os
import asyncio
import uuid
from replicate import Client
bot_username = None
from constants import TEMP_DIR, bot, ADMINS_ID, PROMPT

from work_with_image import apply_filter, delete_temp_files

# Папка для сохранения временных файлов
os.makedirs(TEMP_DIR, exist_ok=True)

user_data = {}


@bot.message_handler(commands=['admin'])
async def start_message(message):
    if str(message.from_user.id) not in ADMINS_ID:
        await bot.send_message(message.from_user.id, 'Ты не админ')
        return
    await bot.send_message(message.chat.id, '/set_prompt для изменения промпта')


@bot.message_handler(commands=['set_prompt'])
async def set_prompt(message):
    if str(message.from_user.id) not in ADMINS_ID:
        return

        # Запрашиваем новый текст для PROMPT
    await bot.send_message(message.chat.id, "Введите новый текст для фильтра:")

    # Ожидаем следующего сообщения с текстом
    @bot.message_handler(func=lambda msg: msg.chat.id == message.chat.id)
    async def update_prompt(msg):
        global PROMPT  # Обновляем глобальную переменную
        PROMPT = msg.text
        await bot.send_message(msg.chat.id, f"Новый текст для фильтра установлен: {PROMPT}")
        # Убираем обработчик, чтобы не было повторных реакций
        bot.message_handler(func=lambda msg: msg.chat.id == message.chat.id)


# Обработчик команды /start
@bot.message_handler(commands=['start'])
async def start_message(message):


    await bot.send_message(
        message.chat.id,
        "Привет! Отправь мне своё фото, и я создам стикеры с твоим лицом!\n\n"
    )





# Обработчик фотографий
@bot.message_handler(content_types=['photo'])
async def handle_photo(message):
    if message.chat.type != 'private':
        await bot.send_message(message.chat.id, 'Эта команда доступна только в личных сообщениях.')
        return

    unique_id = str(uuid.uuid4())  # Уникальный идентификатор для каждого запроса
    try:
        # Скачиваем фото пользователя
        file_id = message.photo[-1].file_id
        file_info = await bot.get_file(file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        user_photo_path = os.path.join(TEMP_DIR, f"user_{message.chat.id}_{unique_id}.jpg")

        with open(user_photo_path, "wb") as file:
            file.write(downloaded_file)

        await bot.send_message(message.chat.id, "Фото получено! Начинаю обработку...")


        result = await apply_filter(user_photo_path, PROMPT)



        # Удаление временных файлов
        await delete_temp_files(user_photo_path)

        await bot.send_message(
            message.chat.id,
            result
        )

        await bot.send_message(
            message.chat.id,
            "Можете отправить еще фото"
        )
    except Exception as e:
        await bot.send_message(message.chat.id, f"Произошла ошибка: {e}")



async def main():
    print(f'bot started')
    await bot.infinity_polling()

if __name__ == "__main__":
    asyncio.run(main())