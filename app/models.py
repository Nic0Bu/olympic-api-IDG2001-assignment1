"""SQLAlchemy ORM models for users and Olympic event data."""

import uuid
from typing import Optional
from sqlalchemy import String, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class User(Base):
    """A registered API user with an email, hashed password, and token balance."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(
        String, unique=True, nullable=False, index=True
    )
    password: Mapped[str] = mapped_column(String, nullable=False)
    tokens: Mapped[int] = mapped_column(Integer, default=100, nullable=False)


class AthleteEvent(Base):
    """A single athlete's participation in an Olympic event."""

    __tablename__ = "athlete_events"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    athlete_id: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    sex: Mapped[Optional[str]] = mapped_column(String)
    age: Mapped[Optional[float]] = mapped_column(Float)
    height: Mapped[Optional[float]] = mapped_column(Float)
    weight: Mapped[Optional[float]] = mapped_column(Float)
    team: Mapped[Optional[str]] = mapped_column(String)
    noc: Mapped[Optional[str]] = mapped_column(String, index=True)
    games: Mapped[Optional[str]] = mapped_column(String)
    year: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    season: Mapped[Optional[str]] = mapped_column(String)
    city: Mapped[Optional[str]] = mapped_column(String)
    sport: Mapped[Optional[str]] = mapped_column(String, index=True)
    event: Mapped[Optional[str]] = mapped_column(String)
    medal: Mapped[Optional[str]] = mapped_column(String)
