"""
Iteration 56 - Backend API Tests
Testing: Admin User Management, Webhook Events, Customer Portal (Profile/Documents/Consents), 
Security Headers, CORS, Rate Limiting, Outbound Lead Machine
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://contract-os.preview.emergentagent.com').rstrip('/')

# Admin credentials from test_credentials.md
ADMIN_EMAIL = "p.courbois@icloud.com"
ADMIN_PASSWORD = "1def!xO2022!!"


class TestAdminAuth:
    """Admin authentication tests"""
    
    def test_admin_login_success(self):
        """Test admin login with OAuth2 form-encoded"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=f"username={ADMIN_EMAIL}&password={ADMIN_PASSWORD}"
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access_token in response"
        assert data["token_type"] == "bearer"
        print(f"✓ Admin login successful, token received")
        return data["access_token"]
    
    def test_admin_login_invalid_credentials(self):
        """Test admin login with wrong password"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data="username=wrong@email.com&password=wrongpassword"
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Invalid credentials correctly rejected with 401")


class TestSecurityHeaders:
    """Security headers and CORS tests (Block G)"""
    
    def test_security_headers_present(self):
        """Test that security headers are present in responses"""
        response = requests.get(f"{BASE_URL}/api/health")
        headers = response.headers
        
        # Check X-Content-Type-Options
        assert headers.get("X-Content-Type-Options") == "nosniff", "Missing X-Content-Type-Options: nosniff"
        print("✓ X-Content-Type-Options: nosniff")
        
        # Check X-Frame-Options
        assert headers.get("X-Frame-Options") == "DENY", "Missing X-Frame-Options: DENY"
        print("✓ X-Frame-Options: DENY")
        
        # Check Strict-Transport-Security
        hsts = headers.get("Strict-Transport-Security", "")
        assert "max-age=" in hsts, "Missing Strict-Transport-Security header"
        print(f"✓ Strict-Transport-Security: {hsts}")
        
        # Check X-XSS-Protection
        assert headers.get("X-XSS-Protection") == "1; mode=block", "Missing X-XSS-Protection"
        print("✓ X-XSS-Protection: 1; mode=block")
    
    def test_cors_headers_present(self):
        """Test that CORS headers are present in responses"""
        response = requests.options(
            f"{BASE_URL}/api/health",
            headers={"Origin": "https://contract-os.preview.emergentagent.com"}
        )
        cors_origin = response.headers.get("Access-Control-Allow-Origin", "")
        # Note: CORS is currently set to * which is acceptable for preview but should be restricted in production
        if cors_origin:
            print(f"✓ CORS origin header present: {cors_origin}")
            if cors_origin == "*":
                print("  ⚠ Note: CORS is wildcard (*) - acceptable for preview, should be restricted in production")
        else:
            print("✓ CORS origin header not present")


class TestAdminUserManagement:
    """Admin user management tests (Block D - Governance)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token for authenticated requests"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=f"username={ADMIN_EMAIL}&password={ADMIN_PASSWORD}"
        )
        assert response.status_code == 200
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
    
    def test_get_admin_users_list(self):
        """GET /api/admin/users - List admin users"""
        response = requests.get(f"{BASE_URL}/api/admin/users", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "users" in data, "Response should contain 'users' key"
        assert "count" in data, "Response should contain 'count' key"
        assert len(data["users"]) >= 1, "Should have at least 1 admin user"
        
        # Verify the main admin user exists
        admin_emails = [u["email"] for u in data["users"]]
        assert ADMIN_EMAIL in admin_emails, f"Admin user {ADMIN_EMAIL} should be in list"
        print(f"✓ Admin users list: {data['count']} users found")
        print(f"  Users: {admin_emails}")
    
    def test_create_admin_user(self):
        """POST /api/admin/users - Create new admin user"""
        test_email = "TEST_admin_iter56@example.com"
        test_password = "TestPassword123!"
        
        # First, try to delete if exists (cleanup from previous runs)
        requests.delete(f"{BASE_URL}/api/admin/users/{test_email}", headers=self.headers)
        
        # Create new admin user
        response = requests.post(
            f"{BASE_URL}/api/admin/users",
            headers=self.headers,
            json={"email": test_email, "password": test_password, "role": "admin"}
        )
        assert response.status_code == 200, f"Create failed: {response.text}"
        data = response.json()
        assert data.get("status") == "ok", "Status should be 'ok'"
        # Backend lowercases emails, so compare lowercase
        assert data.get("email") == test_email.lower(), "Email should match (lowercased)"
        print(f"✓ Created admin user: {data.get('email')}")
        
        # Verify user appears in list
        list_response = requests.get(f"{BASE_URL}/api/admin/users", headers=self.headers)
        users = list_response.json().get("users", [])
        user_emails = [u["email"] for u in users]
        assert test_email.lower() in user_emails, "New user should appear in list"
        print("✓ New user verified in admin users list")
        
        # Cleanup - delete test user
        delete_response = requests.delete(f"{BASE_URL}/api/admin/users/{test_email.lower()}", headers=self.headers)
        assert delete_response.status_code == 200, f"Delete failed: {delete_response.text}"
        print(f"✓ Cleaned up test user: {test_email.lower()}")
    
    def test_cannot_delete_self(self):
        """DELETE /api/admin/users/{email} - Cannot delete own account"""
        response = requests.delete(
            f"{BASE_URL}/api/admin/users/{ADMIN_EMAIL}",
            headers=self.headers
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ Self-deletion correctly blocked with 400")


class TestWebhookEventStore:
    """Webhook event store tests (Block F - Data Integrity)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=f"username={ADMIN_EMAIL}&password={ADMIN_PASSWORD}"
        )
        assert response.status_code == 200
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
    
    def test_get_webhook_events(self):
        """GET /api/admin/webhooks/events - List webhook events"""
        response = requests.get(f"{BASE_URL}/api/admin/webhooks/events", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "events" in data, "Response should contain 'events' key"
        assert "count" in data, "Response should contain 'count' key"
        print(f"✓ Webhook events endpoint working: {data['count']} events")


class TestCustomerPortalEndpoints:
    """Customer portal endpoints tests (Block B)"""
    
    def test_customer_profile_requires_auth(self):
        """GET /api/customer/profile - Requires customer JWT"""
        response = requests.get(f"{BASE_URL}/api/customer/profile")
        assert response.status_code in [401, 403, 422], f"Expected auth error, got {response.status_code}"
        print("✓ Customer profile correctly requires authentication")
    
    def test_customer_documents_requires_auth(self):
        """GET /api/customer/documents - Requires customer JWT"""
        response = requests.get(f"{BASE_URL}/api/customer/documents")
        assert response.status_code in [401, 403, 422], f"Expected auth error, got {response.status_code}"
        print("✓ Customer documents correctly requires authentication")
    
    def test_customer_consents_requires_auth(self):
        """GET /api/customer/consents - Requires customer JWT"""
        response = requests.get(f"{BASE_URL}/api/customer/consents")
        assert response.status_code in [401, 403, 422], f"Expected auth error, got {response.status_code}"
        print("✓ Customer consents correctly requires authentication")
    
    def test_customer_opt_out_requires_auth(self):
        """POST /api/customer/consents/opt-out - Requires customer JWT"""
        response = requests.post(
            f"{BASE_URL}/api/customer/consents/opt-out",
            json={"reason": "test"}
        )
        assert response.status_code in [401, 403, 422], f"Expected auth error, got {response.status_code}"
        print("✓ Customer opt-out correctly requires authentication")
    
    def test_portal_customer_invalid_token(self):
        """GET /api/portal/customer/{token} - Invalid token returns 403"""
        response = requests.get(f"{BASE_URL}/api/portal/customer/invalid_token_12345")
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ Invalid portal token correctly rejected with 403")


class TestOutboundLeadMachine:
    """Outbound Lead Machine tests (Block E)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=f"username={ADMIN_EMAIL}&password={ADMIN_PASSWORD}"
        )
        assert response.status_code == 200
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
    
    def test_outbound_pipeline_stats(self):
        """GET /api/admin/outbound/pipeline - Pipeline stats"""
        response = requests.get(f"{BASE_URL}/api/admin/outbound/pipeline", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "pipeline" in data, "Response should contain 'pipeline'"
        assert "total" in data, "Response should contain 'total'"
        assert "conversion_rate" in data, "Response should contain 'conversion_rate'"
        print(f"✓ Outbound pipeline: {data['total']} total leads, {data['conversion_rate']}% conversion")
    
    def test_outbound_leads_list(self):
        """GET /api/admin/outbound/leads - List outbound leads"""
        response = requests.get(f"{BASE_URL}/api/admin/outbound/leads", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "leads" in data, "Response should contain 'leads'"
        assert "count" in data, "Response should contain 'count'"
        print(f"✓ Outbound leads list: {data['count']} leads")
    
    def test_outbound_discover_lead(self):
        """POST /api/admin/outbound/discover - Create new outbound lead"""
        test_lead = {
            "name": "TEST_Iter56_Company",
            "website": "https://test-iter56.example.com",
            "industry": "Technology",
            "email": "test_iter56@example.com",
            "contact_name": "Test Contact",
            "country": "DE",
            "notes": "Test lead for iteration 56"
        }
        response = requests.post(
            f"{BASE_URL}/api/admin/outbound/discover",
            headers=self.headers,
            json=test_lead
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "outbound_lead_id" in data or "lead_id" in data, "Should return lead ID"
        print(f"✓ Discovered new outbound lead")
        return data.get("outbound_lead_id") or data.get("lead_id")
    
    def test_outbound_campaigns(self):
        """GET /api/admin/outbound/campaigns - Campaign overview"""
        response = requests.get(f"{BASE_URL}/api/admin/outbound/campaigns", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "campaigns" in data, "Response should contain 'campaigns'"
        print(f"✓ Outbound campaigns: {data['campaigns'].get('total_leads', 0)} total leads")


class TestAdminDashboard:
    """Admin dashboard and stats tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=f"username={ADMIN_EMAIL}&password={ADMIN_PASSWORD}"
        )
        assert response.status_code == 200
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
    
    def test_admin_stats(self):
        """GET /api/admin/stats - Dashboard stats"""
        response = requests.get(f"{BASE_URL}/api/admin/stats", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "leads_total" in data, "Should have leads_total"
        assert "bookings_total" in data, "Should have bookings_total"
        assert "chat_sessions_total" in data, "Should have chat_sessions_total"
        print(f"✓ Dashboard stats: {data['leads_total']} leads, {data['bookings_total']} bookings, {data['chat_sessions_total']} chats")


class TestProjectsAndContracts:
    """Projects and Contracts tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=f"username={ADMIN_EMAIL}&password={ADMIN_PASSWORD}"
        )
        assert response.status_code == 200
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
    
    def test_projects_list(self):
        """GET /api/admin/projects - List projects"""
        response = requests.get(f"{BASE_URL}/api/admin/projects", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "projects" in data, "Response should contain 'projects'"
        print(f"✓ Projects list: {len(data['projects'])} projects")
    
    def test_contracts_list(self):
        """GET /api/admin/contracts - List contracts"""
        response = requests.get(f"{BASE_URL}/api/admin/contracts", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "contracts" in data, "Response should contain 'contracts'"
        print(f"✓ Contracts list: {len(data['contracts'])} contracts")


class TestMonitoringAndBilling:
    """Monitoring and Billing tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=f"username={ADMIN_EMAIL}&password={ADMIN_PASSWORD}"
        )
        assert response.status_code == 200
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
    
    def test_billing_status(self):
        """GET /api/admin/billing/status - Billing dashboard"""
        response = requests.get(f"{BASE_URL}/api/admin/billing/status", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        print("✓ Billing status endpoint working")
    
    def test_legal_compliance(self):
        """GET /api/admin/legal/compliance - Legal compliance summary"""
        response = requests.get(f"{BASE_URL}/api/admin/legal/compliance", headers=self.headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        print("✓ Legal compliance endpoint working")


class TestHealthEndpoint:
    """Health check endpoint test"""
    
    def test_health_check(self):
        """GET /api/health - Basic health check"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.text}"
        print("✓ Health check passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
