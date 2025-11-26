import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command

# BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Отправляет сообщение, когда пользователь вводит команду /start."""
    await message.answer("Привет я твой школьный помощник для расписания")

async def main():
    """Запускает бота."""
    print("Бот запущен...")
    # Запускаем polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
