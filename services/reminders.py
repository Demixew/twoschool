from aiogram import Bot
from .db import Database
from .gigachat import get_tomorrow_summary
import logging
from bot.handlers import default_schedule

async def send_daily_reminders(bot: Bot, db: Database):
    logging.info("Начинаю рассылку ежедневных напоминаний...")
    chat_ids = await db.get_all_chat_ids()
    for chat_id in chat_ids:
        schedule = await db.get_schedule(chat_id)
        if not schedule:
            schedule = default_schedule.text
        
        try:
            summary = await get_tomorrow_summary(schedule)
            await bot.send_message(chat_id, f"👋 Привет! Небольшая сводка на завтра:\n\n{summary}")
        except Exception as e:
            logging.error(f"Не удалось отправить напоминание пользователю {chat_id}: {e}")
    logging.info("Рассылка завершена.")