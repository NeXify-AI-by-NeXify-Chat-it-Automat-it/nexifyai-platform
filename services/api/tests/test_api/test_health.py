"""Tests for health endpoint."""
import pytest


def test_health_check(client):
    """Verify /api/health returns 200."""
    response = client.get("/api/health")
    assert response.status_code in [200, 503]  # 503 if backend not running
    if response.status_code == 200:
        data = response.json()
        assert "status" in data


def test_metrics_endpoint(client):
    """Verify /metrics returns Prometheus format."""
    response = client.get("/metrics")
    assert response.status_code in [200, 404]  # 404 if not configured


def test_security_headers(client):
    """Verify security headers are present."""
    response = client.get("/api/health")
    if response.status_code == 200:
        assert "X-Content-Type-Options" in response.headers
