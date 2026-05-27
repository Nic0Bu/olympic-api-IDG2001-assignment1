"""Token shop service.

Handles token purchases. Users buy tokens here and get a secret code back.
They then take that code to the main API to actually receive the tokens.

Endpoints:
    POST /buy      — buy tokens, get a secret code
    POST /verify   — main API calls this to check a code and get token count
    GET  /price    — current token price (tokens per unit of money)
    PUT  /price    — admin: update the token price
"""

import os
import secrets
import time
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import OperationalError

_db_url = os.getenv("DATABASE_URL", "sqlite:///./shop.db")
if _db_url.startswith("postgres://"):
    _db_url = _db_url.replace("postgres://", "postgresql://", 1)

_connect_args = {"check_same_thread": False} if "sqlite" in _db_url else {}
engine = create_engine(_db_url, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

ADMIN_KEY = os.getenv("ADMIN_KEY", "supersecret")


class PurchaseCode(Base):
    __tablename__ = "purchase_codes"
    code = Column(String, primary_key=True)
    username = Column(String, nullable=False)
    money = Column(Integer, nullable=False)
    used = Column(Boolean, default=False, nullable=False)


class TokenPrice(Base):
    __tablename__ = "token_price"
    id = Column(Integer, primary_key=True)
    # how many tokens per unit of money
    price = Column(Float, nullable=False, default=10.0)


app = FastAPI(title="Token Shop")


@app.on_event("startup")
def init_db():
    # wait for postgres to be ready
    for i in range(30):
        try:
            Base.metadata.create_all(bind=engine)
            break
        except OperationalError:
            print(f"Waiting for DB... ({i + 1}/30)")
            time.sleep(2)

    db = SessionLocal()
    try:
        if not db.query(TokenPrice).first():
            db.add(TokenPrice(id=1, price=10.0))
            db.commit()
    finally:
        db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class BuyRequest(BaseModel):
    username: str
    password: str
    money: int


class VerifyRequest(BaseModel):
    code: str


class PriceUpdate(BaseModel):
    price: float


@app.post("/buy")
def buy_tokens(body: BuyRequest, db: Session = Depends(get_db)):
    """Buy tokens. Returns a one-time secret code to redeem at the main API."""
    if body.money <= 0:
        raise HTTPException(status_code=400, detail="money must be a positive integer")
    if not body.username or not body.password:
        raise HTTPException(status_code=400, detail="username and password are required")

    code = secrets.token_hex(16)
    db.add(PurchaseCode(code=code, username=body.username, money=body.money))
    db.commit()
    return {"secret": code}


@app.post("/verify")
def verify_code(body: VerifyRequest, db: Session = Depends(get_db)):
    """Check a code and return how many tokens it's worth. Marks the code as used."""
    purchase = (
        db.query(PurchaseCode)
        .filter(PurchaseCode.code == body.code, PurchaseCode.used == False)  # noqa: E712
        .first()
    )
    if not purchase:
        raise HTTPException(status_code=404, detail="Code not found or already used")

    price_row = db.query(TokenPrice).first()
    tokens = int(purchase.money * price_row.price)

    purchase.used = True
    db.commit()

    return {"tokens": tokens}


@app.get("/price")
def get_price(db: Session = Depends(get_db)):
    """Returns the current token price (tokens per unit of money)."""
    row = db.query(TokenPrice).first()
    return {"price": row.price, "description": "tokens per unit of money"}


@app.put("/price")
def update_price(
    body: PriceUpdate,
    x_admin_key: str = Header(...),
    db: Session = Depends(get_db),
):
    """Admin only — update the token price."""
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin key")
    if body.price <= 0:
        raise HTTPException(status_code=400, detail="price must be positive")
    row = db.query(TokenPrice).first()
    row.price = body.price
    db.commit()
    return {"price": row.price}
