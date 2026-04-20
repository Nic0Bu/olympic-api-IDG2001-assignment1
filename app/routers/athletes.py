"""Athlete data endpoint."""

from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AthleteEvent, User
from app.helpers.auth import consume_token
from app.helpers.response import format_response

router = APIRouter(prefix="/v1/athlete", tags=["athletes"])


@router.get("/{athlete_id}")
def get_athlete(
    athlete_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _user: User = Depends(consume_token),
):
    """Return all Olympic results for a given athlete ID.

    Uses the athlete's original dataset ID. Costs 1 token.
    Supports JSON (default) and XML via Accept header.
    """
    rows = (
        db.query(AthleteEvent)
        .filter(AthleteEvent.athlete_id == athlete_id)
        .all()
    )
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
    return format_response(data, request)
