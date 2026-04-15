"""
NeXifyAI — OpenRouter Migration Tests (Iteration 81)
Tests for DeepSeek → OpenRouter (minimax/minimax-m2.7) migration.
All endpoints should return 'openrouter' instead of 'deepseek'.
"""
import os
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "p.courbois@icloud.com"
ADMIN_PASSWORD = "1def!xO2022!!"


@pytest.fixture(scope="module")
def auth_token():
    """Get admin authentication token."""
    response = requests.post(
        f"{BASE_URL}/api/admin/login",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    assert "access_token" in data, "No access_token in response"
    return data["access_token"]


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Get headers with auth token."""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }


class TestHealthEndpoint:
    """Test GET /api/health returns 'openrouter' service status."""
    
    def test_health_returns_openrouter_not_deepseek(self):
        """Health check should have 'openrouter' key, not 'deepseek'."""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        
        # Should have 'openrouter' service
        assert "services" in data
        assert "openrouter" in data["services"], "Missing 'openrouter' in services"
        assert data["services"]["openrouter"]["status"] == "ok"
        assert data["services"]["openrouter"]["configured"] == True
        
        # Should NOT have 'deepseek' service
        assert "deepseek" not in data["services"], "Found 'deepseek' in services - should be 'openrouter'"
        
    def test_health_overall_status_healthy(self):
        """Overall health status should be 'healthy'."""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestNexifyAIStatus:
    """Test GET /api/admin/nexify-ai/status returns OpenRouter config."""
    
    def test_nexify_ai_status_master_llm_openrouter(self, auth_headers):
        """master_llm should be 'openrouter', not 'deepseek'."""
        response = requests.get(
            f"{BASE_URL}/api/admin/nexify-ai/status",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # master_llm should be 'openrouter'
        assert data["master_llm"] == "openrouter", f"Expected master_llm='openrouter', got '{data.get('master_llm')}'"
        
    def test_nexify_ai_status_openrouter_configured(self, auth_headers):
        """OpenRouter should be configured and connected."""
        response = requests.get(
            f"{BASE_URL}/api/admin/nexify-ai/status",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # OpenRouter config
        assert "openrouter" in data, "Missing 'openrouter' key in status"
        assert data["openrouter"]["configured"] == True
        assert data["openrouter"]["connected"] == True
        assert data["openrouter"]["model"] == "minimax/minimax-m2.7"
        assert data["openrouter"]["primary"] == True
        
    def test_nexify_ai_status_no_deepseek_key(self, auth_headers):
        """Should NOT have 'deepseek' key in status response."""
        response = requests.get(
            f"{BASE_URL}/api/admin/nexify-ai/status",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should NOT have 'deepseek' key
        assert "deepseek" not in data, "Found 'deepseek' key in status - should be 'openrouter'"


class TestOracleHealth:
    """Test GET /api/admin/oracle/health returns 'openrouter' key."""
    
    def test_oracle_health_has_openrouter(self, auth_headers):
        """Oracle health should have 'openrouter' key, not 'deepseek'."""
        response = requests.get(
            f"{BASE_URL}/api/admin/oracle/health",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should have 'openrouter' key
        assert "openrouter" in data, "Missing 'openrouter' key in oracle health"
        assert data["openrouter"]["configured"] == True
        assert data["openrouter"]["connected"] == True
        assert data["openrouter"]["model"] == "minimax/minimax-m2.7"
        
        # Should NOT have 'deepseek' key
        assert "deepseek" not in data, "Found 'deepseek' key in oracle health - should be 'openrouter'"


class TestTriggerRun:
    """Test POST /api/admin/trigger/run uses OpenRouter."""
    
    def test_trigger_run_deep_research_success(self, auth_headers):
        """Trigger deep-research task should succeed with OpenRouter."""
        response = requests.post(
            f"{BASE_URL}/api/admin/trigger/run",
            headers=auth_headers,
            json={
                "task_id": "deep-research",
                "payload": {
                    "initialQuery": "test OpenRouter migration",
                    "depth": 1,
                    "breadth": 1,
                    "language": "de"
                }
            },
            timeout=120  # AI tasks can take time
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should succeed
        assert data["success"] == True
        assert "run_id" in data
        assert data["task_id"] == "deep-research"
        
        # Should use OpenRouter model
        assert data.get("model") == "minimax/minimax-m2.7", f"Expected model='minimax/minimax-m2.7', got '{data.get('model')}'"
        
        # Result should not contain 'deepseek' (except in content about migration)
        # Note: The result content may mention DeepSeek as a topic, but the model used should be OpenRouter


class TestTriggerStatus:
    """Test GET /api/admin/trigger/status."""
    
    def test_trigger_status_returns_tasks(self, auth_headers):
        """Trigger status should return available tasks."""
        response = requests.get(
            f"{BASE_URL}/api/admin/trigger/status",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should have tasks_available
        assert "tasks_available" in data
        assert data["tasks_available"] >= 6  # At least 6 tasks


class TestNoDeepSeekInResponses:
    """Verify no API response body contains 'deepseek' or 'DeepSeek' as a service name."""
    
    def test_health_no_deepseek_string(self):
        """Health response should not contain 'deepseek' as service."""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        text = response.text.lower()
        
        # Check for deepseek as a service key (not as content)
        data = response.json()
        services_str = str(data.get("services", {})).lower()
        assert "deepseek" not in services_str, "Found 'deepseek' in services"
        
    def test_nexify_ai_status_no_deepseek_service(self, auth_headers):
        """NeXify AI status should not have deepseek as a service."""
        response = requests.get(
            f"{BASE_URL}/api/admin/nexify-ai/status",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check top-level keys
        top_keys = list(data.keys())
        assert "deepseek" not in top_keys, f"Found 'deepseek' in top-level keys: {top_keys}"
        
    def test_oracle_health_no_deepseek_service(self, auth_headers):
        """Oracle health should not have deepseek as a service."""
        response = requests.get(
            f"{BASE_URL}/api/admin/oracle/health",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check top-level keys
        top_keys = list(data.keys())
        assert "deepseek" not in top_keys, f"Found 'deepseek' in top-level keys: {top_keys}"


class TestLLMProviderStatus:
    """Test LLM provider configuration via admin endpoints."""
    
    def test_admin_stats_loads(self, auth_headers):
        """Admin stats endpoint should load successfully."""
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "leads_total" in data or "contacts_total" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
