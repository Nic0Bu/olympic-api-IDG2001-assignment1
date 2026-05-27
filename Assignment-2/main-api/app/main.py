"""Olympic Games API v2 — entry point.

Start locally with:
    uvicorn app.main:app --reload

All endpoints are under /v2/. Data endpoints require an X-User-Id header
and consume 1 token per call. Requests are rate-limited, cached, and logged
by the respective microservices.
"""

from fastapi import FastAPI
from app.database import engine, Base
from app.routers import users, tokens, athletes, countries, sports, events

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Olympic Games API",
    description="Token-based API for 120 years of Olympic history. v2 adds caching, rate limiting, logging, and a token shop.",
    version="2.0.0",
)

app.include_router(users.router)
app.include_router(tokens.router)
app.include_router(athletes.router)
app.include_router(countries.router)
app.include_router(sports.router)
app.include_router(events.router)


@app.get("/")
def root():
    return {"status": "ok", "version": "2.0.0"}
