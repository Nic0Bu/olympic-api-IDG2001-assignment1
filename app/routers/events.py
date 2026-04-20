"""Event creation endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AthleteEvent
from app.schemas import EventCreate

router = APIRouter(prefix="/v1/event", tags=["events"])


@router.post("", status_code=201)
def create_event(body: EventCreate, db: Session = Depends(get_db)):
    """Create a new athlete event participation entry in the database."""
    event = AthleteEvent(**body.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return {"id": event.id, "message": "Event created successfully"}
