"""
analytics.py — Persistent query tracking for GMU Chatbot v2

Original code lost all popularity counts on every restart.
This saves counts to analytics.json so data survives forever.
"""

from __future__ import annotations
import json
import logging
from pathlib import Path

# ── Logger ───────────────────────────────────────────────────────────────
logging.basicConfig(
    filename="chatbot.log",
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
    encoding="utf-8",
)
_logger = logging.getLogger("gmu_chatbot")


def log_query(user_query: str, intent: str | None, confidence: float) -> None:
    _logger.info(
        f"query={json.dumps(user_query)} | "
        f"intent={intent or 'NO_MATCH'} | "
        f"confidence={confidence:.1f}"
    )


# ── Tracker ──────────────────────────────────────────────────────────────
class PopularityTracker:
    """Tracks how often each intent is queried. Persists to disk."""

    def __init__(self, analytics_file: str = "data/analytics.json"):
        self.file   = Path(analytics_file)
        self.counts: dict[str, int] = self._load()

    def record_hit(self, intent: str) -> None:
        self.counts[intent] = self.counts.get(intent, 0) + 1
        self._save()

    def get_counts(self) -> dict:
        return dict(sorted(self.counts.items(), key=lambda x: x[1], reverse=True))

    def get_top(self, n: int = 10) -> list:
        return list(self.get_counts().items())[:n]

    def format_report(self) -> str:
        top = self.get_top(10)
        if not top:
            return "No queries recorded yet."
        lines = ["📊 **Top Queried Topics**\n"]
        for rank, (intent, count) in enumerate(top, 1):
            bar = "█" * min(count, 20)
            lines.append(f"{rank:2}. {intent:<30} {bar} ({count})")
        return "\n".join(lines)

    def _load(self) -> dict:
        if self.file.exists():
            try:
                return json.loads(self.file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {}

    def _save(self) -> None:
        self.file.parent.mkdir(parents=True, exist_ok=True)
        self.file.write_text(
            json.dumps(self.counts, indent=2),
            encoding="utf-8"
        )
