"""Token consumption dependency — validates user, rate-limits, logs the request."""

import time
from fastapi import Header, HTTPException, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.helpers.services import rate_limit_check, log_request


def consume_token(
    request: Request,
    x_user_id: str = Header(..., description="Your user ID"),
    db: Session = Depends(get_db),
) -> User:
    """Validate user, apply rate-limit delay, deduct one token, log the call."""
    user = db.query(User).filter(User.id == x_user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user ID")
    if user.tokens <= 0:
        raise HTTPException(status_code=402, detail="No tokens remaining.")

    delay = rate_limit_check(user.id, user.email)
    if delay > 0:
        time.sleep(delay)

    user.tokens -= 1
    db.commit()
    db.refresh(user)

    endpoint = f"{request.method} {request.url.path}"
    log_request(user.email, endpoint, 1)

    return user
