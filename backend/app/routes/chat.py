import json
import logging
import re
from pathlib import Path

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.dependencies import get_current_user
from app.models import User
from app.services.analytics import PopularityTracker, log_query
from app.services.responder import format_help

logger = logging.getLogger(__name__)
router = APIRouter()

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

with open(DATA_DIR / "gmu_resources.json", encoding="utf-8") as f:
    RESOURCES = json.load(f)

tracker = PopularityTracker(str(DATA_DIR / "analytics.json"))

HELP_COMMANDS = {"help", "?", "topics", "list"}
STATS_COMMANDS = {"stats", "analytics", "popular"}
GREETINGS = {"hi", "hello", "hey", "howdy"}
GOODBYES = {"bye", "goodbye", "thanks", "thank", "thx"}

GREETING_REPLY = "Hi there. I'm the GMU Resource Assistant. Ask me anything about campus resources."
GOODBYE_REPLY = "Goodbye, and good luck this semester."
FALLBACK_REPLY = "I'm having trouble connecting right now. Please try again."


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=300,
        json_schema_extra={"example": "where do I get my transcript"},
    )


class ChatResponse(BaseModel):
    response: str
    intent: str | None = None
    confidence: float = 0.0
    link: str | None = None
    rag_used: bool = False


def is_small_talk(words, vocab):
    # short messages only, so "hi, where's the registrar" still reaches RAG
    return len(words) <= 3 and bool(words & vocab)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, user: User = Depends(get_current_user)):
    # deferred so the embedding model loads on the first question, not at server start
    from app.services.rag import is_rag_enabled, semantic_rag_response

    message = request.message.strip()
    lowered = message.lower()
    words = set(re.findall(r"[a-z']+", lowered))

    if lowered in HELP_COMMANDS:
        return ChatResponse(response=format_help(RESOURCES), intent="help", confidence=100.0)

    if lowered in STATS_COMMANDS:
        return ChatResponse(response=tracker.format_report(), intent="stats", confidence=100.0)

    if is_small_talk(words, GREETINGS):
        return ChatResponse(response=GREETING_REPLY, intent="greeting", confidence=100.0)

    if is_small_talk(words, GOODBYES):
        return ChatResponse(response=GOODBYE_REPLY, intent="goodbye", confidence=100.0)

    if is_rag_enabled():
        try:
            result = await semantic_rag_response(message, RESOURCES)
        except Exception:
            logger.exception("RAG pipeline failed for user %s", user.id)
            result = {}

        if result.get("response"):
            intent = result.get("intent")
            confidence = result.get("confidence", 0.0)

            tracker.record_hit(intent or "general")
            log_query(message, intent, confidence)

            return ChatResponse(
                response=result["response"],
                intent=intent,
                confidence=confidence,
                link=result.get("link"),
                rag_used=True,
            )

    log_query(message, None, 0.0)
    return ChatResponse(response=FALLBACK_REPLY)