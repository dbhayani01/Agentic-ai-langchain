from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.services.repository import ChatRepository

router = APIRouter(prefix="/chat", tags=["chat"])


def get_chat_service(db: AsyncSession = Depends(get_db_session)) -> ChatService:
    return ChatService(ChatRepository(db))


@router.post("", response_model=ChatResponse, summary="Send a chat message to support agent")
async def chat(payload: ChatRequest, service: ChatService = Depends(get_chat_service)) -> ChatResponse:
    try:
        response = await service.handle_chat(payload.session_id, payload.message)
        return ChatResponse(session_id=payload.session_id, response=response)
    except Exception as exc:  # broad to map AI/provider errors into API-safe response
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {exc}") from exc


@router.post("/stream", summary="Stream support assistant response")
async def chat_stream(payload: ChatRequest, service: ChatService = Depends(get_chat_service)) -> StreamingResponse:
    async def event_stream():
        try:
            async for chunk in service.stream_chat(payload.session_id, payload.message):
                yield chunk
        except Exception as exc:
            yield f"\n[ERROR] {exc}"

    return StreamingResponse(event_stream(), media_type="text/plain")
