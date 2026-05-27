"""Token endpoints — check price, redeem a code, admin price update."""

import os
from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import TokenRedeem, PriceUpdate, UserOut
from app.helpers.services import shop_verify_code, shop_get_price, shop_update_price

router = APIRouter(prefix="/v2/tokens", tags=["tokens"])


@router.get("")
def get_token_price():
    """Returns the current token price from the token shop."""
    return shop_get_price()


@router.post("", response_model=UserOut)
def redeem_code(body: TokenRedeem, db: Session = Depends(get_db)):
    """Redeem a code from the token shop and add tokens to the user account."""
    user = db.query(User).filter(User.id == body.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    tokens = shop_verify_code(body.code)
    if tokens is None:
        raise HTTPException(status_code=400, detail="Code invalid or already used")

    user.tokens += tokens
    db.commit()
    db.refresh(user)
    return user


@router.put("/price")
def update_token_price(
    body: PriceUpdate,
    x_admin_key: str = Header(..., description="Admin key"),
):
    """Admin-only: update the token price in the token shop."""
    admin_key = os.getenv("ADMIN_KEY", "supersecret")
    if x_admin_key != admin_key:
        raise HTTPException(status_code=403, detail="Invalid admin key")
    return shop_update_price(body.price, x_admin_key)
