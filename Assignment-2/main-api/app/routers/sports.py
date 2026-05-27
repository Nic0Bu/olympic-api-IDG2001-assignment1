"""Sport data endpoint with query-parameter filtering."""

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi import Query as QParam
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import AthleteEvent, User
from app.helpers.auth import consume_token
from app.helpers.response import format_response
from app.helpers.services import cache_get, cache_set

router = APIRouter(prefix="/v2/sport", tags=["sports"])

MEDAL_MAP = {"gold": "Gold", "silver": "Silver", "bronze": "Bronze"}


def _aggregate_medals(rows: list) -> dict:
    counts = {"gold": 0, "silver": 0, "bronze": 0, "na": 0, "total": len(rows)}
    for row in rows:
        medal = (row.medal or "NA").strip()
        if medal == "Gold":
            counts["gold"] += 1
        elif medal == "Silver":
            counts["silver"] += 1
        elif medal == "Bronze":
            counts["bronze"] += 1
        else:
            counts["na"] += 1
    return counts


@router.get("/{sport_id}")
def get_sport(
    sport_id: str,
    request: Request,
    db: Session = Depends(get_db),
    _user: User = Depends(consume_token),
    country: str = QParam(None, description="Filter by NOC country code"),
    year: int = QParam(None, description="Filter by Olympic year"),
    medals: str = QParam(None, description="gold, silver, or bronze"),
):
    """Return participation and medal data for a sport. Costs 1 token.
    sport_id uses hyphens for spaces (e.g. ski-jumping).
    Supports JSON, XML, CSV.
    """
    cache_key = str(request.url)
    cached = cache_get(cache_key)
    if cached["hit"]:
        return format_response(cached["data"], request)

    sport_name = sport_id.replace("-", " ")
    query = db.query(AthleteEvent).filter(
        func.lower(AthleteEvent.sport) == sport_name.lower()
    )
    if country:
        query = query.filter(AthleteEvent.noc == country.upper())
    if year:
        query = query.filter(AthleteEvent.year == year)
    if medals:
        medal_val = MEDAL_MAP.get(medals.lower())
        if not medal_val:
            raise HTTPException(status_code=400, detail="medals must be gold, silver, or bronze")
        query = query.filter(AthleteEvent.medal == medal_val)

    rows = query.all()
    if not rows and not any([country, year, medals]):
        raise HTTPException(status_code=404, detail="Sport not found")

    data = {
        "sport": sport_name,
        "filters": {"country": country, "year": year, "medals": medals},
        "medals": _aggregate_medals(rows),
        "count": len(rows),
    }
    cache_set(cache_key, data)
    return format_response(data, request)
