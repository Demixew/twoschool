import logging
from datetime import datetime, timedelta
from aiogram import Router
from aiogram.types import Message, BufferedInputFile
from aiogram.filters import Command
from ics import Calendar, Event
from services.db import Database
from services.gigachat import get_schedule_from_text


async def create_schedule_ics_file(db: Database, user_id: int) -> bytes | None:
    """
    Создает содержимое .ics файла из расписания пользователя в базе данных.
    """
    schedule_text = await db.get_schedule(user_id)
    if not schedule_text:
        return None

    schedule_data = await get_schedule_from_text(schedule_text)
    if not schedule_data:
        return None

    cal = Calendar()
    # Устанавливаем начальную дату на 23 ноября 2024 года (ближайший понедельник)
    start_date = datetime(2025, 11, 25) # Monday

    days_map = {"понедельник": 0, "вторник": 1, "среда": 2, "четверг": 3, "пятница": 4, "суббота": 5, "воскресенье": 6}

    for day_name_ru, lessons in schedule_data.items():
        day_name = day_name_ru.lower()
        if day_name not in days_map:
            continue

        day_offset = days_map[day_name]
        lesson_date = start_date + timedelta(days=day_offset)

        for lesson in lessons:
            try:
                start_time_dt = datetime.strptime(lesson['start_time'], '%H:%M').time()
                end_time_dt = datetime.strptime(lesson['end_time'], '%H:%M').time()

                event_start = datetime.combine(lesson_date, start_time_dt)
                event_end = datetime.combine(lesson_date, end_time_dt)

                event = Event()
                event.name = lesson['subject']
                event.begin = event_start
                event.end = event_end
                event.location = lesson.get('cabinet', 'Н/У')
                cal.events.add(event)
            except (ValueError, TypeError, KeyError) as e:
                logging.warning(f"Не удалось создать событие для урока: {lesson}. Ошибка: {e}")
                continue

    return str(cal).encode('utf-8')

async def cmd_export(message: Message, db: Database):
    ics_content = await create_schedule_ics_file(db, message.chat.id)
    if ics_content:
        file = BufferedInputFile(ics_content, filename="schedule.ics")
        await message.answer_document(file, caption="🗓️ Ваше текущее расписание в формате .ics. Можете добавить его в свой календарь!")
    else:
        await message.answer("У вас еще нет сохраненного расписания. Отправьте мне файл, чтобы я его запомнил.")

def get_export_router():
    router = Router()
    router.message.register(cmd_export, Command("export"))
    return router