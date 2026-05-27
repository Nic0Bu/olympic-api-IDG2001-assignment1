"""User management endpoints (CRUD)."""

from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import bcrypt

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserUpdate, UserOut

router = APIRouter(prefix="/v2/user", tags=["users"])


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


@router.post("", response_model=UserOut, status_code=201)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """Create a new user. Starts with 100 tokens."""
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(email=user_in.email, password=hash_password(user_in.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("", response_model=List[UserOut])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserOut)
def replace_user(user_id: str, update: UserCreate, db: Session = Depends(get_db)):
    """Full replacement of email and password (tokens unchanged)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.email = update.email
    user.password = hash_password(update.password)
    db.commit()
    db.refresh(user)
    return user


@router.patch("/{user_id}", response_model=UserOut)
def update_user(user_id: str, update: UserUpdate, db: Session = Depends(get_db)):
    """Partial update — only provided fields are changed."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if update.email is not None:
        user.email = update.email
    if update.password is not None:
        user.password = hash_password(update.password)
    if update.tokens is not None:
        user.tokens = update.tokens
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
