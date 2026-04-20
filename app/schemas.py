"""Pydantic schemas for request validation and response serialization."""

from typing import Optional
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """Schema for creating a new user."""

    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Schema for partially updating a user's fields."""

    email: Optional[EmailStr] = None
    password: Optional[str] = None
    tokens: Optional[int] = None


class UserOut(BaseModel):
    """Public-facing user representation (password excluded)."""

    id: str
    email: str
    tokens: int

    model_config = {"from_attributes": True}


class TokenAdd(BaseModel):
    """Schema for adding tokens to a user account."""

    user_id: str
    amount: int


class EventCreate(BaseModel):
    """Schema for creating a new athlete event entry."""

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
