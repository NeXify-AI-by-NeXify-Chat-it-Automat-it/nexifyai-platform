"""
NeXifyAI External API v1 Tests - Iteration 64
Tests for API-Key-based authentication and all /api/v1/ endpoints.
"""
import pytest
import requests
import os
import time
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://contract-os.preview.emergentagent.com').rstrip('/')

# Test credentials
ADMIN_EMAIL = "p.courbois@icloud.com"
ADMIN_PASSWORD = "1def!xO2022!!"
EXISTING_API_KEY = "nxa_live_aaeef1d1f40df3f43537a153f83c6a65999a3e438e6137dd"


class TestApiV1Health:
    """Test /api/v1/health endpoint - no auth required"""
    
    def test_health_returns_200(self):
        """GET /api/v1/health returns 200 with status=operational"""
        response = requests.get(f"{BASE_URL}/api/v1/health")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("status") == "operational", f"Expected status=operational, got {data}"
        assert "version" in data
        assert "timestamp" in data
        print(f"✓ Health check passed: {data}")


class TestApiV1Docs:
    """Test /api/v1/docs endpoint - no auth required"""
    
    def test_docs_returns_full_documentation(self):
        """GET /api/v1/docs returns full documentation JSON"""
        response = requests.get(f"{BASE_URL}/api/v1/docs")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify structure
        assert "name" in data, "Missing 'name' in docs"
        assert "version" in data, "Missing 'version' in docs"
        assert "base_url" in data, "Missing 'base_url' in docs"
        assert "authentication" in data, "Missing 'authentication' in docs"
        assert "endpoints" in data, "Missing 'endpoints' in docs"
        assert "scopes" in data, "Missing 'scopes' in docs"
        
        # Verify authentication info
        auth = data["authentication"]
        assert auth.get("type") == "API Key", f"Expected API Key auth type, got {auth.get('type')}"
        assert auth.get("header") == "X-API-Key", f"Expected X-API-Key header, got {auth.get('header')}"
        
        # Verify endpoints exist
        endpoints = data["endpoints"]
        assert "contacts" in endpoints, "Missing contacts endpoints"
        assert "leads" in endpoints, "Missing leads endpoints"
        assert "quotes" in endpoints, "Missing quotes endpoints"
        assert "contracts" in endpoints, "Missing contracts endpoints"
        assert "projects" in endpoints, "Missing projects endpoints"
        assert "invoices" in endpoints, "Missing invoices endpoints"
        assert "stats" in endpoints, "Missing stats endpoint"
        assert "webhooks" in endpoints, "Missing webhooks endpoints"
        
        print(f"✓ Docs endpoint returned full documentation with {len(endpoints)} endpoint groups")


class TestApiV1Authentication:
    """Test API Key authentication"""
    
    def test_missing_api_key_returns_401(self):
        """Requests without X-API-Key header return 401"""
        response = requests.get(f"{BASE_URL}/api/v1/contacts")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        data = response.json()
        assert "detail" in data
        print(f"✓ Missing API key correctly returns 401: {data['detail']}")
    
    def test_invalid_api_key_returns_401(self):
        """Requests with invalid X-API-Key return 401"""
        headers = {"X-API-Key": "nxa_live_invalid_key_12345"}
        response = requests.get(f"{BASE_URL}/api/v1/contacts", headers=headers)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        data = response.json()
        assert "detail" in data
        print(f"✓ Invalid API key correctly returns 401: {data['detail']}")
    
    def test_valid_api_key_returns_200(self):
        """Requests with valid X-API-Key return 200"""
        headers = {"X-API-Key": EXISTING_API_KEY}
        response = requests.get(f"{BASE_URL}/api/v1/contacts", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "data" in data
        assert "total" in data
        print(f"✓ Valid API key returns 200 with {data['total']} contacts")


class TestAdminApiKeyManagement:
    """Test admin API key management endpoints"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=f"username={ADMIN_EMAIL}&password={ADMIN_PASSWORD}"
        )
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, f"No access_token in response: {data}"
        return data["access_token"]
    
    def test_admin_create_api_key(self, admin_token):
        """POST /api/admin/api-keys creates a new API key"""
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "name": f"TEST_api_key_{int(time.time())}",
            "scopes": ["all"],
            "rate_limit_per_hour": 500,
            "description": "Test key for iteration 64"
        }
        response = requests.post(f"{BASE_URL}/api/admin/api-keys", headers=headers, json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "api_key" in data, f"Missing api_key in response: {data}"
        assert "key_id" in data, f"Missing key_id in response: {data}"
        assert data["api_key"].startswith("nxa_live_"), f"API key should start with nxa_live_: {data['api_key']}"
        assert data["name"] == payload["name"]
        
        # Store for cleanup
        self.__class__.created_key_id = data["key_id"]
        self.__class__.created_api_key = data["api_key"]
        print(f"✓ Created API key: {data['key_id']} with prefix {data['api_key'][:16]}...")
    
    def test_admin_list_api_keys(self, admin_token):
        """GET /api/admin/api-keys lists all API keys"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/api-keys", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "keys" in data, f"Missing 'keys' in response: {data}"
        assert "count" in data, f"Missing 'count' in response: {data}"
        assert isinstance(data["keys"], list)
        assert len(data["keys"]) >= 1, "Should have at least one API key"
        
        # Verify key structure
        if data["keys"]:
            key = data["keys"][0]
            assert "key_id" in key
            assert "name" in key
            assert "key_prefix" in key
            assert "scopes" in key
            assert "is_active" in key
            # key_hash should NOT be exposed
            assert "key_hash" not in key, "key_hash should not be exposed in list"
        
        print(f"✓ Listed {data['count']} API keys")
    
    def test_admin_toggle_api_key(self, admin_token):
        """PUT /api/admin/api-keys/{id} toggles active status"""
        if not hasattr(self.__class__, 'created_key_id'):
            pytest.skip("No test key created")
        
        key_id = self.__class__.created_key_id
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        }
        
        # Deactivate
        response = requests.put(
            f"{BASE_URL}/api/admin/api-keys/{key_id}",
            headers=headers,
            json={"is_active": False}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("status") == "ok"
        print(f"✓ Deactivated API key {key_id}")
        
        # Reactivate
        response = requests.put(
            f"{BASE_URL}/api/admin/api-keys/{key_id}",
            headers=headers,
            json={"is_active": True}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print(f"✓ Reactivated API key {key_id}")
    
    def test_admin_delete_api_key(self, admin_token):
        """DELETE /api/admin/api-keys/{id} removes key"""
        if not hasattr(self.__class__, 'created_key_id'):
            pytest.skip("No test key created")
        
        key_id = self.__class__.created_key_id
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = requests.delete(f"{BASE_URL}/api/admin/api-keys/{key_id}", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("status") == "ok"
        assert data.get("deleted") == key_id
        print(f"✓ Deleted API key {key_id}")


class TestApiV1Stats:
    """Test /api/v1/stats endpoint"""
    
    def test_stats_with_valid_key(self):
        """GET /api/v1/stats returns system statistics"""
        headers = {"X-API-Key": EXISTING_API_KEY}
        response = requests.get(f"{BASE_URL}/api/v1/stats", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify stats structure
        assert "contacts" in data, "Missing contacts count"
        assert "leads" in data, "Missing leads count"
        assert "quotes" in data, "Missing quotes stats"
        assert "contracts" in data, "Missing contracts stats"
        assert "projects" in data, "Missing projects stats"
        assert "invoices" in data, "Missing invoices stats"
        assert "timestamp" in data, "Missing timestamp"
        
        print(f"✓ Stats: {data['contacts']} contacts, {data['leads']} leads")


class TestApiV1Contacts:
    """Test /api/v1/contacts CRUD endpoints"""
    
    created_contact_id = None
    
    def test_list_contacts(self):
        """GET /api/v1/contacts returns paginated data"""
        headers = {"X-API-Key": EXISTING_API_KEY}
        response = requests.get(f"{BASE_URL}/api/v1/contacts", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "data" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
        assert "has_more" in data
        assert isinstance(data["data"], list)
        
        print(f"✓ Listed contacts: {data['total']} total, page {data['page']}")
    
    def test_create_contact(self):
        """POST /api/v1/contacts creates a contact"""
        headers = {
            "X-API-Key": EXISTING_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "email": f"test_api_{int(time.time())}@example.com",
            "first_name": "TEST_API",
            "last_name": "Contact",
            "company": "Test Company GmbH",
            "phone": "+49 123 456789",
            "source": "api",
            "tags": ["test", "api"],
            "metadata": {"test_run": "iteration_64"}
        }
        response = requests.post(f"{BASE_URL}/api/v1/contacts", headers=headers, json=payload)
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "contact_id" in data
        assert data["email"] == payload["email"].lower()
        assert data["first_name"] == payload["first_name"]
        assert data["source"] == "api"
        
        self.__class__.created_contact_id = data["contact_id"]
        print(f"✓ Created contact: {data['contact_id']}")
    
    def test_get_contact(self):
        """GET /api/v1/contacts/{id} returns contact"""
        if not self.__class__.created_contact_id:
            pytest.skip("No contact created")
        
        headers = {"X-API-Key": EXISTING_API_KEY}
        contact_id = self.__class__.created_contact_id
        response = requests.get(f"{BASE_URL}/api/v1/contacts/{contact_id}", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data["contact_id"] == contact_id
        assert "email" in data
        print(f"✓ Retrieved contact: {contact_id}")
    
    def test_update_contact(self):
        """PUT /api/v1/contacts/{id} updates contact"""
        if not self.__class__.created_contact_id:
            pytest.skip("No contact created")
        
        headers = {
            "X-API-Key": EXISTING_API_KEY,
            "Content-Type": "application/json"
        }
        contact_id = self.__class__.created_contact_id
        payload = {"company": "Updated Company GmbH", "phone": "+49 999 888777"}
        
        response = requests.put(f"{BASE_URL}/api/v1/contacts/{contact_id}", headers=headers, json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data["company"] == payload["company"]
        assert data["phone"] == payload["phone"]
        print(f"✓ Updated contact: {contact_id}")
        
        # Verify persistence with GET
        response = requests.get(f"{BASE_URL}/api/v1/contacts/{contact_id}", headers={"X-API-Key": EXISTING_API_KEY})
        assert response.status_code == 200
        data = response.json()
        assert data["company"] == payload["company"], "Update not persisted"


class TestApiV1Leads:
    """Test /api/v1/leads CRUD endpoints"""
    
    created_lead_id = None
    
    def test_list_leads(self):
        """GET /api/v1/leads returns paginated data"""
        headers = {"X-API-Key": EXISTING_API_KEY}
        response = requests.get(f"{BASE_URL}/api/v1/leads", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "data" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
        assert "has_more" in data
        
        print(f"✓ Listed leads: {data['total']} total")
    
    def test_create_lead(self):
        """POST /api/v1/leads creates a lead"""
        headers = {
            "X-API-Key": EXISTING_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "email": f"test_lead_{int(time.time())}@example.com",
            "vorname": "TEST_API",
            "nachname": "Lead",
            "unternehmen": "Lead Company GmbH",
            "telefon": "+49 111 222333",
            "nachricht": "Test lead from API v1",
            "source": "api",
            "kanal": "api"
        }
        response = requests.post(f"{BASE_URL}/api/v1/leads", headers=headers, json=payload)
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "lead_id" in data
        assert data["email"] == payload["email"].lower()
        assert data["vorname"] == payload["vorname"]
        assert data["status"] == "new"
        
        self.__class__.created_lead_id = data["lead_id"]
        print(f"✓ Created lead: {data['lead_id']}")
    
    def test_get_lead(self):
        """GET /api/v1/leads/{id} returns lead"""
        if not self.__class__.created_lead_id:
            pytest.skip("No lead created")
        
        headers = {"X-API-Key": EXISTING_API_KEY}
        lead_id = self.__class__.created_lead_id
        response = requests.get(f"{BASE_URL}/api/v1/leads/{lead_id}", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data["lead_id"] == lead_id
        print(f"✓ Retrieved lead: {lead_id}")


class TestApiV1ReadOnlyEndpoints:
    """Test read-only endpoints: quotes, contracts, projects, invoices"""
    
    def test_list_quotes(self):
        """GET /api/v1/quotes returns paginated data"""
        headers = {"X-API-Key": EXISTING_API_KEY}
        response = requests.get(f"{BASE_URL}/api/v1/quotes", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "data" in data
        assert "total" in data
        assert "page" in data
        print(f"✓ Listed quotes: {data['total']} total")
    
    def test_list_contracts(self):
        """GET /api/v1/contracts returns paginated data"""
        headers = {"X-API-Key": EXISTING_API_KEY}
        response = requests.get(f"{BASE_URL}/api/v1/contracts", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "data" in data
        assert "total" in data
        print(f"✓ Listed contracts: {data['total']} total")
    
    def test_list_projects(self):
        """GET /api/v1/projects returns paginated data"""
        headers = {"X-API-Key": EXISTING_API_KEY}
        response = requests.get(f"{BASE_URL}/api/v1/projects", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "data" in data
        assert "total" in data
        print(f"✓ Listed projects: {data['total']} total")
    
    def test_list_invoices(self):
        """GET /api/v1/invoices returns paginated data"""
        headers = {"X-API-Key": EXISTING_API_KEY}
        response = requests.get(f"{BASE_URL}/api/v1/invoices", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "data" in data
        assert "total" in data
        print(f"✓ Listed invoices: {data['total']} total")


class TestApiV1Webhooks:
    """Test /api/v1/webhooks CRUD endpoints"""
    
    created_webhook_id = None
    
    def test_register_webhook(self):
        """POST /api/v1/webhooks creates a webhook"""
        headers = {
            "X-API-Key": EXISTING_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "url": "https://example.com/webhook/test",
            "events": ["contact.created", "lead.created"],
            "description": "Test webhook for iteration 64"
        }
        response = requests.post(f"{BASE_URL}/api/v1/webhooks", headers=headers, json=payload)
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "webhook_id" in data
        assert data["url"] == payload["url"]
        assert data["events"] == payload["events"]
        assert "secret" in data  # Auto-generated if not provided
        assert data["is_active"] == True
        
        self.__class__.created_webhook_id = data["webhook_id"]
        print(f"✓ Created webhook: {data['webhook_id']}")
    
    def test_list_webhooks(self):
        """GET /api/v1/webhooks lists webhooks for the key"""
        headers = {"X-API-Key": EXISTING_API_KEY}
        response = requests.get(f"{BASE_URL}/api/v1/webhooks", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "data" in data
        assert "total" in data
        assert isinstance(data["data"], list)
        print(f"✓ Listed webhooks: {data['total']} total")
    
    def test_delete_webhook(self):
        """DELETE /api/v1/webhooks/{id} removes webhook"""
        if not self.__class__.created_webhook_id:
            pytest.skip("No webhook created")
        
        headers = {"X-API-Key": EXISTING_API_KEY}
        webhook_id = self.__class__.created_webhook_id
        
        response = requests.delete(f"{BASE_URL}/api/v1/webhooks/{webhook_id}", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("deleted") == True
        print(f"✓ Deleted webhook: {webhook_id}")
        
        # Verify deletion
        response = requests.get(f"{BASE_URL}/api/v1/webhooks", headers=headers)
        data = response.json()
        webhook_ids = [w["webhook_id"] for w in data.get("data", [])]
        assert webhook_id not in webhook_ids, "Webhook should be deleted"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
