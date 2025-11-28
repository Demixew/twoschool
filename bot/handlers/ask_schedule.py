from aiogram import Router, F
from aiogram.types import Message
from services.db import Database
from services.gigachat import safe_ask_gigachat, is_schedule_update_statement, Messages
from . import start, default_schedule
from collections import defaultdict
from .common_requests import COMMON_QUERIES

router = Router()

# Хранилище для истории диалогов (chat_id -> list[Messages])
conversation_history = defaultdict(list)   
MAX_HISTORY_LEN = 20 

@router.message(F.text, ~F.text.in_(COMMON_QUERIES))
async def handle_question(message: Message, db: Database):
    user_text = message.text
    chat_id = message.chat.id

    if await is_schedule_update_statement(user_text):
        await db.add_temporary_change(chat_id, user_text)
        await message.answer(f"✅ Понял! Запомнил это изменение на сегодня: \"{user_text}\"")
        return

    schedule = await db.get_schedule(chat_id)
    if not schedule:
        schedule = default_schedule.text
    
    temp_changes = await db.get_temporary_changes_for_today(chat_id)
    if temp_changes:
        changes_text = "\n".join(f"- {change}" for change in temp_changes)
        schedule = f"ВАЖНЫЕ ВРЕМЕННЫЕ ИЗМЕНЕНИЯ НА СЕГОДНЯ:\n{changes_text}\n\nОСНОВНОЕ РАСПИСАНИЕ:\n{schedule}"

    history = conversation_history[chat_id]
    answer = await safe_ask_gigachat(schedule, user_text, history)

    history.append(Messages(role="user", content=user_text))
    history.append(Messages(role="assistant", content=answer))
    conversation_history[chat_id] = history[-MAX_HISTORY_LEN:]

    await message.answer(answer, reply_markup=start.main_keyboard)