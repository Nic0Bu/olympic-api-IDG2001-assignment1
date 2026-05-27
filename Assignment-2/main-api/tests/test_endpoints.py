"""API endpoint tests — runs against a live server.

Usage:
    1. Start the stack:  docker compose up
    2. Run:              python tests/test_endpoints.py
       or via pytest:    pytest tests/test_endpoints.py

Set BASE_URL env var to override the default (http://localhost:8000/v2).
Set TOKEN_SHOP_URL env var to override token shop URL (http://localhost:8004).
"""

import os
import sys
import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000/v2")
TOKEN_SHOP_URL = os.getenv("TOKEN_SHOP_URL", "http://localhost:8004")

TEST_EMAIL = "endpoint_test_user@example.com"
TEST_PASSWORD = "testpass123"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_or_create_user() -> dict:
    resp = requests.post(
        f"{BASE_URL}/user",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
    )
    if resp.status_code == 201:
        return resp.json()
    all_users = requests.get(f"{BASE_URL}/user").json()
    return next(u for u in all_users if u["email"] == TEST_EMAIL)


def _delete_user(user_id: str) -> None:
    requests.delete(f"{BASE_URL}/user/{user_id}")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_create_user():
    """POST /v2/user creates a user with 100 starting tokens."""
    all_users = requests.get(f"{BASE_URL}/user").json()
    for u in all_users:
        if u["email"] == TEST_EMAIL:
            _delete_user(u["id"])

    resp = requests.post(
        f"{BASE_URL}/user",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
    )
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["email"] == TEST_EMAIL
    assert data["tokens"] == 100
    _delete_user(data["id"])


def test_duplicate_email_rejected():
    """POST /v2/user with a taken email returns 409."""
    user = _get_or_create_user()
    resp = requests.post(
        f"{BASE_URL}/user",
        json={"email": TEST_EMAIL, "password": "other"},
    )
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}"
    _delete_user(user["id"])


def test_token_consumed_by_data_endpoint():
    """Calling a data endpoint costs exactly 1 token."""
    user = _get_or_create_user()
    requests.patch(f"{BASE_URL}/user/{user['id']}", json={"tokens": 10})

    before = requests.get(f"{BASE_URL}/user/{user['id']}").json()["tokens"]
    requests.get(f"{BASE_URL}/country/USA", headers={"X-User-Id": user["id"]})
    after = requests.get(f"{BASE_URL}/user/{user['id']}").json()["tokens"]

    assert after == before - 1, f"Expected {before - 1} tokens, got {after}"
    _delete_user(user["id"])


def test_zero_tokens_returns_402():
    """A user with 0 tokens gets a 402 response."""
    user = _get_or_create_user()
    requests.patch(f"{BASE_URL}/user/{user['id']}", json={"tokens": 0})

    resp = requests.get(
        f"{BASE_URL}/country/NOR",
        headers={"X-User-Id": user["id"]},
    )
    assert resp.status_code == 402, f"Expected 402, got {resp.status_code}"
    _delete_user(user["id"])


def test_invalid_user_id_returns_401():
    """An unknown X-User-Id returns 401."""
    resp = requests.get(
        f"{BASE_URL}/country/NOR",
        headers={"X-User-Id": "00000000-0000-0000-0000-000000000000"},
    )
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"


def test_token_shop_buy_and_redeem():
    """Full token shop flow: buy → get code → redeem → tokens added."""
    user = _get_or_create_user()
    requests.patch(f"{BASE_URL}/user/{user['id']}", json={"tokens": 0})

    # buy from the shop (10 money, price is 10 tokens/money = 100 tokens)
    buy_resp = requests.post(
        f"{TOKEN_SHOP_URL}/buy",
        json={"username": TEST_EMAIL, "password": TEST_PASSWORD, "money": 1},
    )
    assert buy_resp.status_code == 200, f"Buy failed: {buy_resp.text}"
    code = buy_resp.json()["secret"]

    # redeem at main API
    redeem_resp = requests.post(
        f"{BASE_URL}/tokens",
        json={"user_id": user["id"], "code": code},
    )
    assert redeem_resp.status_code == 200, f"Redeem failed: {redeem_resp.text}"
    assert redeem_resp.json()["tokens"] > 0

    _delete_user(user["id"])


def test_code_cannot_be_reused():
    """A code that's already been redeemed returns 400."""
    user = _get_or_create_user()

    buy_resp = requests.post(
        f"{TOKEN_SHOP_URL}/buy",
        json={"username": TEST_EMAIL, "password": TEST_PASSWORD, "money": 1},
    )
    code = buy_resp.json()["secret"]

    requests.post(f"{BASE_URL}/tokens", json={"user_id": user["id"], "code": code})
    second = requests.post(f"{BASE_URL}/tokens", json={"user_id": user["id"], "code": code})

    assert second.status_code == 400, f"Expected 400 on reuse, got {second.status_code}"
    _delete_user(user["id"])


def test_invalid_code_returns_400():
    """A made-up code returns 400."""
    user = _get_or_create_user()
    resp = requests.post(
        f"{BASE_URL}/tokens",
        json={"user_id": user["id"], "code": "thisisnotavalidcode"},
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}"
    _delete_user(user["id"])


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def _run_all() -> bool:
    tests = [
        test_create_user,
        test_duplicate_email_rejected,
        test_token_consumed_by_data_endpoint,
        test_zero_tokens_returns_402,
        test_invalid_user_id_returns_401,
        test_token_shop_buy_and_redeem,
        test_code_cannot_be_reused,
        test_invalid_code_returns_400,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"  FAIL  {t.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    print(f"Running tests against {BASE_URL}\n")
    ok = _run_all()
    sys.exit(0 if ok else 1)
