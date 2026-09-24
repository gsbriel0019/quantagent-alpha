import pytest
from fastapi.testclient import TestClient
from app.api import app

client = TestClient(app)


def test_api_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "author" in data
    assert data["author"] == "Gabriel Proaño"


def test_api_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "QuantFactorAgent" in data["active_agents"]


def test_api_macro():
    response = client.get("/macro/regime")
    assert response.status_code == 200
    data = response.json()
    assert "fed_funds_rate" in data
    assert "vix_level" in data


def test_api_analyze():
    response = client.get("/analyze/NVDA?period=6mo")
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "NVDA"
    assert "conviction_rating" in data
    assert "quantitative_factors" in data


def test_api_memo():
    response = client.get("/thesis/memo/NVDA?period=6mo")
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "NVDA"
    assert "memo_markdown" in data
    assert "# 🏛️ Institutional Investment Memorandum" in data["memo_markdown"]
