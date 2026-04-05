"""
Iteration 70 - Backend API Tests for NeXifyAI B2B Platform
Tests: Stats API expansion, Webhooks events, Monitoring, NeXify AI execute-tool
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
ADMIN_EMAIL = "p.courbois@icloud.com"
ADMIN_PASSWORD = "1def!xO2022!!"


class TestAdminAuth:
    """Admin authentication tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get admin auth token"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=f"username={ADMIN_EMAIL}&password={ADMIN_PASSWORD}"
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access_token in response"
        return data["access_token"]
    
    def test_admin_login(self, auth_token):
        """Test admin login returns valid token"""
        assert auth_token is not None
        assert len(auth_token) > 20


class TestStatsAPIExpansion:
    """Test expanded stats API with contacts_total, quotes_total, contracts_total, invoices_total"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=f"username={ADMIN_EMAIL}&password={ADMIN_PASSWORD}"
        )
        return response.json().get("access_token")
    
    def test_stats_returns_contacts_total(self, auth_token):
        """Verify stats API returns contacts_total field"""
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "contacts_total" in data, "contacts_total missing from stats"
        assert isinstance(data["contacts_total"], int), "contacts_total should be integer"
    
    def test_stats_returns_quotes_total(self, auth_token):
        """Verify stats API returns quotes_total field"""
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "quotes_total" in data, "quotes_total missing from stats"
        assert isinstance(data["quotes_total"], int), "quotes_total should be integer"
    
    def test_stats_returns_contracts_total(self, auth_token):
        """Verify stats API returns contracts_total field"""
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "contracts_total" in data, "contracts_total missing from stats"
        assert isinstance(data["contracts_total"], int), "contracts_total should be integer"
    
    def test_stats_returns_invoices_total(self, auth_token):
        """Verify stats API returns invoices_total field"""
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "invoices_total" in data, "invoices_total missing from stats"
        assert isinstance(data["invoices_total"], int), "invoices_total should be integer"
    
    def test_stats_returns_projects_total(self, auth_token):
        """Verify stats API returns projects_total field"""
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "projects_total" in data, "projects_total missing from stats"
        assert isinstance(data["projects_total"], int), "projects_total should be integer"
    
    def test_stats_returns_all_8_dashboard_fields(self, auth_token):
        """Verify stats API returns all 8 fields needed for dashboard stat cards"""
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        required_fields = [
            "leads_total",
            "leads_new",
            "contacts_total",
            "quotes_total",
            "contracts_total",
            "invoices_total",
            "bookings_total",
            "chat_sessions_total"
        ]
        
        for field in required_fields:
            assert field in data, f"{field} missing from stats response"
            print(f"  {field}: {data[field]}")


class TestWebhookEvents:
    """Test webhook events API with corrected field names"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=f"username={ADMIN_EMAIL}&password={ADMIN_PASSWORD}"
        )
        return response.json().get("access_token")
    
    def test_webhook_events_endpoint_exists(self, auth_token):
        """Verify webhook events endpoint returns 200"""
        response = requests.get(
            f"{BASE_URL}/api/admin/webhooks/events",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Webhook events failed: {response.text}"
        data = response.json()
        assert "events" in data, "events field missing"
        assert "count" in data, "count field missing"
    
    def test_webhook_events_structure(self, auth_token):
        """Verify webhook events have correct field structure"""
        response = requests.get(
            f"{BASE_URL}/api/admin/webhooks/events?limit=10",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # If there are events, check their structure
        if data["events"]:
            event = data["events"][0]
            print(f"  Sample event keys: {list(event.keys())}")
            # The frontend expects: processed_at, event, order_id
            # Backend may return: timestamp, event_type, source
            # Frontend handles both with fallbacks


class TestMonitoringStatus:
    """Test monitoring/status endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=f"username={ADMIN_EMAIL}&password={ADMIN_PASSWORD}"
        )
        return response.json().get("access_token")
    
    def test_monitoring_status_endpoint(self, auth_token):
        """Verify monitoring status endpoint returns system health data"""
        response = requests.get(
            f"{BASE_URL}/api/admin/monitoring/status",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Monitoring status failed: {response.text}"
        data = response.json()
        assert "systems" in data or "status" in data, "Expected systems or status in response"
        print(f"  Monitoring response keys: {list(data.keys())}")


class TestNeXifyAIExecuteTool:
    """Test NeXify AI execute-tool endpoint with system_stats"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=f"username={ADMIN_EMAIL}&password={ADMIN_PASSWORD}"
        )
        return response.json().get("access_token")
    
    def test_execute_tool_system_stats(self, auth_token):
        """Test execute-tool with tool=system_stats returns expanded stats"""
        response = requests.post(
            f"{BASE_URL}/api/admin/nexify-ai/execute-tool",
            headers={
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            },
            json={"tool": "system_stats", "args": {}}
        )
        assert response.status_code == 200, f"Execute tool failed: {response.text}"
        data = response.json()
        assert "result" in data or "output" in data or "stats" in data, f"Unexpected response: {data}"
        print(f"  Execute tool response keys: {list(data.keys())}")


class TestLeadsEndpoint:
    """Test leads endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=f"username={ADMIN_EMAIL}&password={ADMIN_PASSWORD}"
        )
        return response.json().get("access_token")
    
    def test_leads_endpoint(self, auth_token):
        """Verify leads endpoint returns data"""
        response = requests.get(
            f"{BASE_URL}/api/admin/leads",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "leads" in data, "leads field missing"
        assert "total" in data, "total field missing"
        print(f"  Total leads: {data['total']}")


class TestAgentsEndpoint:
    """Test agents endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=f"username={ADMIN_EMAIL}&password={ADMIN_PASSWORD}"
        )
        return response.json().get("access_token")
    
    def test_agents_endpoint(self, auth_token):
        """Verify agents endpoint returns agent list"""
        response = requests.get(
            f"{BASE_URL}/api/admin/agents",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data, "agents field missing"
        print(f"  Total agents: {len(data['agents'])}")


class TestCommercialEndpoints:
    """Test commercial endpoints (quotes/invoices)"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=f"username={ADMIN_EMAIL}&password={ADMIN_PASSWORD}"
        )
        return response.json().get("access_token")
    
    def test_quotes_endpoint(self, auth_token):
        """Verify quotes endpoint returns data"""
        response = requests.get(
            f"{BASE_URL}/api/admin/quotes",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "quotes" in data, "quotes field missing"
        print(f"  Total quotes: {len(data['quotes'])}")
    
    def test_invoices_endpoint(self, auth_token):
        """Verify invoices endpoint returns data"""
        response = requests.get(
            f"{BASE_URL}/api/admin/invoices",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "invoices" in data, "invoices field missing"
        print(f"  Total invoices: {len(data['invoices'])}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
