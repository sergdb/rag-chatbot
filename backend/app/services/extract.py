from io import BytesIO

from docx import Document as DocxDocument
from pypdf import PdfReader


async def extract_text(filename: str, data: bytes) -> str:
    lower = filename.lower()
    if lower.endswith(".txt"):
        return data.decode("utf-8", errors="replace")
    if lower.endswith(".pdf"):
        reader = PdfReader(BytesIO(data))
        parts: list[str] = []
        for page in reader.pages:
            t = page.extract_text() or ""
            parts.append(t)
        return "\n\n".join(parts).strip()
    if lower.endswith(".docx"):
        doc = DocxDocument(BytesIO(data))
        return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip()).strip()
    raise ValueError("Unsupported file type. Use .txt, .pdf, or .docx")
