import io
import pandas as pd
from PyPDF2 import PdfReader

def parse_pdf(file_bytes: bytes) -> str:
    """Читает байты PDF-файла и извлекает из него текст."""
    pdf = PdfReader(io.BytesIO(file_bytes))
    text = []
    for page in pdf.pages:
        text.append(page.extract_text())
    return "\n".join(text)

def parse_excel(file_bytes: bytes) -> str:
    """Читает байты Excel-файла и преобразует его содержимое в текст."""
    xls = pd.ExcelFile(io.BytesIO(file_bytes))
    text = []
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        text.append(df.to_string())
    return "\n\n".join(text)