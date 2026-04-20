"""Dependency for authenticating API calls and consuming user tokens."""

from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User


def consume_token(
    x_user_id: str = Header(..., description="Your user ID"),
    db: Session = Depends(get_db),
) -> User:
    """Validate a user by ID and deduct one token for the API call.

    Raises 401 if the user ID is not found.
    Raises 402 if the user has no tokens remaining.
    """
    user = db.query(User).filter(User.id == x_user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user ID")
    if user.tokens <= 0:
        raise HTTPException(
            status_code=402, detail="No tokens left. Please add more."
        )
    user.tokens -= 1
    db.commit()
    db.refresh(user)
    return user
