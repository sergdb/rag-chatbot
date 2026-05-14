from uuid import UUID

from openai import AsyncOpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import DocumentChunk
from app.services.embed import get_openai_client


async def retrieve_context(session: AsyncSession, document_id: UUID, question: str) -> str:
    qvec = await embed_query(question)
    stmt = (
        select(DocumentChunk.content)
        .where(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.embedding.cosine_distance(qvec))
        .limit(settings.rag_top_k)
    )
    rows = (await session.execute(stmt)).scalars().all()
    if not rows:
        return ""
    parts = [f"[excerpt {i + 1}]\n{c}" for i, c in enumerate(rows)]
    return "\n\n".join(parts)


async def chat_with_context(
    context: str,
    messages: list[dict[str, str]],
) -> str:
    client: AsyncOpenAI = get_openai_client()
    system = (
        "You are a helpful assistant. Answer using only the provided document excerpts. "
        "If the excerpts do not contain the answer, say you cannot find it in the document."
    )
    if context:
        system += f"\n\nDocument excerpts:\n{context}"
    openai_messages = [{"role": "system", "content": system}]
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")
        if role not in ("user", "assistant"):
            continue
        openai_messages.append({"role": role, "content": content})
    resp = await client.chat.completions.create(
        model=settings.openai_chat_model,
        messages=openai_messages,
        temperature=0.2,
    )
    choice = resp.choices[0]
    return (choice.message.content or "").strip()
