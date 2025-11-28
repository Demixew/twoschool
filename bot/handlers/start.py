from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

router = Router()

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Расписание на сегодня")],
        [KeyboardButton(text="Расписание на завтра")],
        [KeyboardButton(text="Какой следующий урок?")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Спроси о расписании или выбери вариант"
)

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "🎒 Привет! Я — <b>Школьный Гид</b>.\n\n"
        "Я могу работать с твоим личным расписанием — просто пришли мне файл в формате PDF, Excel или <b>ICS</b>.\n\n"
        "Или сразу <b>начинай задавать вопросы</b> — я буду отвечать по демонстрационному расписанию.",
        reply_markup=main_keyboard
    )