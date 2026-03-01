import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from src.api_service.app import app


client = TestClient(app)


def test_dashboard_endpoint_returns_payload() -> None:
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    payload = response.json()
    assert "recommendations" in payload
    assert "market_context" in payload


def test_quote_endpoint_requires_ticker() -> None:
    response = client.get("/api/market/quote", params={"ticker": "AAPL"})
    assert response.status_code == 200
    assert response.json()["ticker"] == "AAPL"
