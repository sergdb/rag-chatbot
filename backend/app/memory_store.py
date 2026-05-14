import asyncio
import math
import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class StoredChunk:
    content: str
    embedding: tuple[float, ...]


@dataclass
class StoredDocument:
    id: uuid.UUID
    filename: str
    chunks: list[StoredChunk]


def _cosine_similarity(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    if len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na <= 0.0 or nb <= 0.0:
        return 0.0
    return dot / (na * nb)


class MemoryDocumentStore:
    """Process-local store. Cleared when the API process restarts."""

    def __init__(self) -> None:
        self._docs: dict[uuid.UUID, StoredDocument] = {}
        self._lock = asyncio.Lock()

    async def add_document(
        self,
        filename: str,
        chunk_texts: list[str],
        embeddings: list[list[float]],
    ) -> uuid.UUID:
        if len(chunk_texts) != len(embeddings):
            raise ValueError("chunk_texts and embeddings length mismatch")
        async with self._lock:
            doc_id = uuid.uuid4()
            chunks = [
                StoredChunk(text, tuple(float(x) for x in emb))
                for text, emb in zip(chunk_texts, embeddings, strict=True)
            ]
            self._docs[doc_id] = StoredDocument(id=doc_id, filename=filename, chunks=chunks)
            return doc_id

    async def get(self, doc_id: uuid.UUID) -> StoredDocument | None:
        async with self._lock:
            return self._docs.get(doc_id)

    async def top_k_contents(
        self,
        document_id: uuid.UUID,
        query_embedding: list[float],
        k: int,
    ) -> list[str]:
        q = tuple(float(x) for x in query_embedding)
        async with self._lock:
            doc = self._docs.get(document_id)
            if not doc or not doc.chunks:
                return []
            rows = [(c.content, c.embedding) for c in doc.chunks]
        scored = [(_cosine_similarity(q, emb), content) for content, emb in rows]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [content for _, content in scored[:k]]


_store = MemoryDocumentStore()


def get_store() -> MemoryDocumentStore:
    return _store
