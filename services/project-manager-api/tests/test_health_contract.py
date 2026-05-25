"""Test /health endpoint contract."""
import pytest
from app.main import app
from app.config import BRAIN_API_URL
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health_returns_ok():
    """/health must return api=ok without auth."""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["api"] == "ok"


def test_health_worker_disabled():
    """worker_enabled must be false."""
    resp = client.get("/health")
    data = resp.json()
    assert data["worker_enabled"] == False


def test_health_dry_run_true():
    """dry_run must be true."""
    resp = client.get("/health")
    data = resp.json()
    assert data["dry_run"] == True


def test_health_no_secrets():
    """/health response must not contain secret values."""
    resp = client.get("/health")
    text = resp.text.lower()
    assert "sk-" not in text
    assert "ghp_" not in text
    assert "token" not in text or text.count("token") == text.count("_token") == 0
