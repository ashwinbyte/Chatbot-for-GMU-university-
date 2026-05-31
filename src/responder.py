"""
responder.py — Response formatter for GMU Chatbot v2

Separated from matcher.py so formatting can be changed
without touching the matching algorithm.

Tries RAG first if available, falls back to pre-written descriptions.
"""

from __future__ import annotations

_GREETINGS = [
    "Hi there! 👋 I'm the GMU Resource Assistant. Ask me anything about transcripts, financial aid, housing, health services, career resources, and more. What can I help you with?",
    "Hello! Welcome to the GMU Chatbot. 🎓 I can help you find any campus resource — just ask in plain English.",
    "Hey! I'm the GMU Resource Assistant. Ask me about classes, housing, health, careers, IT support, and more!",
]
_GOODBYES = [
    "Goodbye! Hope I was helpful. Have a great day! 😊",
    "Take care! Come back anytime you need GMU information. 👋",
    "Bye! Best of luck with your studies at Mason! 🟢",
]
_gi = 0
_bi = 0


def format_match(entry: dict, confidence: float, user_query: str = None) -> str:
    """
    Format a matched entry into a response string.
    Tries RAG (Gemini) first — falls back to pre-written description.
    """
    intent = entry.get("intent", "").lower()

    # ── Special intents ──────────────────────────────────────────────
    if intent == "greeting":
        global _gi
        msg = _GREETINGS[_gi % len(_GREETINGS)]
        _gi += 1
        return msg

    if intent in ("goodby", "goodbye"):
        global _bi
        msg = _GOODBYES[_bi % len(_GOODBYES)]
        _bi += 1
        return msg

    # ── Try RAG first ────────────────────────────────────────────────
    if user_query:
        try:
            from src.rag import generate_rag_response, is_rag_enabled
            if is_rag_enabled():
                rag = generate_rag_response(user_query, entry)
                if rag:
                    return rag
        except Exception:
            pass   # rag.py missing or Gemini failed — fall through

    # ── Fallback: pre-written response ───────────────────────────────
    lines = [f"📌 **{entry.get('intent','').title()}**"]

    desc = entry.get("description", "").strip()
    if desc:
        lines.append(desc)

    summary = entry.get("summary", "").strip()
    if summary:
        lines.append(summary)

    link = entry.get("link", "").strip()
    if link:
        lines.append(f"🔗 {link}")

    if confidence < 80:
        lines.append(f"⚠️ Confidence {confidence:.0f}% — let me know if this isn't what you meant.")

    return "\n\n".join(lines)


def format_no_match(suggestions: list) -> str:
    if suggestions:
        s = ", ".join(f'"{x}"' for x in suggestions)
        return f"Sorry, I couldn't find a confident match.\nDid you mean: {s}?\n\nType **help** to see all available topics."
    return "Sorry, I couldn't find a match for that query.\nType **help** to see all available topics."


def format_help(database: list) -> str:
    lines = ["📚 **Available GMU Resource Topics**\n"]
    for entry in database:
        if entry.get("intent", "").lower() not in {"greeting", "goodby", "goodbye"}:
            lines.append(f"• **{entry['intent'].title()}** — {entry.get('description','')}")
    lines.append("\nJust ask me about any of these in plain English!")
    return "\n".join(lines)
