"""Rate limiter service.

Tracks how many requests each user has made in the last 10 seconds.
If they go over 10, it returns a delay they should wait before responding.

Delay formula: delay = (requests_over_limit) / 10
e.g. 13 requests -> r=3, delay=0.3 seconds

Endpoints:
    POST /<user-id>  — register a new request for a user
    GET  /<user-id>  — get request count + delay for a user
"""

from datetime import datetime, timedelta
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Rate Limiter")

_data: dict = {}

WINDOW_SECONDS = 10
LIMIT = 10


class RequestBody(BaseModel):
    username: str


def _get_recent(user_id: str) -> list:
    """Return only timestamps within the last WINDOW_SECONDS, cleaning old ones."""
    if user_id not in _data:
        _data[user_id] = []
    cutoff = datetime.now() - timedelta(seconds=WINDOW_SECONDS)
    _data[user_id] = [t for t in _data[user_id] if datetime.fromisoformat(t) > cutoff]
    return _data[user_id]


@app.post("/{user_id}")
def add_request(user_id: str, body: RequestBody):
    """Log a new request for this user."""
    recent = _get_recent(user_id)
    recent.append(datetime.now().isoformat())
    return {"requests": len(recent)}


@app.get("/{user_id}")
def get_status(user_id: str):
    """Return how many requests the user made recently and how long to delay them."""
    recent = _get_recent(user_id)
    count = len(recent)
    delay = 0.0
    if count > LIMIT:
        r = count - LIMIT
        delay = r / 10
    return {"requests": count, "delay": delay}
