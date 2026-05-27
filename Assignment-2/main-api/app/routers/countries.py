"""Country data endpoint."""

from collections import defaultdict
from typing import Any
from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AthleteEvent, User
from app.helpers.auth import consume_token
from app.helpers.response import format_response
from app.helpers.services import cache_get, cache_set

router = APIRouter(prefix="/v2/country", tags=["countries"])


def _count_medals(rows: list) -> dict:
    """Aggregate medal counts per sport."""
    sports: Any = defaultdict(
        lambda: {"gold": 0, "silver": 0, "bronze": 0, "na": 0, "total": 0}
    )
    for row in rows:
        medal = (row.medal or "NA").strip()
        sport = row.sport or "Unknown"
        sports[sport]["total"] += 1
        if medal == "Gold":
            sports[sport]["gold"] += 1
        elif medal == "Silver":
            sports[sport]["silver"] += 1
        elif medal == "Bronze":
            sports[sport]["bronze"] += 1
        else:
            sports[sport]["na"] += 1
    return dict(sports)


@router.get("/{noc}")
def get_country(
    noc: str,
    request: Request,
    db: Session = Depends(get_db),
    _user: User = Depends(consume_token),
):
    """Return medal counts per sport for a NOC country code. Costs 1 token.
    NOC is case-insensitive. Supports JSON, XML, CSV.
    """
    cache_key = str(request.url)
    cached = cache_get(cache_key)
    if cached["hit"]:
        return format_response(cached["data"], request)

    rows = db.query(AthleteEvent).filter(AthleteEvent.noc == noc.upper()).all()
    if not rows:
        raise HTTPException(status_code=404, detail="Country not found")

    data = {"noc": noc.upper(), "sports": _count_medals(rows)}
    cache_set(cache_key, data)
    return format_response(data, request)
