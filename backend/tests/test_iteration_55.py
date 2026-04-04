"""
Iteration 55 - Backend API Tests
Testing: Outbound Lead Machine, Projects, Contracts, Dashboard, Billing, Legal, Monitoring
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://contract-os.preview.emergentagent.com').rstrip('/')
ADMIN_EMAIL = "p.courbois@icloud.com"
ADMIN_PASSWORD = "1def!xO2022!!"


class TestAdminAuth:
    """Admin authentication tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get admin auth token"""
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
        """Test admin login with valid credentials"""
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
    
    def test_admin_login_invalid_credentials(self):
        """Test admin login with invalid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": "wrong@email.com", "password": "wrongpassword"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 401
        print(f"✓ Invalid credentials correctly rejected with 401")


class TestOutboundLeadMachine:
    """Outbound Lead Machine API tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get admin auth token"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
    
    def test_outbound_pipeline_stats(self, headers):
        """Test GET /api/admin/outbound/pipeline returns pipeline data"""
        response = requests.get(f"{BASE_URL}/api/admin/outbound/pipeline", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "pipeline" in data
        assert "total" in data
        assert "conversion_rate" in data
        assert isinstance(data["pipeline"], list)
        print(f"✓ Pipeline stats: total={data['total']}, conversion_rate={data['conversion_rate']}%")
        print(f"  Pipeline stages: {len(data['pipeline'])}")
    
    def test_outbound_leads_list(self, headers):
        """Test GET /api/admin/outbound/leads returns leads list"""
        response = requests.get(f"{BASE_URL}/api/admin/outbound/leads?limit=50", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "leads" in data
        assert "count" in data
        assert isinstance(data["leads"], list)
        print(f"✓ Outbound leads list: {data['count']} leads returned")
        if data["leads"]:
            lead = data["leads"][0]
            assert "outbound_lead_id" in lead
            assert "company_name" in lead
            assert "status" in lead
            print(f"  First lead: {lead.get('company_name')} - status: {lead.get('status')}")
    
    def test_outbound_leads_filter_by_status(self, headers):
        """Test filtering outbound leads by status"""
        response = requests.get(f"{BASE_URL}/api/admin/outbound/leads?status=discovered&limit=20", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "leads" in data
        # All returned leads should have status 'discovered'
        for lead in data["leads"]:
            assert lead["status"] == "discovered", f"Expected status 'discovered', got '{lead['status']}'"
        print(f"✓ Filter by status 'discovered': {data['count']} leads")
    
    def test_outbound_discover_lead(self, headers):
        """Test POST /api/admin/outbound/discover creates a new lead"""
        test_lead = {
            "name": f"TEST_Company_{int(time.time())}",
            "website": "https://test-company.de",
            "industry": "SaaS",
            "email": f"test_{int(time.time())}@testcompany.de",
            "phone": "+49 123 456789",
            "contact_name": "Test Contact",
            "country": "DE",
            "notes": "Test lead created by iteration 55 tests"
        }
        response = requests.post(f"{BASE_URL}/api/admin/outbound/discover", headers=headers, json=test_lead)
        assert response.status_code == 200
        data = response.json()
        assert "outbound_lead_id" in data
        assert data.get("status") == "discovered"
        print(f"✓ Lead discovered: {data['outbound_lead_id']}")
        return data["outbound_lead_id"]
    
    def test_outbound_lead_detail(self, headers):
        """Test GET /api/admin/outbound/{lead_id} returns lead detail"""
        # First get a lead
        response = requests.get(f"{BASE_URL}/api/admin/outbound/leads?limit=1", headers=headers)
        assert response.status_code == 200
        leads = response.json().get("leads", [])
        if not leads:
            pytest.skip("No outbound leads available for detail test")
        
        lead_id = leads[0]["outbound_lead_id"]
        response = requests.get(f"{BASE_URL}/api/admin/outbound/{lead_id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "outbound_lead_id" in data
        assert "company_name" in data
        assert "status" in data
        print(f"✓ Lead detail: {data.get('company_name')} - score: {data.get('score', 0)}")
    
    def test_outbound_prequalify(self, headers):
        """Test POST /api/admin/outbound/{id}/prequalify transitions to qualified"""
        # Get a discovered lead
        response = requests.get(f"{BASE_URL}/api/admin/outbound/leads?status=discovered&limit=1", headers=headers)
        leads = response.json().get("leads", [])
        if not leads:
            pytest.skip("No discovered leads available for prequalify test")
        
        lead_id = leads[0]["outbound_lead_id"]
        response = requests.post(f"{BASE_URL}/api/admin/outbound/{lead_id}/prequalify", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "qualified"
        print(f"✓ Lead prequalified: {lead_id} -> status: qualified")
    
    def test_outbound_analyze(self, headers):
        """Test POST /api/admin/outbound/{id}/analyze scores the lead"""
        # Get a qualified lead
        response = requests.get(f"{BASE_URL}/api/admin/outbound/leads?status=qualified&limit=1", headers=headers)
        leads = response.json().get("leads", [])
        if not leads:
            # Try discovered leads
            response = requests.get(f"{BASE_URL}/api/admin/outbound/leads?status=discovered&limit=1", headers=headers)
            leads = response.json().get("leads", [])
        if not leads:
            pytest.skip("No leads available for analyze test")
        
        lead_id = leads[0]["outbound_lead_id"]
        response = requests.post(f"{BASE_URL}/api/admin/outbound/{lead_id}/analyze", headers=headers, json={})
        assert response.status_code == 200
        data = response.json()
        assert "score" in data or "status" in data
        print(f"✓ Lead analyzed: {lead_id} - score: {data.get('score', 'N/A')}")
    
    def test_outbound_legal_check(self, headers):
        """Test POST /api/admin/outbound/{id}/legal-check approves legal status"""
        # Get a qualified lead
        response = requests.get(f"{BASE_URL}/api/admin/outbound/leads?status=qualified&limit=1", headers=headers)
        leads = response.json().get("leads", [])
        if not leads:
            pytest.skip("No qualified leads available for legal-check test")
        
        lead_id = leads[0]["outbound_lead_id"]
        response = requests.post(f"{BASE_URL}/api/admin/outbound/{lead_id}/legal-check", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "legal_status" in data or "status" in data
        print(f"✓ Legal check: {lead_id} - legal_status: {data.get('legal_status', 'N/A')}")
    
    def test_outbound_bulk_import(self, headers):
        """Test POST /api/admin/outbound/bulk-import imports multiple leads"""
        test_leads = {
            "leads": [
                {"name": f"TEST_BulkCompany1_{int(time.time())}", "industry": "IT", "email": f"bulk1_{int(time.time())}@test.de"},
                {"name": f"TEST_BulkCompany2_{int(time.time())}", "industry": "Consulting", "email": f"bulk2_{int(time.time())}@test.de"}
            ]
        }
        response = requests.post(f"{BASE_URL}/api/admin/outbound/bulk-import", headers=headers, json=test_leads)
        assert response.status_code == 200
        data = response.json()
        assert "imported" in data
        assert "skipped" in data
        print(f"✓ Bulk import: imported={data['imported']}, skipped={data['skipped']}")
    
    def test_outbound_campaigns(self, headers):
        """Test GET /api/admin/outbound/campaigns returns campaign overview"""
        response = requests.get(f"{BASE_URL}/api/admin/outbound/campaigns", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "campaigns" in data
        assert "recent_activity" in data
        print(f"✓ Campaigns: total_leads={data['campaigns'].get('total_leads', 0)}")


class TestProjects:
    """Project CRUD API tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
    
    def test_projects_list(self, headers):
        """Test GET /api/admin/projects returns projects list"""
        response = requests.get(f"{BASE_URL}/api/admin/projects", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "projects" in data
        print(f"✓ Projects list: {len(data['projects'])} projects")
    
    def test_project_create(self, headers):
        """Test POST /api/admin/projects creates a new project"""
        project_data = {
            "title": f"TEST_Project_{int(time.time())}",
            "customer_email": "test@example.com",
            "tier": "starter",
            "classification": "standard"
        }
        response = requests.post(f"{BASE_URL}/api/admin/projects", headers=headers, json=project_data)
        assert response.status_code == 200
        data = response.json()
        assert "project_id" in data
        print(f"✓ Project created: {data['project_id']}")
        return data["project_id"]
    
    def test_project_detail(self, headers):
        """Test GET /api/admin/projects/{id} returns project detail"""
        # First get a project
        response = requests.get(f"{BASE_URL}/api/admin/projects", headers=headers)
        projects = response.json().get("projects", [])
        if not projects:
            pytest.skip("No projects available for detail test")
        
        project_id = projects[0]["project_id"]
        response = requests.get(f"{BASE_URL}/api/admin/projects/{project_id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "project_id" in data
        assert "title" in data
        print(f"✓ Project detail: {data.get('title')} - status: {data.get('status')}")


class TestContracts:
    """Contract CRUD API tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
    
    def test_contracts_list(self, headers):
        """Test GET /api/admin/contracts returns contracts list"""
        response = requests.get(f"{BASE_URL}/api/admin/contracts", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "contracts" in data
        print(f"✓ Contracts list: {len(data['contracts'])} contracts")
    
    def test_contract_create(self, headers):
        """Test POST /api/admin/contracts creates a new contract"""
        contract_data = {
            "customer": {
                "email": f"test_{int(time.time())}@example.com",
                "name": "Test Customer",
                "company": "Test Company GmbH"
            },
            "tier_key": "starter",
            "contract_type": "standard",
            "notes": "Test contract created by iteration 55 tests"
        }
        response = requests.post(f"{BASE_URL}/api/admin/contracts", headers=headers, json=contract_data)
        assert response.status_code == 200
        data = response.json()
        assert "contract_id" in data
        print(f"✓ Contract created: {data['contract_id']}")
        return data["contract_id"]
    
    def test_contract_detail(self, headers):
        """Test GET /api/admin/contracts/{id} returns contract detail"""
        # First get a contract
        response = requests.get(f"{BASE_URL}/api/admin/contracts", headers=headers)
        contracts = response.json().get("contracts", [])
        if not contracts:
            pytest.skip("No contracts available for detail test")
        
        contract_id = contracts[0]["contract_id"]
        response = requests.get(f"{BASE_URL}/api/admin/contracts/{contract_id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "contract_id" in data
        assert "contract_number" in data
        print(f"✓ Contract detail: {data.get('contract_number')} - status: {data.get('status')}")


class TestDashboard:
    """Dashboard stats API tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
    
    def test_dashboard_stats(self, headers):
        """Test GET /api/admin/stats returns dashboard stats"""
        response = requests.get(f"{BASE_URL}/api/admin/stats", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "leads_total" in data
        assert "bookings_total" in data
        print(f"✓ Dashboard stats: leads={data.get('leads_total')}, bookings={data.get('bookings_total')}")


class TestBilling:
    """Billing API tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
    
    def test_billing_status(self, headers):
        """Test GET /api/admin/billing/status returns billing dashboard"""
        response = requests.get(f"{BASE_URL}/api/admin/billing/status", headers=headers)
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Billing status endpoint working")


class TestLegal:
    """Legal & Compliance API tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
    
    def test_legal_compliance(self, headers):
        """Test GET /api/admin/legal/compliance returns compliance summary"""
        response = requests.get(f"{BASE_URL}/api/admin/legal/compliance", headers=headers)
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Legal compliance endpoint working")


class TestMonitoring:
    """Monitoring API tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
    
    def test_monitoring_health(self, headers):
        """Test GET /api/admin/monitoring/health returns system status"""
        response = requests.get(f"{BASE_URL}/api/admin/monitoring/health", headers=headers)
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Monitoring health endpoint working")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
