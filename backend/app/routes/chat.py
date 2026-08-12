from fastapi import APIRouter, Request
from pydantic import BaseModel, Field
import json
import os
from pathlib import Path

router = APIRouter()

def load_database(file_path) -> list:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

BASE = Path(__file__).parent.parent.parent
DB   = load_database(BASE / "data" / "gmu_resources.json")

class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=300,
        json_schema_extra={"example": "where do I get my transcript"}
    )

class ChatResponse(BaseModel):
    response:   str
    intent:     str | None = None
    confidence: float      = 0.0
    link:       str | None = None
    rag_used:   bool       = False

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    from backend.app.services.rag       import semantic_rag_response, is_rag_enabled
    from backend.app.services.analytics import PopularityTracker, log_query
    from backend.app.services.responder import format_help

    TRACKER = PopularityTracker(str(BASE / "data" / "analytics.json"))
    message = request.message.strip()

    if message.lower() in {"help", "?", "topics", "list"}:
        return ChatResponse(response=format_help(DB), intent="help", confidence=100.0)

    if message.lower() in {"stats", "analytics", "popular"}:
        return ChatResponse(response=TRACKER.format_report(), intent="stats", confidence=100.0)

    msg_lower = message.lower()
    if any(word in msg_lower for word in ["hi", "hello", "hey", "howdy"]):
        return ChatResponse(
            response="Hi there! 👋 I am the GMU Resource Assistant. Ask me anything about campus resources!",
            intent="greeting", confidence=100.0
        )

    if any(word in msg_lower for word in ["bye", "goodbye", "thanks", "thank you"]):
        return ChatResponse(
            response="Goodbye! Have a great day at Mason! 🎓",
            intent="goodbye", confidence=100.0
        )

    if is_rag_enabled():
        try:
            result = await semantic_rag_response(message, DB)
        except Exception as e:
            print(f"RAG error: {e}")
            result = {"response": None}

        if result.get("response"):
            TRACKER.record_hit(result.get("intent", "general"))
            log_query(message, result.get("intent"), result.get("confidence", 0))
            return ChatResponse(
                response   = result["response"],
                intent     = result.get("intent"),
                confidence = result.get("confidence", 0.0),
                link       = result.get("link"),
                rag_used   = True
            )

    log_query(message, None, 0.0)
    return ChatResponse(
        response="I am having trouble connecting right now. Please try again.",
        intent=None, confidence=0.0, link=None
    )