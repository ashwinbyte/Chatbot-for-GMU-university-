"""
matcher.py — Scoring engine for GMU Chatbot v2

Replaces find_link() from the original test_chatbot.py

Key fix over original:
  Original → returned FIRST keyword match found (wrong)
  This     → scores ALL 26 entries, returns HIGHEST scorer (correct)

Also works without any external NLP library.
Uses rapidfuzz if installed, falls back to Python stdlib difflib.
"""

import re
import json
from pathlib import Path

# ── Fuzzy library — try fast one first, fall back to stdlib ──────────────
try:
    from rapidfuzz import fuzz as _rf
    def _partial_ratio(a: str, b: str) -> float:
        return _rf.partial_ratio(a, b)
    FUZZY_BACKEND = "rapidfuzz"
except ImportError:
    from difflib import SequenceMatcher
    def _partial_ratio(a: str, b: str) -> float:
        if not a or not b:
            return 0.0
        shorter, longer = (a, b) if len(a) <= len(b) else (b, a)
        best = 0.0
        for i in range(len(longer) - len(shorter) + 1):
            w = longer[i:i + len(shorter)]
            r = SequenceMatcher(None, shorter, w).ratio() * 100
            if r > best:
                best = r
        return best
    FUZZY_BACKEND = "difflib (stdlib fallback)"

# ── Stop words — no NLTK download needed ────────────────────────────────
STOP_WORDS = {
    "a","an","the","is","it","in","on","at","to","for","of","and","or",
    "but","not","with","this","that","can","i","me","my","we","you","do",
    "how","where","what","when","who","are","was","be","been","have","has",
    "had","about","would","could","should","will","please","need","want",
    "find","get","tell","show","help","any","some","more","information",
    "info","know","does","did","its","their","there","here","which","just",
}

MATCH_THRESHOLD   = 65
SUGGEST_THRESHOLD = 45


# ── Tokenizer ────────────────────────────────────────────────────────────
def _tokenize(text: str) -> list:
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return [t for t in text.split() if t and t not in STOP_WORDS]


# ── Word boundary check ──────────────────────────────────────────────────
def _word_boundary_match(keyword: str, query: str) -> bool:
    pattern = r"(?<![a-z])" + re.escape(keyword) + r"(?![a-z])"
    return bool(re.search(pattern, query))


# ── Score one database entry against the query ───────────────────────────
def _score_entry(query_lower: str, query_tokens: list, entry: dict) -> float:
    best = 0.0
    for keyword in entry.get("keywords", []):
        kw = keyword.lower()
        kt = _tokenize(keyword)

        # Tier 1 — exact whole-word match → score 100, stop immediately
        if len(kw) <= 3:
            if kw in query_tokens:
                return 100.0
        else:
            if _word_boundary_match(kw, query_lower):
                return 100.0

        # Tier 2 — all keyword tokens present in query tokens → score 90
        if kt and all(t in query_tokens for t in kt):
            best = max(best, 90.0)
            continue

        # Tier 3+4 — fuzzy (only for queries with 2+ tokens to avoid false positives)
        if len(query_lower) >= 5 and len(query_tokens) >= 2:
            ratio = _partial_ratio(kw, query_lower)
            lw    = min(1.0, len(kw) / 8.0)
            best  = max(best, ratio * (0.5 + 0.5 * lw))

            for qt in query_tokens:
                for k in kt:
                    if len(k) >= 3:
                        best = max(best, _partial_ratio(k, qt) * 0.75)

    return best


# ── Public API ───────────────────────────────────────────────────────────
def find_best_match(user_query: str, database: list, threshold: int = MATCH_THRESHOLD):
    """Score all 26 entries and return (best_entry, score) or (None, 0)."""
    if not user_query or not user_query.strip():
        return None, 0.0

    ql = user_query.lower().strip()
    qt = _tokenize(ql)

    scored = []
    for entry in database:
        s = _score_entry(ql, qt, entry)
        if s >= threshold:
            scored.append((s, entry))

    if not scored:
        return None, 0.0

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[0][1], scored[0][0]


def find_suggestions(user_query: str, database: list) -> list:
    """Return up to 3 weak-match intent names for 'did you mean?' messages."""
    ql = user_query.lower().strip()
    qt = _tokenize(ql)
    scored = []
    for entry in database:
        s = _score_entry(ql, qt, entry)
        if MATCH_THRESHOLD > s >= SUGGEST_THRESHOLD:
            scored.append((s, entry["intent"]))
    scored.sort(reverse=True)
    return [i for _, i in scored[:3]]


def load_database(file_path) -> list:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
