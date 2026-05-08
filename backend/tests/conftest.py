"""NeXifyAI Backend Test Fixtures."""
import pytest
from fastapi.testclient import TestClient
from backend.main import app


@pytest.fixture
def client():
    """FastAPI TestClient for API testing."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Test authentication headers."""
    return {"Authorization": "Bearer test-token"}
