# NeXifyAI Backend Tests

## Erster Test — Health Endpoint
def test_health_check(client):
    """Verify /api/health returns 200 and correct structure."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ["healthy", "degraded", "down"]

## Teststruktur

- `conftest.py` — Shared fixtures (FastAPI TestClient, DB session)
- `test_api/` — API endpoint tests
- `test_services/` — Business logic tests
- `test_models/` — Data model tests
- `test_middleware/` — Middleware tests (auth, rate limiting, CSP)
