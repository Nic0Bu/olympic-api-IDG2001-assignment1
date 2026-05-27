"""Cache service.

Stores GET responses in memory with a 1-minute TTL.
Expired entries are cleaned up before each lookup.

Endpoints:
    GET  /cache?key=<k>  — check cache
    POST /cache          — store a value
    GET  /log            — hit/miss stats
"""

from datetime import datetime, timedelta
from typing import Any
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Cache")

# { key: {"data": ..., "timestamp": iso-string} }
_store: dict = {}
_hits = 0
_misses = 0

TTL_SECONDS = 60


class CacheSet(BaseModel):
    key: str
    data: Any


def _clean_expired():
    cutoff = datetime.now() - timedelta(seconds=TTL_SECONDS)
    expired = [k for k, v in _store.items() if datetime.fromisoformat(v["timestamp"]) < cutoff]
    for k in expired:
        del _store[k]


@app.get("/cache")
def get_cache(key: str):
    global _hits, _misses
    _clean_expired()

    if key in _store:
        _hits += 1
        return {"hit": True, "data": _store[key]["data"]}

    _misses += 1
    return {"hit": False, "data": None}


@app.post("/cache")
def set_cache(body: CacheSet):
    _store[body.key] = {
        "data": body.data,
        "timestamp": datetime.now().isoformat(),
    }
    return {"ok": True}


@app.get("/log")
def cache_log():
    """Returns total cache hits and misses since startup."""
    return {"hits": _hits, "misses": _misses}
