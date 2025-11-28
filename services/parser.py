import io
import asyncio
import pandas as pd
import pytesseract
from PyPDF2 import PdfReader
from ics import Calendar
from PIL import Image
from pdf2image import convert_from_path


async def _run_blocking_ocr(image: Image) -> str:
    """Асинхронная обертка для блокирующей функции pytesseract."""
    loop = asyncio.get_running_loop()
    # Запускаем блокирующую операцию в отдельном потоке, чтобы не мешать работе бота
    text = await loop.run_in_executor(
        None, lambda: pytesseract.image_to_string(image, lang='rus+eng')
    )
    return text


def parse_pdf(file_bytes: bytes) -> str:
    """
    Читает байты PDF-файла и извлекает из него текст.
    Сначала пытается извлечь текстовый слой. Если его нет, использует OCR.
    """
    pdf_file = io.BytesIO(file_bytes)
    pdf = PdfReader(pdf_file)
    text = []
    for page in pdf.pages:
        extracted = page.extract_text()
        if extracted:
            text.append(extracted)
    
    full_text = "\n".join(text).strip()

    # Если PyPDF2 не нашел текст (например, это скан), используем OCR
    if not full_text:
        # pdf2image работает с путями, поэтому нужно сохранить файл временно
        # Но мы можем передать байты напрямую, если используем poppler-cpp
        # Для простоты и совместимости, здесь предполагается, что pdf2image может работать с байтами
        # или требует путь. В асинхронном контексте лучше избегать временных файлов.
        # Однако, pdf2image.convert_from_bytes существует, но может быть менее стабильной.
        # Для надежности, хендлер должен будет сохранить файл и передать путь.
        # Здесь мы оставим заглушку, а логику реализуем в хендлере.
        return "" # Возвращаем пустую строку, сигнализируя о необходимости OCR

    return full_text

def parse_excel(file_bytes: bytes) -> str:
    """Читает байты Excel-файла и преобразует его содержимое в текст."""
    xls = pd.ExcelFile(io.BytesIO(file_bytes))
    text = []
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        text.append(df.to_string())
    return "\n\n".join(text)

def parse_ics(file_bytes: bytes) -> str:
    """Читает байты .ics файла и преобразует события в текстовое расписание."""
    try:
        calendar_str = file_bytes.decode('utf-8')
    except UnicodeDecodeError:
        raise ValueError("Не удалось прочитать файл. Пожалуйста, убедитесь, что он в кодировке UTF-8.")
    cal = Calendar(calendar_str)

    events = sorted(list(cal.events), key=lambda e: e.begin)
    if not events:
        return "В календаре нет событий."

    text_lines = []
    current_day = None

    for event in events:
        event_day = event.begin.strftime("%A, %d %B")
        if event_day != current_day:
            current_day = event_day
            text_lines.append(f"\n--- {current_day} ---")
        
        location = f" (Место: {event.location})" if event.location else ""
        text_lines.append(
            f"- {event.name} ({event.begin.strftime('%H:%M')} - {event.end.strftime('%H:%M')}){location}"
        )
    
    return "\n".join(text_lines)

async def parse_image(file_bytes: bytes) -> str:
    """Читает байты изображения и распознает на нем текст с помощью OCR."""
    try:
        image = Image.open(io.BytesIO(file_bytes))
        return await _run_blocking_ocr(image)
    except Exception:
        return ""

async def parse_pdf_with_ocr(pdf_path: str) -> str:
    """
    Принудительно использует OCR для распознавания текста в PDF-файле по его пути.
    """
    loop = asyncio.get_running_loop()
    # pdf2image - блокирующая операция
    images = await loop.run_in_executor(
        None, lambda: convert_from_path(pdf_path)
    )

    tasks = [_run_blocking_ocr(image) for image in images]
    texts = await asyncio.gather(*tasks)
    
    return "\n\n".join(texts)