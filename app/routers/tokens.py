"""Token management endpoint."""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import TokenAdd, UserOut

router = APIRouter(prefix="/v1/tokens", tags=["tokens"])


@router.post("", response_model=UserOut)
def add_tokens(body: TokenAdd, db: Session = Depends(get_db)):
    """Add tokens to a user's account.

    The amount must be a positive integer.
    """
    if body.amount <= 0:
        raise HTTPException(
            status_code=400, detail="Amount must be a positive integer"
        )
    user = db.query(User).filter(User.id == body.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.tokens += body.amount
    db.commit()
    db.refresh(user)
    return user
