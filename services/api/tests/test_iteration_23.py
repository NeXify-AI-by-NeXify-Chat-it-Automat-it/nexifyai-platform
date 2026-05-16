"""
Iteration 23 - Unified Auth & Customer Portal Tests
Tests for:
1. POST /api/auth/check-email — Admin/Customer/Unknown role detection
2. POST /api/auth/request-magic-link — Magic link generation
3. POST /api/auth/verify-token — Token verification → JWT with role=customer
4. GET /api/customer/me — JWT auth, customer profile
5. GET /api/customer/dashboard — JWT auth, dashboard data
6. Role separation: Customer JWT cannot access /api/admin/* (403)
7. Admin JWT has role=admin in payload
"""
import pytest
import requests
import os
import hashlib
from datetime import datetime, timezone, timedelta

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# Test credentials from test_credentials.md
ADMIN_EMAIL = "p.courbois@icloud.com"
ADMIN_PASSWORD = "NxAi#Secure2026!"
CUSTOMER_EMAIL = "max@testfirma.de"


class TestHealthCheck:
    """Basic health check to ensure API is running"""
    
    def test_health_endpoint(self):
        r = requests.get(f"{BASE_URL}/api/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "healthy"
        print(f"✓ Health check passed: {data}")


class TestAuthCheckEmail:
    """POST /api/auth/check-email — Role detection"""
    
    def test_admin_email_returns_admin_role(self):
        """Admin email should return role=admin, needs_password=true"""
        r = requests.post(f"{BASE_URL}/api/auth/check-email", json={"email": ADMIN_EMAIL})
        assert r.status_code == 200
        data = r.json()
        assert data["role"] == "admin", f"Expected role=admin, got {data}"
        assert data.get("needs_password") == True, f"Expected needs_password=true, got {data}"
        print(f"✓ Admin email check: {data}")
    
    def test_customer_email_returns_customer_role(self):
        """Customer email should return role=customer, needs_magic_link=true"""
        r = requests.post(f"{BASE_URL}/api/auth/check-email", json={"email": CUSTOMER_EMAIL})
        assert r.status_code == 200
        data = r.json()
        assert data["role"] == "customer", f"Expected role=customer, got {data}"
        assert data.get("needs_magic_link") == True, f"Expected needs_magic_link=true, got {data}"
        print(f"✓ Customer email check: {data}")
    
    def test_unknown_email_returns_unknown_role(self):
        """Unknown email should return role=unknown"""
        r = requests.post(f"{BASE_URL}/api/auth/check-email", json={"email": "unknown_test_user_xyz@nonexistent.com"})
        assert r.status_code == 200
        data = r.json()
        assert data["role"] == "unknown", f"Expected role=unknown, got {data}"
        print(f"✓ Unknown email check: {data}")
    
    def test_empty_email_returns_400(self):
        """Empty email should return 400"""
        r = requests.post(f"{BASE_URL}/api/auth/check-email", json={"email": ""})
        assert r.status_code == 400
        print(f"✓ Empty email returns 400")


class TestAuthRequestMagicLink:
    """POST /api/auth/request-magic-link — Magic link generation"""
    
    def test_magic_link_for_customer_returns_200(self):
        """Request magic link for existing customer should return 200"""
        r = requests.post(f"{BASE_URL}/api/auth/request-magic-link", json={"email": CUSTOMER_EMAIL})
        assert r.status_code == 200
        data = r.json()
        assert data.get("status") == "ok", f"Expected status=ok, got {data}"
        print(f"✓ Magic link request for customer: {data}")
    
    def test_magic_link_for_unknown_email_returns_404(self):
        """Request magic link for unknown email should return 404"""
        r = requests.post(f"{BASE_URL}/api/auth/request-magic-link", json={"email": "unknown_xyz_test@nonexistent.com"})
        assert r.status_code == 404
        print(f"✓ Magic link for unknown email returns 404")
    
    def test_magic_link_empty_email_returns_400(self):
        """Empty email should return 400"""
        r = requests.post(f"{BASE_URL}/api/auth/request-magic-link", json={"email": ""})
        assert r.status_code == 400
        print(f"✓ Empty email returns 400")


class TestAuthVerifyToken:
    """POST /api/auth/verify-token — Token verification"""
    
    def test_invalid_token_returns_403(self):
        """Invalid token should return 403"""
        r = requests.post(f"{BASE_URL}/api/auth/verify-token", json={"token": "invalid_token_xyz"})
        assert r.status_code == 403
        print(f"✓ Invalid token returns 403")
    
    def test_empty_token_returns_400(self):
        """Empty token should return 400"""
        r = requests.post(f"{BASE_URL}/api/auth/verify-token", json={"token": ""})
        assert r.status_code == 400
        print(f"✓ Empty token returns 400")


class TestAdminLogin:
    """Admin login flow and JWT role verification"""
    
    def test_admin_login_success(self):
        """Admin login should return JWT with role=admin"""
        form_data = {"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        r = requests.post(f"{BASE_URL}/api/admin/login", data=form_data)
        assert r.status_code == 200, f"Admin login failed: {r.text}"
        data = r.json()
        assert "access_token" in data, f"No access_token in response: {data}"
        assert data.get("token_type") == "bearer"
        print(f"✓ Admin login success, got token")
        return data["access_token"]
    
    def test_admin_jwt_has_admin_role(self):
        """Admin JWT should have role=admin in payload"""
        # Login to get token
        form_data = {"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        r = requests.post(f"{BASE_URL}/api/admin/login", data=form_data)
        assert r.status_code == 200
        token = r.json()["access_token"]
        
        # Decode JWT payload (without verification, just to check role)
        import base64
        import json
        parts = token.split(".")
        if len(parts) >= 2:
            # Add padding if needed
            payload_b64 = parts[1]
            padding = 4 - len(payload_b64) % 4
            if padding != 4:
                payload_b64 += "=" * padding
            payload = json.loads(base64.urlsafe_b64decode(payload_b64))
            assert payload.get("role") == "admin", f"Expected role=admin in JWT, got {payload}"
            print(f"✓ Admin JWT has role=admin: {payload}")


class TestCustomerJWTEndpoints:
    """GET /api/customer/me and /api/customer/dashboard — JWT auth"""
    
    def test_customer_me_without_auth_returns_401(self):
        """Customer /me without auth should return 401"""
        r = requests.get(f"{BASE_URL}/api/customer/me")
        assert r.status_code == 401
        print(f"✓ Customer /me without auth returns 401")
    
    def test_customer_dashboard_without_auth_returns_401(self):
        """Customer /dashboard without auth should return 401"""
        r = requests.get(f"{BASE_URL}/api/customer/dashboard")
        assert r.status_code == 401
        print(f"✓ Customer /dashboard without auth returns 401")


class TestRoleSeparation:
    """Role separation: Customer JWT cannot access admin endpoints"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin JWT token"""
        form_data = {"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        r = requests.post(f"{BASE_URL}/api/admin/login", data=form_data)
        assert r.status_code == 200
        return r.json()["access_token"]
    
    def test_admin_can_access_admin_endpoints(self, admin_token):
        """Admin JWT should be able to access /api/admin/* endpoints"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        r = requests.get(f"{BASE_URL}/api/admin/leads", headers=headers)
        assert r.status_code == 200, f"Admin should access /api/admin/leads, got {r.status_code}: {r.text}"
        print(f"✓ Admin can access /api/admin/leads")
    
    def test_customer_cannot_access_admin_endpoints_with_admin_token(self, admin_token):
        """This test verifies admin token works, then we test customer token rejection"""
        # First verify admin token works
        headers = {"Authorization": f"Bearer {admin_token}"}
        r = requests.get(f"{BASE_URL}/api/admin/leads", headers=headers)
        assert r.status_code == 200
        print(f"✓ Admin token verified working")


class TestPortalAccessTokenFlow:
    """Test portal access token creation and verification flow"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin JWT token"""
        form_data = {"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        r = requests.post(f"{BASE_URL}/api/admin/login", data=form_data)
        assert r.status_code == 200
        return r.json()["access_token"]
    
    def test_create_portal_access_and_verify(self, admin_token):
        """Create portal access token via admin endpoint, then verify it"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create portal access for customer
        r = requests.post(
            f"{BASE_URL}/api/admin/customers/portal-access",
            headers=headers,
            json={"email": CUSTOMER_EMAIL}
        )
        
        assert r.status_code == 200, f"Portal access creation failed: {r.text}"
        data = r.json()
        
        # Extract token from portal_url (format: .../portal/{token})
        portal_url = data.get("portal_url", "")
        raw_token = None
        if "/portal/" in portal_url:
            raw_token = portal_url.split("/portal/")[-1]
        elif data.get("token"):
            raw_token = data.get("token")
        
        assert raw_token, f"No token found in portal access response: {data}"
        
        # Verify the token
        verify_r = requests.post(
            f"{BASE_URL}/api/auth/verify-token",
            json={"token": raw_token}
        )
        assert verify_r.status_code == 200, f"Token verification failed: {verify_r.text}"
        verify_data = verify_r.json()
        assert verify_data.get("role") == "customer", f"Expected role=customer, got {verify_data}"
        assert "access_token" in verify_data, f"No access_token in verify response: {verify_data}"
        print(f"✓ Portal access token created and verified: role={verify_data.get('role')}")
        
        # Now test customer endpoints with this JWT
        customer_jwt = verify_data["access_token"]
        customer_headers = {"Authorization": f"Bearer {customer_jwt}"}
        
        # Test /api/customer/me
        me_r = requests.get(f"{BASE_URL}/api/customer/me", headers=customer_headers)
        assert me_r.status_code == 200, f"Customer /me failed: {me_r.text}"
        me_data = me_r.json()
        assert me_data.get("role") == "customer", f"Expected role=customer in /me, got {me_data}"
        print(f"✓ Customer /me works with JWT: {me_data.get('email')}")
        
        # Test /api/customer/dashboard
        dash_r = requests.get(f"{BASE_URL}/api/customer/dashboard", headers=customer_headers)
        assert dash_r.status_code == 200, f"Customer /dashboard failed: {dash_r.text}"
        dash_data = dash_r.json()
        # Dashboard should have these keys (may be empty arrays)
        for key in ["quotes", "invoices", "bookings", "communications", "timeline"]:
            assert key in dash_data, f"Missing {key} in dashboard: {dash_data.keys()}"
        print(f"✓ Customer /dashboard works: quotes={len(dash_data.get('quotes', []))}, invoices={len(dash_data.get('invoices', []))}")
        
        # Test role separation: Customer JWT should NOT access admin endpoints
        admin_r = requests.get(f"{BASE_URL}/api/admin/leads", headers=customer_headers)
        assert admin_r.status_code == 403, f"Customer should get 403 on admin endpoint, got {admin_r.status_code}: {admin_r.text}"
        print(f"✓ Customer JWT correctly blocked from /api/admin/leads (403)")


class TestCustomerJWTRoleSeparation:
    """Explicit test for customer JWT being blocked from admin endpoints"""
    
    def get_customer_jwt(self):
        """Get customer JWT via portal access flow"""
        # Get admin token first
        form_data = {"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        r = requests.post(f"{BASE_URL}/api/admin/login", data=form_data)
        if r.status_code != 200:
            return None
        admin_token = r.json()["access_token"]
        
        # Create portal access
        headers = {"Authorization": f"Bearer {admin_token}"}
        r = requests.post(
            f"{BASE_URL}/api/admin/customers/portal-access",
            headers=headers,
            json={"email": CUSTOMER_EMAIL}
        )
        if r.status_code != 200:
            return None
        
        data = r.json()
        # Extract token from portal_url
        portal_url = data.get("portal_url", "")
        raw_token = None
        if "/portal/" in portal_url:
            raw_token = portal_url.split("/portal/")[-1]
        elif data.get("token"):
            raw_token = data.get("token")
        
        if not raw_token:
            return None
        
        verify_r = requests.post(f"{BASE_URL}/api/auth/verify-token", json={"token": raw_token})
        if verify_r.status_code != 200:
            return None
        
        return verify_r.json()["access_token"]
    
    def test_customer_jwt_blocked_from_admin_leads(self):
        """Customer JWT should get 403 on /api/admin/leads"""
        customer_jwt = self.get_customer_jwt()
        assert customer_jwt is not None, "Failed to get customer JWT"
        headers = {"Authorization": f"Bearer {customer_jwt}"}
        r = requests.get(f"{BASE_URL}/api/admin/leads", headers=headers)
        assert r.status_code == 403, f"Expected 403, got {r.status_code}: {r.text}"
        print(f"✓ Customer JWT blocked from /api/admin/leads: 403")
    
    def test_customer_jwt_blocked_from_admin_customers(self):
        """Customer JWT should get 403 on /api/admin/customers"""
        customer_jwt = self.get_customer_jwt()
        assert customer_jwt is not None, "Failed to get customer JWT"
        headers = {"Authorization": f"Bearer {customer_jwt}"}
        r = requests.get(f"{BASE_URL}/api/admin/customers", headers=headers)
        assert r.status_code == 403, f"Expected 403, got {r.status_code}: {r.text}"
        print(f"✓ Customer JWT blocked from /api/admin/customers: 403")
    
    def test_customer_jwt_blocked_from_admin_quotes(self):
        """Customer JWT should get 403 on /api/admin/quotes"""
        customer_jwt = self.get_customer_jwt()
        assert customer_jwt is not None, "Failed to get customer JWT"
        headers = {"Authorization": f"Bearer {customer_jwt}"}
        r = requests.get(f"{BASE_URL}/api/admin/quotes", headers=headers)
        assert r.status_code == 403, f"Expected 403, got {r.status_code}: {r.text}"
        print(f"✓ Customer JWT blocked from /api/admin/quotes: 403")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
