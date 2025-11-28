from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from services.db import Database
from services.gigachat import get_tomorrow_summary
from . import start, default_schedule

router = Router()

@router.message(Command("tomorrow"))
async def cmd_tomorrow(message: Message, db: Database):
    schedule = await db.get_schedule(message.chat.id)
    if not schedule:
        schedule = default_schedule.text

    summary = await get_tomorrow_summary(schedule)
    await message.answer(f"🔮 Заглянем в завтрашний день...\n\n{summary}", reply_markup=start.main_keyboard)