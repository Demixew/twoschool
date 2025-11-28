from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "🎒 Привет! Я — <b>Школьный Гид</b>.\n\n"
        "Пришли мне расписание в виде PDF или Excel-файла.\n"
        "После этого можешь спрашивать обо всём: уроках, кабинетах, заменах.\n\n"
        "Я говорю только правду — и никогда не выдумываю."
    )