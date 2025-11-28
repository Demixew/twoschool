import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from services.db import Database
from services.reminders import send_daily_reminders
from services.parser import parse_ics
from bot.handlers import default_schedule, get_handlers_router, get_export_router

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не найден в .env")

async def on_startup(bot: Bot, db: Database, scheduler: AsyncIOScheduler):
    try:
        with open("test_schedule.ics", "rb") as f:
            ics_bytes = f.read()
            default_schedule.text = parse_ics(ics_bytes)
            logging.info("✅ Демо-расписание загружено.")
    except FileNotFoundError:
        logging.error("❌ Файл test_schedule.ics не найден. Демо-режим не будет работать.")

    scheduler.add_job(send_daily_reminders, trigger='cron', hour=20, minute=0, kwargs={'bot': bot, 'db': db})
    scheduler.start()
    logging.info("✅ Планировщик задач запущен.")

    await bot.delete_webhook(drop_pending_updates=True)

async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")

    db = Database("school_guide.db")
    await db.init()

    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow") # Убедитесь, что часовой пояс верный
    dp = Dispatcher(db=db, scheduler=scheduler)

    dp.include_router(get_handlers_router())
    dp.include_router(get_export_router())
    dp.startup.register(on_startup)
    
    logging.info("🚀 Бот запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())