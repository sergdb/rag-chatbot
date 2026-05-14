from fastapi import APIRouter, Depends, HTTPException

from app.memory_store import MemoryDocumentStore, get_store
from app.schemas import ChatRequest, ChatResponse
from app.services.rag import chat_with_context, retrieve_context

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    store: MemoryDocumentStore = Depends(get_store),
) -> ChatResponse:
    doc = await store.get(body.document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if not body.messages:
        raise HTTPException(status_code=400, detail="messages must not be empty")
    last = body.messages[-1]
    if last.role != "user":
        raise HTTPException(status_code=400, detail="Last message must be from user")
    question = last.content.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Empty question")
    context = await retrieve_context(store, body.document_id, question)
    if not context.strip():
        raise HTTPException(
            status_code=400,
            detail="No indexed content for this document. Try uploading again.",
        )
    msgs = [{"role": m.role, "content": m.content} for m in body.messages]
    reply = await chat_with_context(context, msgs)
    return ChatResponse(reply=reply)
