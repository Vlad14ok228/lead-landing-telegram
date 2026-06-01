"""
Tests for the FastAPI lead collection backend.

Strategy:
- Set required env vars before importing the app so pydantic-settings
  does not raise a ValidationError at collection time.
- Patch `router.send_lead_to_telegram` (the name as imported in router.py)
  so the Telegram HTTP call is never made.
- Use FastAPI's synchronous TestClient for simplicity (no event-loop
  fixture boilerplate needed).
"""

import os

# ---------------------------------------------------------------------------
# Provide dummy credentials BEFORE any app module is imported so that
# pydantic-settings can build Settings() without a real .env file.
# ---------------------------------------------------------------------------
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "test-token-12345")
os.environ.setdefault("TELEGRAM_CHAT_ID", "-100000000")

import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from fastapi.testclient import TestClient

# Import after env vars are set
from main import app  # noqa: E402  (import not at top intentional)

client = TestClient(app)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

VALID_PAYLOAD = {"name": "Іван Петренко", "phone": "+380 67 123-45-67"}


def _post(payload: dict):
    return client.post("/leads", json=payload)


# ---------------------------------------------------------------------------
# Test 1 – valid name + phone → 200 {"ok": true}
# ---------------------------------------------------------------------------

def test_valid_lead_returns_200():
    with patch("router.send_lead_to_telegram", new_callable=AsyncMock) as mock_tg:
        mock_tg.return_value = None
        response = _post(VALID_PAYLOAD)

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    mock_tg.assert_awaited_once()


# ---------------------------------------------------------------------------
# Test 2 – name too short (1 char) → 422 Unprocessable Entity
# ---------------------------------------------------------------------------

def test_name_too_short_returns_422():
    payload = {**VALID_PAYLOAD, "name": "А"}
    response = _post(payload)
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Test 3 – invalid phone → 422 Unprocessable Entity
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("bad_phone", [
    "abc",           # non-digits
    "123",           # too short (< 7 significant chars)
    "++1234567",     # double plus
    "",              # empty
])
def test_invalid_phone_returns_422(bad_phone: str):
    payload = {**VALID_PAYLOAD, "phone": bad_phone}
    response = _post(payload)
    assert response.status_code == 422, f"Expected 422 for phone={bad_phone!r}"


# ---------------------------------------------------------------------------
# Test 4 – Telegram call fails → 502 with {"ok": false}
# ---------------------------------------------------------------------------

def test_telegram_failure_returns_502():
    with patch("router.send_lead_to_telegram", new_callable=AsyncMock) as mock_tg:
        mock_tg.side_effect = HTTPException(
            status_code=502,
            detail={"ok": False, "message": "Не вдалося надіслати повідомлення. Спробуйте пізніше."},
        )
        response = _post(VALID_PAYLOAD)

    assert response.status_code == 502
    body = response.json()
    # FastAPI serialises HTTPException detail into {"detail": ...}
    detail = body.get("detail", body)
    assert detail["ok"] is False


# ---------------------------------------------------------------------------
# Test 5 – missing required fields → 422 Unprocessable Entity
# ---------------------------------------------------------------------------

def test_missing_name_returns_422():
    response = _post({"phone": "+380671234567"})
    assert response.status_code == 422


def test_missing_phone_returns_422():
    response = _post({"name": "Іван Петренко"})
    assert response.status_code == 422


def test_empty_body_returns_422():
    response = _post({})
    assert response.status_code == 422
