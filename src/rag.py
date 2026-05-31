"""
rag.py — RAG (Retrieval-Augmented Generation) engine for GMU Chatbot v2
 
How RAG works here:
  RETRIEVE → embeddings.py finds most relevant scraped GMU content chunks
  GENERATE → Gemini writes a natural answer using those chunks as context
 
Why this is better than plain keywords:
  - Answers from REAL GMU website content (scraped)
  - Handles semantic queries: "I feel stressed" → mental health ✅
  - No hallucination — Gemini only uses the retrieved context
  - Graceful fallback — if Gemini fails, pre-written description is used
 
Setup:
  1. Get free key from aistudio.google.com
  2. Add to .env: GEMINI_API_KEY=your_key_here
"""
 
from __future__ import annotations
import os
 
# Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
 
# Try importing the NEW Gemini library (google-genai)
try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
 
# ── Configure Gemini ─────────────────────────────────────────────────────
_api_key    = os.environ.get("GEMINI_API_KEY", "")
RAG_ENABLED = bool(_api_key and GEMINI_AVAILABLE)
_client     = None
 
if RAG_ENABLED:
    try:
        _client = genai.Client(api_key=_api_key)
        print("✅ RAG enabled (Gemini 2.0 Flash)")
    except Exception as e:
        RAG_ENABLED = False
        print(f"⚠️  Gemini setup failed: {e} — RAG disabled")
else:
    if not _api_key:
        print("⚠️  GEMINI_API_KEY not found in .env — RAG disabled, using fallback responses")
    elif not GEMINI_AVAILABLE:
        print("⚠️  google-genai not installed — run: pip install google-genai")
 
 
def generate_rag_response(user_query: str, matched_entry: dict) -> str | None:
    """
    Generate a natural conversational response using:
      - The user's original query
      - The matched database entry (for fallback context)
      - Scraped website content (for rich real content, if available)
 
    Returns generated text, or None if RAG disabled/failed.
    When None is returned, responder.py uses the pre-written description.
    """
    if not RAG_ENABLED or _client is None:
        return None
 
    # ── Try to get scraped content for richer context ────────────────
    scraped_context = ""
    try:
        from src.embeddings import find_similar_chunks, is_vector_db_ready
        if is_vector_db_ready():
            chunks = find_similar_chunks(user_query, n_results=3)
            if chunks:
                scraped_context = "\n\n".join([
                    f"[From {c['url']}]:\n{c['text']}"
                    for c in chunks
                ])
    except Exception:
        pass   # embeddings not available — use fallback context
 
    # ── Build context ────────────────────────────────────────────────
    if scraped_context:
        context = f"""Real content from GMU website:
 
{scraped_context}"""
    else:
        # Fall back to pre-written summary from gmu_resources.json
        context = f"""Topic: {matched_entry.get('intent', '')}
Description: {matched_entry.get('description', '')}
Details: {matched_entry.get('summary', '')}"""
 
    official_link = matched_entry.get("link", "")
 
    # ── Build prompt ─────────────────────────────────────────────────
    prompt = f"""You are a helpful and friendly assistant for George Mason University (GMU) students.
 
Use ONLY the provided context below to answer the student's question.
Do NOT make up information not in the context.
Be conversational and concise — 2 to 4 sentences maximum.
If the answer mentions specific steps, dates, or procedures, include them.
End your response by naturally mentioning the official resource link: {official_link}
 
Context:
{context}
 
Student question: {user_query}
 
Answer:"""
 
    # ── Call Gemini ──────────────────────────────────────────────────
    try:
        response = _client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        text = response.text.strip()
        if text:
            return text
    except Exception as e:
        print(f"Gemini API error: {e} — using fallback")
 
    return None
 
 
def is_rag_enabled() -> bool:
    return RAG_ENABLED