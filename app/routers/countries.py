"""Country data endpoint."""

from collections import defaultdict
from typing import Any
from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AthleteEvent, User
from app.helpers.auth import consume_token
from app.helpers.response import format_response

router = APIRouter(prefix="/v1/country", tags=["countries"])


def _count_medals(rows: list) -> dict:
    """Aggregate medal counts per sport from a list of AthleteEvent rows.

    Returns a dict keyed by sport name with gold/silver/bronze/na/total counts.
    """
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
    """Return medal counts grouped by sport for a given NOC country code.

    The NOC code is case-insensitive (e.g. NOR, nor, Nor all work).
    Costs 1 token. Supports JSON (default) and XML via Accept header.
    """
    rows = (
        db.query(AthleteEvent)
        .filter(AthleteEvent.noc == noc.upper())
        .all()
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Country not found")
    data = {"noc": noc.upper(), "sports": _count_medals(rows)}
    return format_response(data, request)
