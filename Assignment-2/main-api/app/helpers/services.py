"""HTTP client helpers for talking to the other services.

All calls use a short timeout and fail silently where possible,
so a slow/down service doesn't take out the whole API.
"""

import os
import requests

CACHE_URL = os.getenv("CACHE_URL", "http://cache:8001")
RATE_LIMITER_URL = os.getenv("RATE_LIMITER_URL", "http://rate-limiter:8002")
LOGGER_URL = os.getenv("LOGGER_URL", "http://logger:8003")
TOKEN_SHOP_URL = os.getenv("TOKEN_SHOP_URL", "http://token-shop:8004")

_TIMEOUT = 2


def cache_get(key: str) -> dict:
    try:
        r = requests.get(f"{CACHE_URL}/cache", params={"key": key}, timeout=_TIMEOUT)
        return r.json()
    except Exception:
        return {"hit": False, "data": None}


def cache_set(key: str, data) -> None:
    try:
        requests.post(f"{CACHE_URL}/cache", json={"key": key, "data": data}, timeout=_TIMEOUT)
    except Exception:
        pass


def rate_limit_check(user_id: str, username: str) -> float:
    """Record a request for the user and return how many seconds to sleep."""
    try:
        requests.post(
            f"{RATE_LIMITER_URL}/{user_id}",
            json={"username": username},
            timeout=_TIMEOUT,
        )
        r = requests.get(f"{RATE_LIMITER_URL}/{user_id}", timeout=_TIMEOUT)
        return float(r.json().get("delay", 0))
    except Exception:
        return 0.0


def log_request(username: str, endpoint: str, tokens: int) -> None:
    try:
        requests.post(
            f"{LOGGER_URL}/log",
            json={"username": username, "endpoint": endpoint, "tokens": tokens},
            timeout=_TIMEOUT,
        )
    except Exception:
        pass


def shop_verify_code(code: str):
    """Ask the token shop to redeem a code. Returns token count or None on failure."""
    try:
        r = requests.post(
            f"{TOKEN_SHOP_URL}/verify",
            json={"code": code},
            timeout=_TIMEOUT,
        )
        if r.status_code == 200:
            return r.json().get("tokens")
        return None
    except Exception:
        return None


def shop_get_price() -> dict:
    try:
        r = requests.get(f"{TOKEN_SHOP_URL}/price", timeout=_TIMEOUT)
        return r.json()
    except Exception:
        return {"error": "token shop unavailable"}


def shop_update_price(price: float, admin_key: str) -> dict:
    try:
        r = requests.put(
            f"{TOKEN_SHOP_URL}/price",
            json={"price": price},
            headers={"x-admin-key": admin_key},
            timeout=_TIMEOUT,
        )
        return r.json()
    except Exception:
        return {"error": "token shop unavailable"}
