"""
rag.py — RAG engine for GMU Chatbot v3
PRIMARY → Groq LLaMA 3.3 (14,400 free requests/day)
"""

from __future__ import annotations
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

_groq_key    = os.environ.get("GROQ_API_KEY", "")
_groq_client = None
RAG_ENABLED  = bool(_groq_key and GROQ_AVAILABLE)

if RAG_ENABLED:
    try:
        _groq_client = Groq(api_key=_groq_key)
        print("RAG enabled — Groq LLaMA 3.3 — 14,400 requests/day free")
    except Exception as e:
        RAG_ENABLED = False
        print(f" Groq setup failed: {e}")
else:
    if not _groq_key:
        print(" GROQ_API_KEY not found — add it to .env")
    elif not GROQ_AVAILABLE:
        print("groq not installed — run: pip install groq")


def _call_llm(prompt: str) -> str | None:
    if not RAG_ENABLED or _groq_client is None:
        return None
    try:
        response = _groq_client.chat.completions.create(
            model       = "llama-3.3-70b-versatile",
            messages    = [{"role": "user", "content": prompt}],
            max_tokens  = 500,
            temperature = 0.7
        )
        text = response.choices[0].message.content.strip()
        if text:
            return text
    except Exception as e:
        print(f"Groq error: {e}")
    return None


def generate_rag_response(user_query: str, matched_entry: dict) -> str | None:
    if not RAG_ENABLED:
        return None

    scraped_context = ""
    try:
        from src.embeddings import find_similar_chunks, is_vector_db_ready
        if is_vector_db_ready():
            chunks = find_similar_chunks(user_query, n_results=3)
            if chunks:
                scraped_context = "\n\n".join([
                    f"[From {c['url']}]:\n{c['text']}" for c in chunks
                ])
    except Exception:
        pass

    if scraped_context:
        context = f"Real content from GMU website:\n\n{scraped_context}"
    else:
        context = f"""Topic: {matched_entry.get('intent', '')}
Description: {matched_entry.get('description', '')}
Details: {matched_entry.get('summary', '')}"""

    official_link = matched_entry.get("link", "")
    prompt = f"""You are a helpful assistant for George Mason University (GMU) students.
Use ONLY the provided context to answer. Be conversational and concise — 2 to 4 sentences.
End by mentioning: {official_link}

Context:
{context}

Student question: {user_query}
Answer:"""
    return _call_llm(prompt)


def conversational_fallback(user_query: str, database: list) -> str | None:
    if not RAG_ENABLED:
        return None

    resources_summary = "\n".join([
        f"- {e['intent']}: {e.get('description','')} → {e.get('link','')}"
        for e in database if e.get('link')
    ])

    scraped_context = ""
    try:
        from src.embeddings import find_similar_chunks, is_vector_db_ready
        if is_vector_db_ready():
            chunks = find_similar_chunks(user_query, n_results=3)
            if chunks:
                scraped_context = "\n\n".join([
                    f"[From {c['url']}]:\n{c['text']}" for c in chunks
                ])
    except Exception:
        pass

    prompt = f"""You are a helpful GMU assistant.

GMU RESOURCES:
{resources_summary}

CONTEXT:
{scraped_context if scraped_context else "Use general GMU knowledge."}

Rules: mention relevant links, be conversational, 2-4 sentences.

Student question: {user_query}
Answer:"""
    return _call_llm(prompt)


async def semantic_rag_response(user_query: str, database: list) -> dict:
    if not RAG_ENABLED:
        return {"response": None}

    relevant_chunks = []
    detected_intent = None
    detected_link   = None

    try:
        from src.embeddings import find_similar_chunks, is_vector_db_ready
        if is_vector_db_ready():
            chunks = find_similar_chunks(user_query, n_results=5)
            if chunks:
                relevant_chunks = chunks
                detected_intent = chunks[0].get("intent")
                for entry in database:
                    if entry.get("intent") == detected_intent:
                        detected_link = entry.get("link")
                        break
    except Exception as e:
        print(f"Vector search error: {e}")

    if relevant_chunks:
        scraped_context = "\n\n".join([
            f"[Source: {c['url']}]\n{c['text']}" for c in relevant_chunks
        ])
    else:
        scraped_context = "No specific content found. Use your general GMU knowledge."

    resource_list = "\n".join([
        f"- {e['intent']}: {e.get('description', '')} → {e.get('link', '')}"
        for e in database
        if e.get("link") and e.get("intent", "").lower()
        not in {"greeting", "goodbye", "goodby"}
    ])

    prompt = f"""You are a helpful AI assistant for George Mason University (GMU) students.

AVAILABLE GMU RESOURCES:
{resource_list}

RELEVANT CONTENT FROM GMU WEBSITES:
{scraped_context}

INSTRUCTIONS:
- Answer using the relevant content above as your primary source
- If content does not fully answer use your general GMU knowledge
- Always mention the most relevant resource link
- If unrelated to GMU politely redirect
- Be conversational and concise — 2 to 4 sentences

Student question: {user_query}
Answer:"""

    text = _call_llm(prompt)
    if text:
        return {
            "response":   text,
            "intent":     detected_intent or "general",
            "confidence": round(relevant_chunks[0]["similarity"] * 100, 1)
                          if relevant_chunks else 0.0,
            "link":       detected_link,
            "rag_used":   True
        }

    return {"response": None}


def is_rag_enabled() -> bool:
    return RAG_ENABLED