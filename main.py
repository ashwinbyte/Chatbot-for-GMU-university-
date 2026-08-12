
from __future__ import annotations
import sys
import os
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.analytics import PopularityTracker, log_query
from src.responder import format_help


def load_database(file_path) -> list:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


app = FastAPI(
    title="GMU Resource Chatbot API",
    description="AI-powered chatbot for GMU students using pure semantic RAG.",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE    = Path(__file__).parent
DB      = load_database(BASE / "data" / "gmu_resources.json")
TRACKER = PopularityTracker(str(BASE / "data" / "analytics.json"))


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=300,
        description="Student query in plain English",
        json_schema_extra={"example": "where do I get my transcript"}
    )

class ChatResponse(BaseModel):
    response:   str
    intent:     str | None = None
    confidence: float      = 0.0
    link:       str | None = None
    rag_used:   bool       = False

class StatsResponse(BaseModel):
    top_topics: list[dict]


@app.get("/", summary="Health check")
async def health():
    from src.rag        import is_rag_enabled
    from src.embeddings import is_vector_db_ready
    return {
        "status":       "online",
        "version":      "3.0.0",
        "architecture": "pure semantic RAG — Groq LLaMA 3.3",
        "rag_enabled":  is_rag_enabled(),
        "vector_db":    is_vector_db_ready(),
        "resources":    len(DB),
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    message = request.message.strip()

    # Special commands
    if message.lower() in {"help", "?", "topics", "list"}:
        return ChatResponse(response=format_help(DB), intent="help", confidence=100.0)

    if message.lower() in {"stats", "analytics", "popular"}:
        return ChatResponse(response=TRACKER.format_report(), intent="stats", confidence=100.0)

    # Greetings — no API call needed
    msg_lower = message.lower()
    if any(word in msg_lower for word in ["hi", "hello", "hey", "howdy"]):
        return ChatResponse(
            response="Hi there!  I am the GMU Resource Assistant. Ask me anything about campus resources — financial aid, housing, health services, careers, transcripts, and more!",
            intent="greeting",
            confidence=100.0
        )

    # Goodbyes — no API call needed
    if any(word in msg_lower for word in ["bye", "goodbye", "see you", "thanks", "thank you"]):
        return ChatResponse(
            response="Goodbye! Hope I was helpful. Have a great day at Mason! 🎓",
            intent="goodbye",
            confidence=100.0
        )

    # Pure semantic RAG — one path for everything
    from src.rag import semantic_rag_response, is_rag_enabled

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
        response="I am having trouble connecting right now. Please try again in a moment.",
        intent=None,
        confidence=0.0,
        link=None
    )


@app.get("/stats", response_model=StatsResponse)
async def stats():
    top = TRACKER.get_top(10)
    return StatsResponse(
        top_topics=[{"intent": i, "count": c} for i, c in top]
    )


if __name__ == "__main__":
    import uvicorn
    port  = int(os.environ.get("PORT", 8000))
    debug = os.environ.get("ENVIRONMENT", "development") != "production"
    print(f"\n{'='*50}")
    print(f"  GMU Resource Chatbot v3.0")
    print(f"  Architecture: Pure Semantic RAG — Groq")
    print(f"  Running on: http://localhost:{port}")
    print(f"  API docs:   http://localhost:{port}/docs")
    print(f"{'='*50}\n")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=debug)