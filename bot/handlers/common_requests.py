from aiogram import F, Router
from aiogram.types import Message

from services.db import Database
from services.gigachat import safe_ask_gigachat
from . import start, default_schedule, ask_schedule

router = Router()

COMMON_QUERIES = [
    "Расписание на сегодня",
    "Расписание на завтра",
    "Какой следующий урок?",
]

@router.message(F.text.in_(COMMON_QUERIES))
async def handle_common_queries(message: Message, db: Database):
    await ask_schedule.handle_question(message, db)