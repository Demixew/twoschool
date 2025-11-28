FROM python:3.10-slim

WORKDIR /app

# Устанавливаем системные зависимости для OCR:
# tesseract-ocr - сам движок
# tesseract-ocr-rus - русский языковой пакет для Tesseract
# poppler-utils - утилита для работы с PDF, нужна для pdf2image
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-rus \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]