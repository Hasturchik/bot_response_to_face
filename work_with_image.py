import base64
import io
import random
import re
import string
import replicate
import aiohttp
from openai import AsyncOpenAI
from telebot.async_telebot import AsyncTeleBot
import cv2
import os
from replicate import Client
bot_username = None
from constants import OPEN_AI_API_TOKEN, TEMP_DIR, bot
from PIL import Image

async def apply_filter(user_photo_path, prompt):
    """
    Отправка изображения с текстовым промптом в ChatGPT.
    """
    # Преобразование изображения в base64
    base64_image = await convert_image_to_base64(user_photo_path)

    # Подготовка сообщений для GPT
    messages = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": "Ты - ассистент, который анализирует полученные фото. ТЫ ДОЛЖЕН ОТВЕЧАТЬ НА КАЖДОЕ СООБЩЕНИЕ ПОЛЬЗОВАТЕЛЯ"
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {'type': 'image_url',
                 'image_url': {
                     'url': base64_image
                 }}
            ]
        }

    ]

    # Инициализация клиента OpenAI
    client = AsyncOpenAI(api_key=OPEN_AI_API_TOKEN)
    # Выполнение запроса
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    print(response.choices[0].message.content)
    return response.choices[0].message.content


async def delete_temp_files(*files):
    for file in files:
        if os.path.exists(file):
            os.remove(file)


async def convert_image_to_base64(image_path: str) -> str:
    """
    Конвертирует изображение в base64-encoded строку с правильным MIME-типом.

    :param image_path: Путь к изображению.
    :return: Base64-encoded строка с MIME-типом.
    """
    # Открываем изображение и определяем его формат
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
        image = Image.open(io.BytesIO(image_data))
        mime_type = f"image/{image.format.lower()}"

        # Кодируем изображение в base64
        encoded_image = base64.b64encode(image_data).decode("utf-8")

        # Возвращаем строку в формате base64 с MIME-типом
        return f"data:{mime_type};base64,{encoded_image}"