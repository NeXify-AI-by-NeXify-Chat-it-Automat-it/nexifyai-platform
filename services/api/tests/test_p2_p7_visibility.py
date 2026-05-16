"""
P2-P7 Visibility Layer Tests
Tests for Admin Billing Dashboard, Outbound Pipeline, Legal Guardian View,
Project Download/Handover, and Customer Portal Projects Tab
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
ADMIN_EMAIL = "p.courbois@icloud.com"
ADMIN_PASSWORD = "NxAi#Secure2026!"
TEST_PROJECT_ID = "prj_6c4e346089384828"


class TestAdminAuth:
    """Admin authentication tests"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin auth token"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access_token in response"
        return data["access_token"]
    
    def test_admin_login(self, admin_token):
        """Test admin login returns valid token"""
        assert admin_token is not None
        assert len(admin_token) > 0
        print(f"✅ Admin login successful, token length: {len(admin_token)}")


class TestBillingDashboard:
    """P7: Billing Dashboard tests"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        return response.json().get("access_token")
    
    def test_billing_status_endpoint(self, admin_token):
        """GET /api/admin/billing/status returns billing overview"""
        response = requests.get(
            f"{BASE_URL}/api/admin/billing/status",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Billing status failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "quotes" in data, "Missing quotes in billing status"
        assert "invoices" in data, "Missing invoices in billing status"
        assert "contracts" in data, "Missing contracts in billing status"
        assert "revenue" in data, "Missing revenue in billing status"
        
        # Verify quotes structure
        assert "total" in data["quotes"], "Missing quotes.total"
        assert "accepted" in data["quotes"], "Missing quotes.accepted"
        
        # Verify invoices structure
        assert "total" in data["invoices"], "Missing invoices.total"
        assert "paid" in data["invoices"], "Missing invoices.paid"
        assert "pending" in data["invoices"], "Missing invoices.pending"
        assert "overdue" in data["invoices"], "Missing invoices.overdue"
        
        # Verify contracts structure
        assert "total" in data["contracts"], "Missing contracts.total"
        assert "active" in data["contracts"], "Missing contracts.active"
        
        # Verify revenue structure
        assert "total_gross" in data["revenue"], "Missing revenue.total_gross"
        assert "total_open" in data["revenue"], "Missing revenue.total_open"
        
        print(f"✅ Billing status: {data['quotes']['total']} quotes, {data['invoices']['total']} invoices, {data['contracts']['total']} contracts")
    
    def test_billing_status_requires_auth(self):
        """Billing status requires authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/billing/status")
        assert response.status_code == 401, "Billing status should require auth"
        print("✅ Billing status correctly requires authentication")


class TestOutboundPipeline:
    """P6: Outbound Pipeline tests"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        return response.json().get("access_token")
    
    def test_outbound_pipeline_endpoint(self, admin_token):
        """GET /api/admin/outbound/pipeline returns pipeline overview"""
        response = requests.get(
            f"{BASE_URL}/api/admin/outbound/pipeline",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Outbound pipeline failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "pipeline" in data, "Missing pipeline in response"
        assert "total" in data, "Missing total in response"
        assert "conversion_rate" in data, "Missing conversion_rate in response"
        
        # Verify pipeline is a list with stages
        assert isinstance(data["pipeline"], list), "Pipeline should be a list"
        if len(data["pipeline"]) > 0:
            stage = data["pipeline"][0]
            assert "key" in stage, "Pipeline stage missing key"
            assert "label" in stage, "Pipeline stage missing label"
            assert "count" in stage, "Pipeline stage missing count"
        
        print(f"✅ Outbound pipeline: {data['total']} total leads, {data['conversion_rate']}% conversion")
    
    def test_outbound_pipeline_requires_auth(self):
        """Outbound pipeline requires authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/outbound/pipeline")
        assert response.status_code == 401, "Outbound pipeline should require auth"
        print("✅ Outbound pipeline correctly requires authentication")


class TestLegalGuardian:
    """P5: Legal Guardian View tests"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        return response.json().get("access_token")
    
    def test_compliance_summary_endpoint(self, admin_token):
        """GET /api/admin/legal/compliance returns compliance summary"""
        response = requests.get(
            f"{BASE_URL}/api/admin/legal/compliance",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Compliance summary failed: {response.text}"
        data = response.json()
        
        # Verify response structure (may vary based on implementation)
        assert isinstance(data, dict), "Compliance summary should be a dict"
        print(f"✅ Compliance summary returned: {list(data.keys())}")
    
    def test_legal_risks_endpoint(self, admin_token):
        """GET /api/admin/legal/risks returns risks list"""
        response = requests.get(
            f"{BASE_URL}/api/admin/legal/risks",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Legal risks failed: {response.text}"
        data = response.json()
        
        assert "risks" in data, "Missing risks in response"
        assert isinstance(data["risks"], list), "Risks should be a list"
        print(f"✅ Legal risks: {len(data['risks'])} risks found")
    
    def test_legal_audit_endpoint(self, admin_token):
        """GET /api/admin/legal/audit returns audit log"""
        response = requests.get(
            f"{BASE_URL}/api/admin/legal/audit",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Legal audit failed: {response.text}"
        data = response.json()
        
        assert "audit_log" in data, "Missing audit_log in response"
        assert isinstance(data["audit_log"], list), "Audit log should be a list"
        print(f"✅ Legal audit: {len(data['audit_log'])} audit entries")
    
    def test_legal_endpoints_require_auth(self):
        """Legal endpoints require authentication"""
        endpoints = [
            "/api/admin/legal/compliance",
            "/api/admin/legal/risks",
            "/api/admin/legal/audit"
        ]
        for endpoint in endpoints:
            response = requests.get(f"{BASE_URL}{endpoint}")
            assert response.status_code == 401, f"{endpoint} should require auth"
        print("✅ All legal endpoints correctly require authentication")


class TestProjectHandover:
    """P3-P4: Project Download/Handover tests"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        return response.json().get("access_token")
    
    def test_download_handover_endpoint(self, admin_token):
        """GET /api/admin/projects/{id}/download-handover returns markdown file"""
        response = requests.get(
            f"{BASE_URL}/api/admin/projects/{TEST_PROJECT_ID}/download-handover",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        # May return 404 if no handover version exists
        if response.status_code == 404:
            print(f"⚠️ No handover version found for project {TEST_PROJECT_ID}")
            pytest.skip("No handover version exists for test project")
        
        assert response.status_code == 200, f"Download handover failed: {response.text}"
        
        # Verify it's a markdown file
        content_type = response.headers.get("content-type", "")
        assert "text/markdown" in content_type or "text/plain" in content_type, f"Expected markdown, got {content_type}"
        
        # Verify content-disposition header for download
        content_disp = response.headers.get("content-disposition", "")
        assert "attachment" in content_disp, "Should have attachment disposition"
        assert ".md" in content_disp, "Filename should be .md"
        
        print(f"✅ Download handover: {len(response.content)} bytes, {content_disp}")
    
    def test_start_prompt_endpoint(self, admin_token):
        """GET /api/admin/projects/{id}/start-prompt returns start prompt"""
        response = requests.get(
            f"{BASE_URL}/api/admin/projects/{TEST_PROJECT_ID}/start-prompt",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        # May return 404 if no handover version exists
        if response.status_code == 404:
            print(f"⚠️ No handover version found for project {TEST_PROJECT_ID}")
            pytest.skip("No handover version exists for test project")
        
        assert response.status_code == 200, f"Start prompt failed: {response.text}"
        data = response.json()
        
        assert "start_prompt" in data, "Missing start_prompt in response"
        assert "version" in data, "Missing version in response"
        
        print(f"✅ Start prompt: version {data['version']}, prompt length: {len(data.get('start_prompt', ''))}")
    
    def test_project_endpoints_require_auth(self):
        """Project handover endpoints require authentication"""
        endpoints = [
            f"/api/admin/projects/{TEST_PROJECT_ID}/download-handover",
            f"/api/admin/projects/{TEST_PROJECT_ID}/start-prompt"
        ]
        for endpoint in endpoints:
            response = requests.get(f"{BASE_URL}{endpoint}")
            assert response.status_code == 401, f"{endpoint} should require auth"
        print("✅ Project handover endpoints correctly require authentication")


class TestCustomerPortalProjects:
    """P2: Customer Portal Projects Tab tests"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        return response.json().get("access_token")
    
    @pytest.fixture(scope="class")
    def customer_token(self, admin_token):
        """Get customer portal access token"""
        # First get portal access URL for test customer
        response = requests.post(
            f"{BASE_URL}/api/admin/customers/portal-access",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"email": "max@testfirma.de"}
        )
        if response.status_code != 200:
            pytest.skip("Could not get customer portal access")
        
        data = response.json()
        portal_url = data.get("portal_url", "")
        
        # Extract token from URL
        if "token=" in portal_url:
            token = portal_url.split("token=")[1].split("&")[0]
        else:
            pytest.skip("No token in portal URL")
        
        # Verify token
        verify_response = requests.post(
            f"{BASE_URL}/api/auth/verify-token",
            json={"token": token}
        )
        if verify_response.status_code != 200:
            pytest.skip("Token verification failed")
        
        return verify_response.json().get("access_token")
    
    def test_customer_projects_endpoint(self, customer_token):
        """GET /api/customer/projects returns customer's projects"""
        response = requests.get(
            f"{BASE_URL}/api/customer/projects",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        assert response.status_code == 200, f"Customer projects failed: {response.text}"
        data = response.json()
        
        assert "projects" in data, "Missing projects in response"
        assert isinstance(data["projects"], list), "Projects should be a list"
        
        if len(data["projects"]) > 0:
            project = data["projects"][0]
            assert "project_id" in project, "Project missing project_id"
            assert "title" in project, "Project missing title"
            assert "status" in project, "Project missing status"
        
        print(f"✅ Customer projects: {len(data['projects'])} projects found")
    
    def test_customer_project_detail(self, customer_token):
        """GET /api/customer/projects/{id} returns project detail"""
        # First get list of projects
        list_response = requests.get(
            f"{BASE_URL}/api/customer/projects",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        if list_response.status_code != 200:
            pytest.skip("Could not get projects list")
        
        projects = list_response.json().get("projects", [])
        if len(projects) == 0:
            pytest.skip("No projects available for customer")
        
        project_id = projects[0]["project_id"]
        
        response = requests.get(
            f"{BASE_URL}/api/customer/projects/{project_id}",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        assert response.status_code == 200, f"Project detail failed: {response.text}"
        data = response.json()
        
        assert "project_id" in data, "Missing project_id in detail"
        assert "title" in data, "Missing title in detail"
        
        print(f"✅ Customer project detail: {data.get('title', 'N/A')}")
    
    def test_customer_project_chat(self, customer_token):
        """POST /api/customer/projects/{id}/chat sends message"""
        # First get list of projects
        list_response = requests.get(
            f"{BASE_URL}/api/customer/projects",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        if list_response.status_code != 200:
            pytest.skip("Could not get projects list")
        
        projects = list_response.json().get("projects", [])
        if len(projects) == 0:
            pytest.skip("No projects available for customer")
        
        project_id = projects[0]["project_id"]
        
        response = requests.post(
            f"{BASE_URL}/api/customer/projects/{project_id}/chat",
            headers={"Authorization": f"Bearer {customer_token}", "Content-Type": "application/json"},
            json={"content": "TEST_chat_message_from_pytest"}
        )
        assert response.status_code == 200, f"Project chat failed: {response.text}"
        data = response.json()
        
        assert "message_id" in data or "success" in data or "message" in data, "Unexpected chat response"
        
        print(f"✅ Customer project chat: message sent successfully")
    
    def test_customer_projects_requires_auth(self):
        """Customer projects endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/customer/projects")
        assert response.status_code == 401, "Customer projects should require auth"
        print("✅ Customer projects correctly requires authentication")


class TestAdminNavItems:
    """Test that admin nav items are accessible"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        return response.json().get("access_token")
    
    def test_admin_stats_dashboard(self, admin_token):
        """Admin dashboard stats endpoint works"""
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Admin stats failed: {response.text}"
        print("✅ Admin dashboard stats accessible")
    
    def test_admin_projects_list(self, admin_token):
        """Admin projects list endpoint works"""
        response = requests.get(
            f"{BASE_URL}/api/admin/projects",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Admin projects failed: {response.text}"
        data = response.json()
        assert "projects" in data, "Missing projects in response"
        print(f"✅ Admin projects: {len(data['projects'])} projects")
    
    def test_admin_contracts_list(self, admin_token):
        """Admin contracts list endpoint works"""
        response = requests.get(
            f"{BASE_URL}/api/admin/contracts",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Admin contracts failed: {response.text}"
        data = response.json()
        assert "contracts" in data, "Missing contracts in response"
        print(f"✅ Admin contracts: {len(data['contracts'])} contracts")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
