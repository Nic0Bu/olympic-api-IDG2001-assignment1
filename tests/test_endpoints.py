"""API endpoint tests. Runs against a live server.

Usage:
    1. Start the API:  uvicorn app.main:app --reload
    2. Wait a few seconds for it to be ready
    3. Run as a script:  python tests/test_endpoints.py
       or via pytest:    pytest tests/test_endpoints.py

The server is expected at http://localhost:8000 by default.
Set the BASE_URL environment variable to override.
"""

import os
import sys
import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000/v1")
TEST_EMAIL = "endpoint_test_user@example.com"
TEST_PASSWORD = "testpassword123"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_or_create_user() -> dict:
    """Return an existing test user or create a fresh one."""
    resp = requests.post(
        f"{BASE_URL}/user",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
    )
    if resp.status_code == 201:
        return resp.json()
    # Already exists — find them in the user list
    all_users = requests.get(f"{BASE_URL}/user").json()
    return next(u for u in all_users if u["email"] == TEST_EMAIL)


def _delete_test_user(user_id: str) -> None:
    """Delete the test user if it exists."""
    requests.delete(f"{BASE_URL}/user/{user_id}")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_create_user():
    """POST /user creates a user with 100 starting tokens."""
    # Ensure clean state
    all_users = requests.get(f"{BASE_URL}/user").json()
    for u in all_users:
        if u["email"] == TEST_EMAIL:
            _delete_test_user(u["id"])

    resp = requests.post(
        f"{BASE_URL}/user",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
    )
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["email"] == TEST_EMAIL
    assert data["tokens"] == 100
    _delete_test_user(data["id"])


def test_duplicate_email_rejected():
    """POST /user with an already-registered email returns 409."""
    user = _get_or_create_user()
    resp = requests.post(
        f"{BASE_URL}/user",
        json={"email": TEST_EMAIL, "password": "another"},
    )
    assert resp.status_code == 409, f"Expected 409, got {resp.status_code}"
    _delete_test_user(user["id"])


def test_add_tokens():
    """POST /tokens increases the user's token count by the given amount."""
    user = _get_or_create_user()
    # Set a known baseline
    requests.patch(f"{BASE_URL}/user/{user['id']}", json={"tokens": 50})
    resp = requests.post(
        f"{BASE_URL}/tokens",
        json={"user_id": user["id"], "amount": 30},
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["tokens"] == 80, (
        f"Expected 80 tokens, got {resp.json()['tokens']}"
    )
    _delete_test_user(user["id"])


def test_tokens_consumed_by_data_endpoint():
    """Calling a data endpoint deducts exactly one token from the user."""
    user = _get_or_create_user()
    requests.patch(f"{BASE_URL}/user/{user['id']}", json={"tokens": 10})

    before = requests.get(f"{BASE_URL}/user/{user['id']}").json()["tokens"]

    # Call the country endpoint — may 404 on data but still costs a token
    requests.get(
        f"{BASE_URL}/country/USA",
        headers={"X-User-Id": user["id"]},
    )

    after = requests.get(f"{BASE_URL}/user/{user['id']}").json()["tokens"]
    assert after == before - 1, (
        f"Expected {before - 1} tokens after call, got {after}"
    )
    _delete_test_user(user["id"])


def test_zero_tokens_returns_402():
    """A user with 0 tokens receives a 402 response from data endpoints."""
    user = _get_or_create_user()
    requests.patch(f"{BASE_URL}/user/{user['id']}", json={"tokens": 0})

    resp = requests.get(
        f"{BASE_URL}/country/NOR",
        headers={"X-User-Id": user["id"]},
    )
    assert resp.status_code == 402, f"Expected 402, got {resp.status_code}"
    _delete_test_user(user["id"])


def test_invalid_user_id_returns_401():
    """An unknown X-User-Id header returns 401."""
    resp = requests.get(
        f"{BASE_URL}/country/NOR",
        headers={"X-User-Id": "00000000-0000-0000-0000-000000000000"},
    )
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"


def test_add_tokens_negative_amount_rejected():
    """POST /tokens with a non-positive amount returns 400."""
    user = _get_or_create_user()
    resp = requests.post(
        f"{BASE_URL}/tokens",
        json={"user_id": user["id"], "amount": -5},
    )
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}"
    _delete_test_user(user["id"])


# ---------------------------------------------------------------------------
# Script runner
# ---------------------------------------------------------------------------

def _run_all() -> bool:
    """Run all test functions and print a summary. Returns True if all pass."""
    tests = [
        test_create_user,
        test_duplicate_email_rejected,
        test_add_tokens,
        test_tokens_consumed_by_data_endpoint,
        test_zero_tokens_returns_402,
        test_invalid_user_id_returns_401,
        test_add_tokens_negative_amount_rejected,
    ]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            print(f"  PASS  {test.__name__}")
            passed += 1
        except Exception as exc:
            print(f"  FAIL  {test.__name__}: {exc}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    print(f"Running endpoint tests against {BASE_URL}\n")
    success = _run_all()
    sys.exit(0 if success else 1)
