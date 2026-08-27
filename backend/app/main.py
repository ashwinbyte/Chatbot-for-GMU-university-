from __future__ import annotations
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routes.chat  import router as chat_router
from backend.app.routes.stats import router as stats_router

app = FastAPI(
    title       = "GMU Resource Chatbot API",
    description = "AI-powered chatbot for GMU students using pure semantic RAG.",
    version     = "3.0.0",
    docs_url    = "/docs",
    redoc_url   = "/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(stats_router)

@app.get("/")
async def health():
    from backend.app.services.rag        import is_rag_enabled
    from backend.app.services.embeddings import is_vector_db_ready
    return {
        "status":       "online",
        "version":      "3.0.0",
        "architecture": "pure semantic RAG — Groq LLaMA 3.3",
        "rag_enabled":  is_rag_enabled(),
        "vector_db":    is_vector_db_ready(),
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"\n{'='*50}")
    print(f"  GMU Resource Chatbot v3.0")
    print(f"  Running on: http://localhost:{port}")
    print(f"  API docs:   http://localhost:{port}/docs")
    print(f"{'='*50}\n")
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=port, reload=True)