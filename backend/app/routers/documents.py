from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import Document, DocumentChunk
from app.schemas import DocumentUploadResponse
from app.services.chunk import chunk_text
from app.services.embed import embed_texts
from app.services.extract import extract_text

router = APIRouter(prefix="/documents", tags=["documents"])

MAX_BYTES = settings.max_upload_mb * 1024 * 1024


@router.post("", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> DocumentUploadResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")
    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max {settings.max_upload_mb} MB",
        )
    try:
        text = await extract_text(file.filename, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    chunks = chunk_text(text)
    if not chunks:
        raise HTTPException(status_code=400, detail="No extractable text in document")
    doc = Document(filename=file.filename)
    db.add(doc)
    await db.flush()
    doc_id: UUID = doc.id
    batch_size = 64
    all_embeddings: list[list[float]] = []
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        vecs = await embed_texts(batch)
        all_embeddings.extend(vecs)
    for idx, (content, emb) in enumerate(zip(chunks, all_embeddings, strict=True)):
        db.add(
            DocumentChunk(
                document_id=doc_id,
                chunk_index=idx,
                content=content,
                embedding=emb,
            )
        )
    await db.commit()
    await db.refresh(doc)
    return DocumentUploadResponse(
        id=str(doc.id),
        filename=doc.filename,
        chunk_count=len(chunks),
    )
