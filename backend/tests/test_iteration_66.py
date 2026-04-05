"""
Iteration 66 - Comprehensive Audit Tests
Testing: Color changes, NeXify AI tools, API endpoints, legal pages
"""
import os
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://contract-os.preview.emergentagent.com').rstrip('/')
ADMIN_EMAIL = "p.courbois@icloud.com"
ADMIN_PASSWORD = "1def!xO2022!!"


@pytest.fixture(scope="module")
def admin_token():
    """Get admin authentication token."""
    resp = requests.post(
        f"{BASE_URL}/api/admin/login",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=f"username={ADMIN_EMAIL}&password={ADMIN_PASSWORD}"
    )
    assert resp.status_code == 200, f"Admin login failed: {resp.text}"
    data = resp.json()
    assert "access_token" in data
    return data["access_token"]


@pytest.fixture(scope="module")
def auth_headers(admin_token):
    """Auth headers for admin requests."""
    return {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }


# ══════════════════════════════════════════════════════════════
# EXTERNAL API HEALTH
# ══════════════════════════════════════════════════════════════
class TestExternalApiHealth:
    """Test external API v1 health endpoint."""
    
    def test_api_v1_health_returns_operational(self):
        """GET /api/v1/health returns operational status."""
        resp = requests.get(f"{BASE_URL}/api/v1/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("status") == "operational"
        assert "version" in data
        assert "timestamp" in data


# ══════════════════════════════════════════════════════════════
# LEGAL PAGES
# ══════════════════════════════════════════════════════════════
class TestLegalPages:
    """Test legal pages return 200."""
    
    def test_impressum_de(self):
        """GET /de/impressum returns 200."""
        resp = requests.get(f"{BASE_URL}/de/impressum", allow_redirects=True)
        assert resp.status_code == 200
    
    def test_impressum_nl(self):
        """GET /nl/impressum returns 200."""
        resp = requests.get(f"{BASE_URL}/nl/impressum", allow_redirects=True)
        assert resp.status_code == 200
    
    def test_imprint_en(self):
        """GET /en/imprint returns 200."""
        resp = requests.get(f"{BASE_URL}/en/imprint", allow_redirects=True)
        assert resp.status_code == 200


# ══════════════════════════════════════════════════════════════
# CUSTOMER PORTAL LOGIN PAGE
# ══════════════════════════════════════════════════════════════
class TestCustomerPortal:
    """Test customer portal login page."""
    
    def test_login_page_renders(self):
        """GET /login returns 200."""
        resp = requests.get(f"{BASE_URL}/login", allow_redirects=True)
        assert resp.status_code == 200


# ══════════════════════════════════════════════════════════════
# API KEYS ENDPOINT
# ══════════════════════════════════════════════════════════════
class TestApiKeys:
    """Test API keys admin endpoint."""
    
    def test_list_api_keys(self, auth_headers):
        """GET /api/admin/api-keys returns keys list."""
        resp = requests.get(f"{BASE_URL}/api/admin/api-keys", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "keys" in data


# ══════════════════════════════════════════════════════════════
# NEXIFY AI TOOLS API
# ══════════════════════════════════════════════════════════════
class TestNeXifyAITools:
    """Test NeXify AI tools endpoints."""
    
    def test_list_tools_returns_18_plus(self, auth_headers):
        """GET /api/admin/nexify-ai/tools returns 18+ tools."""
        resp = requests.get(f"{BASE_URL}/api/admin/nexify-ai/tools", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "tools" in data
        tools = data["tools"]
        assert len(tools) >= 18, f"Expected 18+ tools, got {len(tools)}: {list(tools.keys())}"
        
        # Verify key tools are present
        expected_tools = [
            "list_contacts", "list_leads", "list_quotes", "list_contracts",
            "list_projects", "list_invoices", "send_email", "search_brain",
            "db_query", "audit_log", "worker_status", "timeline", "list_api_keys", "web_search"
        ]
        for tool in expected_tools:
            assert tool in tools, f"Missing tool: {tool}"
    
    def test_execute_tool_system_stats(self, auth_headers):
        """POST /api/admin/nexify-ai/execute-tool with tool=system_stats returns stats."""
        resp = requests.post(
            f"{BASE_URL}/api/admin/nexify-ai/execute-tool",
            headers=auth_headers,
            json={"tool": "system_stats", "params": {}}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "result" in data
        assert data.get("tool") == "system_stats"
        result = data["result"]
        # Verify stats fields
        assert "contacts" in result
        assert "leads" in result
        assert "quotes" in result
        assert "contracts" in result
        assert "projects" in result
        assert "invoices" in result
    
    def test_execute_tool_list_contacts(self, auth_headers):
        """POST /api/admin/nexify-ai/execute-tool with tool=list_contacts returns contacts."""
        resp = requests.post(
            f"{BASE_URL}/api/admin/nexify-ai/execute-tool",
            headers=auth_headers,
            json={"tool": "list_contacts", "params": {"limit": 5}}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "result" in data
        assert data.get("tool") == "list_contacts"
        assert "count" in data
    
    def test_execute_tool_search_brain(self, auth_headers):
        """POST /api/admin/nexify-ai/execute-tool with tool=search_brain searches mem0."""
        resp = requests.post(
            f"{BASE_URL}/api/admin/nexify-ai/execute-tool",
            headers=auth_headers,
            json={"tool": "search_brain", "params": {"query": "test"}}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("tool") == "search_brain"
        # Result may be empty if no memories match, but should have result key
        assert "result" in data
    
    def test_execute_tool_db_query_leads(self, auth_headers):
        """POST /api/admin/nexify-ai/execute-tool with tool=db_query collection=leads returns leads."""
        resp = requests.post(
            f"{BASE_URL}/api/admin/nexify-ai/execute-tool",
            headers=auth_headers,
            json={"tool": "db_query", "params": {"collection": "leads", "limit": 5}}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("tool") == "db_query"
        assert data.get("collection") == "leads"
        assert "result" in data
        assert "count" in data


# ══════════════════════════════════════════════════════════════
# NEXIFY AI STATUS
# ══════════════════════════════════════════════════════════════
class TestNeXifyAIStatus:
    """Test NeXify AI status endpoint."""
    
    def test_nexify_ai_status(self, auth_headers):
        """GET /api/admin/nexify-ai/status returns configuration."""
        resp = requests.get(f"{BASE_URL}/api/admin/nexify-ai/status", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "arcee" in data
        assert "mem0" in data
        assert "stats" in data
        assert data["arcee"].get("configured") == True
        assert data["mem0"].get("configured") == True


# ══════════════════════════════════════════════════════════════
# NEXIFY AI CONVERSATIONS
# ══════════════════════════════════════════════════════════════
class TestNeXifyAIConversations:
    """Test NeXify AI conversations endpoint."""
    
    def test_list_conversations(self, auth_headers):
        """GET /api/admin/nexify-ai/conversations returns conversations list."""
        resp = requests.get(f"{BASE_URL}/api/admin/nexify-ai/conversations", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "conversations" in data


# ══════════════════════════════════════════════════════════════
# ADMIN STATS
# ══════════════════════════════════════════════════════════════
class TestAdminStats:
    """Test admin stats endpoint."""
    
    def test_admin_stats(self, auth_headers):
        """GET /api/admin/stats returns dashboard stats."""
        resp = requests.get(f"{BASE_URL}/api/admin/stats", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "leads_total" in data or "leads_new" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
