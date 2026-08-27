from fastapi import APIRouter
from pathlib import Path
from backend.app.services.analytics import PopularityTracker

router  = APIRouter()
BASE    = Path(__file__).parent.parent.parent
TRACKER = PopularityTracker(str(BASE / "data" / "analytics.json"))

class StatsResponse:
    top_topics: list[dict]

@router.get("/stats")
async def stats():
    top = TRACKER.get_top(10)
    return {"top_topics": [{"intent": i, "count": c} for i, c in top]}