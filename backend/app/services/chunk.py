from app.config import settings


def chunk_text(text: str) -> list[str]:
    text = text.strip()
    if not text:
        return []
    size = settings.chunk_size
    overlap = settings.chunk_overlap
    if overlap >= size:
        overlap = max(0, size // 4)
    chunks: list[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + size, n)
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= n:
            break
        start = end - overlap
    return chunks
