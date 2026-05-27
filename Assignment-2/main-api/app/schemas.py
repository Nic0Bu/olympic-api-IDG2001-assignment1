"""Pydantic schemas for request/response validation."""

from typing import Optional
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    tokens: Optional[int] = None


class UserOut(BaseModel):
    id: str
    email: str
    tokens: int

    model_config = {"from_attributes": True}


class TokenRedeem(BaseModel):
    """Redeem a code received from the token shop."""
    user_id: str
    code: str


class PriceUpdate(BaseModel):
    price: float


class EventCreate(BaseModel):
    name: str
    athlete_id: Optional[int] = None
    sex: Optional[str] = None
    age: Optional[float] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    team: Optional[str] = None
    noc: Optional[str] = None
    games: Optional[str] = None
    year: Optional[int] = None
    season: Optional[str] = None
    city: Optional[str] = None
    sport: Optional[str] = None
    event: Optional[str] = None
    medal: Optional[str] = None
