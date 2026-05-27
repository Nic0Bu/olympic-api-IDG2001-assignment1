"""Database engine and session setup."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

_url = os.getenv("DATABASE_URL", "sqlite:///./olympic.db")

# Render (and some other hosts) give 'postgres://' which SQLAlchemy doesn't accept
if _url.startswith("postgres://"):
    _url = _url.replace("postgres://", "postgresql://", 1)

DATABASE_URL = _url

_connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_engine(DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
