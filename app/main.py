"""Olympic Games API — FastAPI application entry point.

Start the server with:
    uvicorn app.main:app --reload

Then load data (once) with:
    python load_data.py
"""

from fastapi import FastAPI
from app.database import engine, Base
from app.routers import users, tokens, athletes, countries, sports, events

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Olympic Games API",
    description=(
        "A token-based API for querying 120 years of Olympic history. "
        "Data endpoints require an X-User-Id header and cost 1 token each."
    ),
    version="1.0.0",
)

app.include_router(users.router)
app.include_router(tokens.router)
app.include_router(athletes.router)
app.include_router(countries.router)
app.include_router(sports.router)
app.include_router(events.router)


@app.get("/")
def root():
    """Health check — confirms the API is running."""
    return {"status": "ok", "message": "Olympic Games API is running"}
