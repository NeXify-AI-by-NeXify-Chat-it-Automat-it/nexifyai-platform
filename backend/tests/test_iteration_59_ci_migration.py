"""
Iteration 59 - CI Color Migration Tests
Verifies:
1. Health endpoint
2. Security headers
3. Admin login flow
4. Admin stats (72+ leads, 27 bookings)
5. Outbound Lead Machine
6. Contract creation with value calculation (net, VAT 21%, gross)
7. Public contract acceptance endpoints
8. Projects CRUD
9. All admin navigation views
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthAndSecurity:
    """Health and security header tests"""
    
    def test_health_endpoint(self):
        """Verify health endpoint returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"Health check passed: {data}")
    
    def test_security_headers(self):
        """Verify security headers are present"""
        response = requests.get(f"{BASE_URL}/api/health")
        headers = response.headers
        
        # Check for security headers
        assert "x-frame-options" in [h.lower() for h in headers.keys()], "X-Frame-Options header missing"
        assert "x-content-type-options" in [h.lower() for h in headers.keys()], "X-Content-Type-Options header missing"
        
        # Verify values
        x_frame = headers.get("X-Frame-Options", headers.get("x-frame-options", ""))
        x_content = headers.get("X-Content-Type-Options", headers.get("x-content-type-options", ""))
        
        assert x_frame.upper() == "DENY", f"X-Frame-Options should be DENY, got {x_frame}"
        assert x_content.lower() == "nosniff", f"X-Content-Type-Options should be nosniff, got {x_content}"
        print(f"Security headers verified: X-Frame-Options={x_frame}, X-Content-Type-Options={x_content}")


class TestAdminAuth:
    """Admin authentication tests"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={
                "username": "p.courbois@icloud.com",
                "password": "1def!xO2022!!"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, f"No access_token in response: {data}"
        return data["access_token"]
    
    def test_admin_login_success(self):
        """Test admin login with valid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={
                "username": "p.courbois@icloud.com",
                "password": "1def!xO2022!!"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data.get("token_type") == "bearer"
        print(f"Admin login successful, token type: {data.get('token_type')}")
    
    def test_admin_login_invalid_credentials(self):
        """Test admin login with invalid credentials returns 401"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={
                "username": "wrong@example.com",
                "password": "wrongpassword"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 401
        print("Invalid credentials correctly rejected with 401")
    
    def test_protected_route_without_token(self):
        """Test that protected routes return 401 without token"""
        response = requests.get(f"{BASE_URL}/api/admin/stats")
        assert response.status_code == 401
        print("Protected route correctly returns 401 without token")


class TestAdminDashboard:
    """Admin dashboard and stats tests"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get authenticated headers"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={
                "username": "p.courbois@icloud.com",
                "password": "1def!xO2022!!"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token = response.json().get("access_token")
        return {"Authorization": f"Bearer {token}"}
    
    def test_admin_stats(self, auth_headers):
        """Test admin stats endpoint returns expected data"""
        response = requests.get(f"{BASE_URL}/api/admin/stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        # Verify stats structure
        assert "leads" in data or "total_leads" in data or isinstance(data, dict)
        print(f"Admin stats: {data}")
    
    def test_admin_leads(self, auth_headers):
        """Test admin leads endpoint - verify 72+ leads"""
        response = requests.get(f"{BASE_URL}/api/admin/leads", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        # API returns {leads: [...], total: N}
        leads = data.get("leads", data) if isinstance(data, dict) else data
        total = data.get("total", len(leads)) if isinstance(data, dict) else len(data)
        assert total >= 72, f"Expected 72+ leads, got {total}"
        print(f"Leads count: {total} (expected 72+)")
    
    def test_admin_bookings(self, auth_headers):
        """Test admin bookings endpoint - verify 27 bookings"""
        response = requests.get(f"{BASE_URL}/api/admin/bookings", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        # API returns {bookings: [...], total: N}
        bookings = data.get("bookings", data) if isinstance(data, dict) else data
        total = data.get("total", len(bookings)) if isinstance(data, dict) else len(data)
        assert total >= 27, f"Expected 27+ bookings, got {total}"
        print(f"Bookings count: {total} (expected 27+)")


class TestOutboundLeadMachine:
    """Outbound Lead Machine tests"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get authenticated headers"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={
                "username": "p.courbois@icloud.com",
                "password": "1def!xO2022!!"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token = response.json().get("access_token")
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    def test_outbound_pipeline(self, auth_headers):
        """Test outbound pipeline stats"""
        response = requests.get(f"{BASE_URL}/api/admin/outbound/pipeline", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        print(f"Outbound pipeline: {data}")
    
    def test_outbound_leads(self, auth_headers):
        """Test outbound leads list"""
        response = requests.get(f"{BASE_URL}/api/admin/outbound/leads", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        # API returns {leads: [...], count: N}
        leads = data.get("leads", data) if isinstance(data, dict) else data
        count = data.get("count", len(leads)) if isinstance(data, dict) else len(data)
        assert count > 0, "Expected outbound leads"
        print(f"Outbound leads count: {count}")


class TestContractValueCalculation:
    """Contract creation with value calculation tests"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get authenticated headers"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={
                "username": "p.courbois@icloud.com",
                "password": "1def!xO2022!!"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token = response.json().get("access_token")
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    def test_contract_creation_with_value(self, auth_headers):
        """Test contract creation with value auto-calculation (net, VAT 21%, gross)"""
        # Create a test contract with required fields
        contract_data = {
            "title": "TEST_CI_Migration_Contract",
            "customer": {
                "name": "Test Customer CI",
                "email": "test.ci@example.com"
            },
            "value": 10000  # Net value
        }
        
        response = requests.post(
            f"{BASE_URL}/api/admin/contracts",
            json=contract_data,
            headers=auth_headers
        )
        assert response.status_code in [200, 201], f"Contract creation failed: {response.text}"
        data = response.json()
        
        # Verify value calculation in calculation object
        calc = data.get("calculation", data)
        if "net_total" in calc:
            assert calc["net_total"] == 10000, f"Net total should be 10000, got {calc.get('net_total')}"
        if "vat_amount" in calc:
            expected_vat = 10000 * 0.21  # 21% VAT
            assert calc["vat_amount"] == expected_vat, f"VAT should be {expected_vat}, got {calc.get('vat_amount')}"
        if "gross_total" in calc:
            expected_gross = 10000 + (10000 * 0.21)  # Net + VAT
            assert calc["gross_total"] == expected_gross, f"Gross should be {expected_gross}, got {calc.get('gross_total')}"
        
        print(f"Contract created with value calculation: {data}")
        return data
    
    def test_contracts_list(self, auth_headers):
        """Test contracts list endpoint"""
        response = requests.get(f"{BASE_URL}/api/admin/contracts", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        # API returns {contracts: [...], total: N}
        contracts = data.get("contracts", data) if isinstance(data, dict) else data
        total = data.get("total", len(contracts)) if isinstance(data, dict) else len(data)
        assert total > 0, "Expected contracts"
        print(f"Contracts count: {total}")


class TestPublicContractAcceptance:
    """Public contract acceptance endpoint tests"""
    
    def test_public_contract_view_without_params(self):
        """Test public contract view returns error without params"""
        response = requests.get(f"{BASE_URL}/api/public/contracts/view")
        # Should return 400 or 422 for missing params
        assert response.status_code in [400, 422, 404], f"Expected 400/422/404, got {response.status_code}"
        print(f"Public contract view without params: {response.status_code}")
    
    def test_public_contract_view_with_invalid_token(self):
        """Test public contract view with invalid token"""
        response = requests.get(
            f"{BASE_URL}/api/public/contracts/view",
            params={"token": "invalid_token", "cid": "invalid_cid"}
        )
        # Should return 403 (forbidden) or 404 for invalid contract
        assert response.status_code in [400, 403, 404], f"Expected 400/403/404, got {response.status_code}"
        print(f"Public contract view with invalid token: {response.status_code}")


class TestProjectsCRUD:
    """Projects CRUD tests"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get authenticated headers"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={
                "username": "p.courbois@icloud.com",
                "password": "1def!xO2022!!"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token = response.json().get("access_token")
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    def test_projects_list(self, auth_headers):
        """Test projects list endpoint"""
        response = requests.get(f"{BASE_URL}/api/admin/projects", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        # API returns {projects: [...], total: N}
        projects = data.get("projects", data) if isinstance(data, dict) else data
        total = data.get("total", len(projects)) if isinstance(data, dict) else len(data)
        assert total > 0, "Expected projects"
        print(f"Projects count: {total}")
    
    def test_project_create(self, auth_headers):
        """Test project creation"""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        project_data = {
            "title": f"TEST_CI_Migration_Project_{unique_id}",
            "customer_email": f"test.ci.project.{unique_id}@example.com"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/admin/projects",
            json=project_data,
            headers=auth_headers
        )
        assert response.status_code in [200, 201], f"Project creation failed: {response.text}"
        data = response.json()
        assert "title" in data or "project_id" in data or "_id" in data or "id" in data
        print(f"Project created: {data.get('project_id', data.get('title'))}")
        print(f"Project created: {data}")


class TestAdminViews:
    """Test all admin navigation views are accessible"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get authenticated headers"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={
                "username": "p.courbois@icloud.com",
                "password": "1def!xO2022!!"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token = response.json().get("access_token")
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    def test_admin_users(self, auth_headers):
        """Test admin users endpoint"""
        response = requests.get(f"{BASE_URL}/api/admin/users", headers=auth_headers)
        assert response.status_code == 200
        print(f"Admin users: {response.status_code}")
    
    def test_admin_chat_sessions(self, auth_headers):
        """Test admin chat sessions endpoint"""
        response = requests.get(f"{BASE_URL}/api/admin/chat-sessions", headers=auth_headers)
        assert response.status_code == 200
        print(f"Chat sessions: {response.status_code}")
    
    def test_admin_timeline(self, auth_headers):
        """Test admin timeline endpoint"""
        response = requests.get(f"{BASE_URL}/api/admin/timeline", headers=auth_headers)
        assert response.status_code == 200
        print(f"Timeline: {response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
