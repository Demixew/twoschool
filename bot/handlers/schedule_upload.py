# bot/handlers/schedule_upload.py
from aiogram import Router, F
from aiogram.types import Message, Document
from aiogram.utils.chat_action import ChatActionSender
import io

from services.db import save_schedule
from services.parser import parse_pdf, parse_excel

router = Router()

@router.message(F.document)
async def handle_document(message: Message):
    document = message.document
    if not document.mime_type:
        await message.answer("Не удалось определить тип файла.")
        return

    if document.mime_type == "application/pdf":
        parser = parse_pdf
    elif document.mime_type in (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel"
    ):
        parser = parse_excel
    else:
        await message.answer("Поддерживаются только PDF и Excel-файлы.")
        return

    async with ChatActionSender.upload_document(bot=message.bot, chat_id=message.chat.id):
        file = await message.bot.get_file(document.file_id)
        file_bytes = await message.bot.download_file(file.file_path)
        try:
            text = parser(file_bytes.read())
        except Exception as e:
            await message.answer(f"Ошибка при чтении файла: {str(e)}")
            return

        if not text.strip():
            await message.answer("Файл пустой или не содержит текста.")
            return

        await save_schedule(message.chat.id, text)
        await message.answer(
            "✅ Расписание сохранено!\nТеперь можешь спрашивать:\n"
            "— «Когда следующий урок?»\n"
            "— «Где биология?»\n"
            "— «Какие завтра контрольные?»"
        )