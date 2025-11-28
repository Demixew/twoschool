import os
import tempfile
from aiogram import Router, F
from aiogram.types import Message, Document
from aiogram.utils.chat_action import ChatActionSender

from services.db import Database
from services.parser import parse_pdf, parse_excel, parse_ics, parse_image, parse_pdf_with_ocr
from .start import main_keyboard

router = Router()

@router.message(F.document)
async def handle_document(message: Message, db: Database):
    if not message.document:
        return

    document = message.document
    if not document.mime_type:
        await message.answer("Не удалось определить тип файла.")
        return

    if document.mime_type == "application/pdf":
        parser = parse_pdf
        is_async_parser = False
    elif document.mime_type in (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel"
    ):
        parser = parse_excel
        is_async_parser = False
    elif document.mime_type == "text/calendar":
        parser = parse_ics
        is_async_parser = False
    elif document.mime_type.startswith("image/"):
        parser = parse_image
        is_async_parser = True
    else:
        await message.answer("Поддерживаются только PDF, Excel, ICS и файлы изображений (JPG, PNG).")
        return

    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        file = await message.bot.get_file(document.file_id)
        if not file.file_path:
            await message.answer("Не удалось получить информацию о файле.")
            return

        file_bytes = await message.bot.download_file(file.file_path)
        file_content = file_bytes.read()

        try:
            if is_async_parser:
                text = await parser(file_content)
            else:
                text = parser(file_content)
        except Exception as e:
            await message.answer(f"Ошибка при чтении файла: {str(e)}")
            return

        # Если это PDF и текст не извлекся, пробуем OCR
        if document.mime_type == "application/pdf" and not text.strip():
            await message.answer("В PDF не найден текстовый слой. Пробую распознать как изображение (это может занять время)...")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                temp_pdf.write(file_content)
                temp_pdf_path = temp_pdf.name
            
            text = await parse_pdf_with_ocr(temp_pdf_path)
            os.remove(temp_pdf_path)

        if not text.strip():
            await message.answer("Не удалось извлечь текст из файла. Он может быть пустым или поврежденным.")
            return

        await db.save_schedule(message.chat.id, text)
        await message.answer(
            "✅ Расписание сохранено! Теперь я готов отвечать на твои вопросы.",
            reply_markup=main_keyboard
        )