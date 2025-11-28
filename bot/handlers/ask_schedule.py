# bot/handlers/ask_schedule.py
from aiogram import Router, F
from aiogram.types import Message
from services.db import get_schedule
from services.gigachat import safe_ask_gigachat

router = Router()

@router.message(F.text)
async def handle_question(message: Message):
    schedule = await get_schedule(message.chat.id)
    if not schedule:
        schedule = (
            "Понедельник: 1. Математика (каб. 101), 2. Русский язык (каб. 202), 3. История (каб. 303)\n"
            "Вторник: 1. Физика (каб. 105), 2. Литература (каб. 202), 3. Английский язык (каб. 305)"
        )

    answer = await safe_ask_gigachat(schedule, message.text)
    await message.answer(answer)