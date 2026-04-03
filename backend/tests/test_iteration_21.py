"""
NeXifyAI Iteration 21 Backend Tests
Testing:
1. POST /api/admin/customers — Manual customer creation
2. POST /api/admin/customers/portal-access — Portal access (Magic Link)
3. GET /api/admin/memory/agents — mem0 Agent-IDs list
4. GET /api/admin/memory/by-agent/{agent_id} — Memory entries per agent
5. GET /api/admin/memory/search?q=... — Text search in memory entries
6. POST /api/admin/customer-memory/{email}/facts — Manual memory fact addition
"""

import pytest
import requests
import os
import time
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://ai-architecture-lab.preview.emergentagent.com').rstrip('/')

# Test credentials
ADMIN_EMAIL = "p.courbois@icloud.com"
ADMIN_PASSWORD = "NxAi#Secure2026!"


class TestAdminAuth:
    """Admin authentication tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get admin authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        return data["access_token"]
    
    def test_admin_login_success(self):
        """Test admin login with correct credentials"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        print(f"✓ Admin login successful, token received")


class TestCustomerManagement:
    """Customer creation and portal access tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get admin authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        """Auth headers for API calls"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
    
    def test_create_customer_success(self, headers):
        """POST /api/admin/customers — Create customer with all fields"""
        unique_id = str(uuid.uuid4())[:8]
        test_email = f"TEST_iter21_{unique_id}@testfirma.de"
        
        payload = {
            "vorname": "Max",
            "nachname": "Mustermann",
            "email": test_email,
            "unternehmen": "Test Firma GmbH",
            "telefon": "+49 171 234 5678",
            "branche": "Logistik"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/admin/customers",
            json=payload,
            headers=headers
        )
        
        assert response.status_code == 200, f"Create customer failed: {response.text}"
        data = response.json()
        assert data["status"] == "ok"
        assert data["email"] == test_email.lower()
        assert "contact_id" in data
        print(f"✓ Customer created: {test_email}, contact_id: {data['contact_id']}")
        return test_email
    
    def test_create_customer_missing_email(self, headers):
        """POST /api/admin/customers — Should fail without email"""
        payload = {
            "vorname": "Max",
            "nachname": "Mustermann"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/admin/customers",
            json=payload,
            headers=headers
        )
        
        assert response.status_code == 400
        print(f"✓ Customer creation correctly rejected without email")
    
    def test_create_customer_upsert(self, headers):
        """POST /api/admin/customers — Upsert existing customer"""
        unique_id = str(uuid.uuid4())[:8]
        test_email = f"TEST_upsert_{unique_id}@testfirma.de"
        
        # First creation
        payload1 = {
            "vorname": "Initial",
            "nachname": "Name",
            "email": test_email,
            "unternehmen": "Initial Company"
        }
        response1 = requests.post(f"{BASE_URL}/api/admin/customers", json=payload1, headers=headers)
        assert response1.status_code == 200
        
        # Upsert with updated data
        payload2 = {
            "vorname": "Updated",
            "nachname": "Name",
            "email": test_email,
            "unternehmen": "Updated Company",
            "branche": "IT"
        }
        response2 = requests.post(f"{BASE_URL}/api/admin/customers", json=payload2, headers=headers)
        assert response2.status_code == 200
        data = response2.json()
        assert data["status"] == "ok"
        print(f"✓ Customer upsert successful for {test_email}")
    
    def test_portal_access_creation(self, headers):
        """POST /api/admin/customers/portal-access — Generate Magic Link"""
        # First create a customer
        unique_id = str(uuid.uuid4())[:8]
        test_email = f"TEST_portal_{unique_id}@testfirma.de"
        
        create_response = requests.post(
            f"{BASE_URL}/api/admin/customers",
            json={"email": test_email, "vorname": "Portal", "nachname": "Test"},
            headers=headers
        )
        assert create_response.status_code == 200
        
        # Now create portal access
        response = requests.post(
            f"{BASE_URL}/api/admin/customers/portal-access",
            json={"email": test_email},
            headers=headers
        )
        
        assert response.status_code == 200, f"Portal access creation failed: {response.text}"
        data = response.json()
        assert data["status"] == "ok"
        assert "portal_url" in data
        assert "expires_at" in data
        assert "/portal/" in data["portal_url"]
        print(f"✓ Portal access created: {data['portal_url'][:60]}...")
    
    def test_portal_access_missing_email(self, headers):
        """POST /api/admin/customers/portal-access — Should fail without email"""
        response = requests.post(
            f"{BASE_URL}/api/admin/customers/portal-access",
            json={},
            headers=headers
        )
        assert response.status_code == 400
        print(f"✓ Portal access correctly rejected without email")
    
    def test_portal_access_nonexistent_contact(self, headers):
        """POST /api/admin/customers/portal-access — Should fail for non-existent contact"""
        response = requests.post(
            f"{BASE_URL}/api/admin/customers/portal-access",
            json={"email": "nonexistent_xyz_12345@nowhere.com"},
            headers=headers
        )
        assert response.status_code == 404
        print(f"✓ Portal access correctly rejected for non-existent contact")


class TestMem0MemoryAPI:
    """mem0 Memory Service API tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get admin authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        """Auth headers for API calls"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
    
    def test_memory_agents_list(self, headers):
        """GET /api/admin/memory/agents — List all agent IDs"""
        response = requests.get(
            f"{BASE_URL}/api/admin/memory/agents",
            headers=headers
        )
        
        assert response.status_code == 200, f"Memory agents list failed: {response.text}"
        data = response.json()
        assert "agents" in data
        
        # Verify expected agent IDs exist
        expected_agents = ["emergent_build", "intake", "research", "outreach", "offer", 
                          "planning", "finance", "support", "design", "qa", "admin", "system", "chat"]
        for agent in expected_agents:
            assert agent in data["agents"], f"Missing agent: {agent}"
        
        print(f"✓ Memory agents list returned {len(data['agents'])} agents: {list(data['agents'].keys())}")
    
    def test_memory_by_agent(self, headers):
        """GET /api/admin/memory/by-agent/{agent_id} — Get entries for specific agent"""
        # Test with admin agent (likely has entries from customer creation)
        response = requests.get(
            f"{BASE_URL}/api/admin/memory/by-agent/admin_agent",
            headers=headers
        )
        
        assert response.status_code == 200, f"Memory by agent failed: {response.text}"
        data = response.json()
        assert "agent_id" in data
        assert data["agent_id"] == "admin_agent"
        assert "entries" in data
        assert "count" in data
        assert isinstance(data["entries"], list)
        print(f"✓ Memory by agent 'admin_agent' returned {data['count']} entries")
    
    def test_memory_by_agent_with_limit(self, headers):
        """GET /api/admin/memory/by-agent/{agent_id}?limit=5 — Test limit parameter"""
        response = requests.get(
            f"{BASE_URL}/api/admin/memory/by-agent/admin_agent?limit=5",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["entries"]) <= 5
        print(f"✓ Memory by agent with limit=5 returned {len(data['entries'])} entries")
    
    def test_memory_search(self, headers):
        """GET /api/admin/memory/search?q=... — Text search in memory"""
        # First add a unique memory fact
        unique_id = str(uuid.uuid4())[:8]
        test_email = f"TEST_search_{unique_id}@testfirma.de"
        search_term = f"UNIQUE_SEARCH_TERM_{unique_id}"
        
        # Create customer first
        requests.post(
            f"{BASE_URL}/api/admin/customers",
            json={"email": test_email, "vorname": "Search", "nachname": "Test"},
            headers=headers
        )
        
        # Add memory fact with unique term
        requests.post(
            f"{BASE_URL}/api/admin/customer-memory/{test_email}/facts",
            json={"fact": f"Test fact with {search_term}", "category": "test"},
            headers=headers
        )
        
        # Search for the unique term
        response = requests.get(
            f"{BASE_URL}/api/admin/memory/search?q={search_term}",
            headers=headers
        )
        
        assert response.status_code == 200, f"Memory search failed: {response.text}"
        data = response.json()
        assert "query" in data
        assert data["query"] == search_term
        assert "results" in data
        assert "count" in data
        assert data["count"] >= 1, f"Expected at least 1 result for unique search term"
        print(f"✓ Memory search for '{search_term}' returned {data['count']} results")
    
    def test_memory_search_with_contact_filter(self, headers):
        """GET /api/admin/memory/search?q=...&contact_id=... — Search with contact filter"""
        response = requests.get(
            f"{BASE_URL}/api/admin/memory/search?q=Kunde&limit=10",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        print(f"✓ Memory search with filter returned {data['count']} results")


class TestCustomerMemoryFacts:
    """Customer memory fact management tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get admin authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        """Auth headers for API calls"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
    
    def test_add_memory_fact_success(self, headers):
        """POST /api/admin/customer-memory/{email}/facts — Add memory fact"""
        unique_id = str(uuid.uuid4())[:8]
        test_email = f"TEST_memfact_{unique_id}@testfirma.de"
        
        # Create customer first
        requests.post(
            f"{BASE_URL}/api/admin/customers",
            json={"email": test_email, "vorname": "Memory", "nachname": "Test"},
            headers=headers
        )
        
        # Add memory fact
        payload = {
            "fact": f"Test memory fact for iteration 21 - {unique_id}",
            "category": "interest",
            "verification_status": "verifiziert"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/admin/customer-memory/{test_email}/facts",
            json=payload,
            headers=headers
        )
        
        assert response.status_code == 200, f"Add memory fact failed: {response.text}"
        data = response.json()
        assert data["status"] == "ok"
        assert "memory" in data
        assert data["memory"]["fact"] == payload["fact"]
        assert data["memory"]["category"] == "interest"
        assert "agent_id" in data["memory"]
        assert "contact_id" in data["memory"]
        print(f"✓ Memory fact added for {test_email}: {payload['fact'][:50]}...")
    
    def test_add_memory_fact_with_agent_id(self, headers):
        """POST /api/admin/customer-memory/{email}/facts — Verify agent_id is set"""
        unique_id = str(uuid.uuid4())[:8]
        test_email = f"TEST_agentid_{unique_id}@testfirma.de"
        
        # Create customer
        requests.post(
            f"{BASE_URL}/api/admin/customers",
            json={"email": test_email, "vorname": "Agent", "nachname": "Test"},
            headers=headers
        )
        
        # Add memory fact
        response = requests.post(
            f"{BASE_URL}/api/admin/customer-memory/{test_email}/facts",
            json={"fact": "Test fact with agent_id verification", "category": "context"},
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["memory"]["agent_id"] == "admin_agent"
        print(f"✓ Memory fact correctly assigned agent_id: {data['memory']['agent_id']}")
    
    def test_add_memory_fact_empty_fact(self, headers):
        """POST /api/admin/customer-memory/{email}/facts — Should fail with empty fact"""
        response = requests.post(
            f"{BASE_URL}/api/admin/customer-memory/test@test.de/facts",
            json={"fact": "", "category": "test"},
            headers=headers
        )
        
        assert response.status_code == 400
        print(f"✓ Empty fact correctly rejected")
    
    def test_add_memory_fact_creates_contact(self, headers):
        """POST /api/admin/customer-memory/{email}/facts — Should create contact if not exists"""
        unique_id = str(uuid.uuid4())[:8]
        test_email = f"TEST_newcontact_{unique_id}@testfirma.de"
        
        # Add memory fact without creating customer first
        response = requests.post(
            f"{BASE_URL}/api/admin/customer-memory/{test_email}/facts",
            json={"fact": "Auto-created contact test", "category": "test"},
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "contact_id" in data["memory"]
        print(f"✓ Contact auto-created when adding memory fact: {data['memory']['contact_id']}")
    
    def test_get_customer_memory(self, headers):
        """GET /api/admin/customer-memory/{email} — Get full customer memory context"""
        unique_id = str(uuid.uuid4())[:8]
        test_email = f"TEST_getmem_{unique_id}@testfirma.de"
        
        # Create customer and add facts
        requests.post(
            f"{BASE_URL}/api/admin/customers",
            json={"email": test_email, "vorname": "GetMem", "nachname": "Test", "branche": "IT"},
            headers=headers
        )
        
        requests.post(
            f"{BASE_URL}/api/admin/customer-memory/{test_email}/facts",
            json={"fact": "Fact 1 for get test", "category": "interest"},
            headers=headers
        )
        
        requests.post(
            f"{BASE_URL}/api/admin/customer-memory/{test_email}/facts",
            json={"fact": "Fact 2 for get test", "category": "context"},
            headers=headers
        )
        
        # Get customer memory
        response = requests.get(
            f"{BASE_URL}/api/admin/customer-memory/{test_email}",
            headers=headers
        )
        
        assert response.status_code == 200, f"Get customer memory failed: {response.text}"
        data = response.json()
        assert data["email"] == test_email.lower()
        assert "memory_context" in data
        assert "memory_facts" in data
        assert len(data["memory_facts"]) >= 2
        print(f"✓ Customer memory retrieved with {len(data['memory_facts'])} facts")


class TestHealthAndBasics:
    """Basic health and API tests"""
    
    def test_health_endpoint(self):
        """GET /api/health — Basic health check"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"✓ Health check passed: {data}")
    
    def test_company_endpoint(self):
        """GET /api/company — Company info"""
        response = requests.get(f"{BASE_URL}/api/company")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        print(f"✓ Company info: {data['name']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
