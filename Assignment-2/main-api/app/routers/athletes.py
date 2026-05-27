"""Athlete data endpoint."""

from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AthleteEvent, User
from app.helpers.auth import consume_token
from app.helpers.response import format_response
from app.helpers.services import cache_get, cache_set

router = APIRouter(prefix="/v2/athlete", tags=["athletes"])


@router.get("/{athlete_id}")
def get_athlete(
    athlete_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _user: User = Depends(consume_token),
):
    """Return all Olympic results for an athlete. Costs 1 token.
    Supports JSON (default), XML, and CSV via Accept header.
    """
    cache_key = str(request.url)
    cached = cache_get(cache_key)
    if cached["hit"]:
        return format_response(cached["data"], request)

    rows = db.query(AthleteEvent).filter(AthleteEvent.athlete_id == athlete_id).all()
    if not rows:
        raise HTTPException(status_code=404, detail="Athlete not found")

    first = rows[0]
    data = {
        "athlete_id": athlete_id,
        "name": first.name,
        "sex": first.sex,
        "team": first.team,
        "noc": first.noc,
        "events": [
            {
                "games": r.games,
                "year": r.year,
                "season": r.season,
                "city": r.city,
                "sport": r.sport,
                "event": r.event,
                "medal": r.medal,
                "age": r.age,
                "height": r.height,
                "weight": r.weight,
            }
            for r in rows
        ],
    }
    cache_set(cache_key, data)
    return format_response(data, request)
