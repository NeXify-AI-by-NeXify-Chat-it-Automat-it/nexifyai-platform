"""
NeXifyAI Iteration 58 - Contract Acceptance E2E Tests
=====================================================
Tests for NEW features in this iteration:
1. Public Contract Acceptance page at /vertrag?token=xxx&cid=xxx (no auth required)
2. Contract title field added
3. Contract value/calculation auto-computed (net, VAT 21%, gross)
4. Appendix creation tolerates both 'type' and 'appendix_type' fields
5. Full E2E Outbound Pipeline
6. Admin Login 2-step flow
7. All Admin navigation views (19 views)
8. Security headers verification
9. Public contract endpoints work WITHOUT auth token
"""

import pytest
import requests
import os
import time
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://contract-os.preview.emergentagent.com').rstrip('/')
ADMIN_EMAIL = "p.courbois@icloud.com"
ADMIN_PASSWORD = "1def!xO2022!!"


class TestHealthAndSecurity:
    """Health endpoint and security headers verification"""
    
    def test_health_endpoint(self):
        """Health endpoint returns healthy"""
        r = requests.get(f"{BASE_URL}/api/health")
        assert r.status_code == 200
        data = r.json()
        assert data.get("status") == "healthy"
        print(f"✓ Health endpoint: {data}")
    
    def test_security_headers_present(self):
        """Security headers are present (HSTS, X-Frame-Options)"""
        r = requests.get(f"{BASE_URL}/api/health")
        headers = r.headers
        
        # Check HSTS
        hsts = headers.get("Strict-Transport-Security", "")
        assert "max-age" in hsts, f"HSTS header missing or invalid: {hsts}"
        print(f"✓ HSTS: {hsts}")
        
        # Check X-Frame-Options
        xfo = headers.get("X-Frame-Options", "")
        assert xfo in ["DENY", "SAMEORIGIN"], f"X-Frame-Options missing or invalid: {xfo}"
        print(f"✓ X-Frame-Options: {xfo}")
        
        # Check X-Content-Type-Options
        xcto = headers.get("X-Content-Type-Options", "")
        assert xcto == "nosniff", f"X-Content-Type-Options missing: {xcto}"
        print(f"✓ X-Content-Type-Options: {xcto}")
    
    def test_admin_routes_require_auth(self):
        """Admin routes require authentication (401 without token)"""
        r = requests.get(f"{BASE_URL}/api/admin/stats")
        assert r.status_code == 401, f"Expected 401, got {r.status_code}"
        print("✓ Admin routes require auth (401 without token)")


class TestAdminLogin:
    """Admin login 2-step flow tests"""
    
    def test_admin_login_success(self):
        """Admin login with correct credentials"""
        r = requests.post(
            f"{BASE_URL}/api/admin/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=f"username={ADMIN_EMAIL}&password={ADMIN_PASSWORD}"
        )
        assert r.status_code == 200, f"Login failed: {r.status_code} - {r.text}"
        data = r.json()
        assert "access_token" in data, f"No access_token in response: {data}"
        print(f"✓ Admin login successful, token received")
        return data["access_token"]
    
    def test_admin_login_invalid_credentials(self):
        """Admin login with wrong password returns 401"""
        r = requests.post(
            f"{BASE_URL}/api/admin/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=f"username={ADMIN_EMAIL}&password=wrongpassword"
        )
        assert r.status_code == 401, f"Expected 401, got {r.status_code}"
        print("✓ Invalid credentials return 401")


class TestContractCreationWithTitleAndValue:
    """Contract creation with title and auto-calculated value"""
    
    @pytest.fixture
    def auth_token(self):
        """Get admin auth token"""
        r = requests.post(
            f"{BASE_URL}/api/admin/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=f"username={ADMIN_EMAIL}&password={ADMIN_PASSWORD}"
        )
        assert r.status_code == 200
        return r.json()["access_token"]
    
    def test_create_contract_with_title_and_value(self, auth_token):
        """Create contract with title and value=15000 → expect correct calculation"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        test_email = f"test_contract_{uuid.uuid4().hex[:8]}@e2e.de"
        payload = {
            "customer": {
                "email": test_email,
                "name": "E2E Test Kunde",
                "company": "E2E Test GmbH"
            },
            "title": "E2E Test Vertrag - Iteration 58",
            "value": 15000,
            "contract_type": "standard",
            "notes": "Created by iteration 58 test"
        }
        
        r = requests.post(f"{BASE_URL}/api/admin/contracts", headers=headers, json=payload)
        assert r.status_code == 200, f"Contract creation failed: {r.status_code} - {r.text}"
        
        data = r.json()
        assert "contract_id" in data, f"No contract_id in response: {data}"
        assert data.get("title") == "E2E Test Vertrag - Iteration 58", f"Title not saved: {data.get('title')}"
        
        # Verify calculation
        calc = data.get("calculation", {})
        assert calc.get("net_total") == 15000, f"Net total incorrect: {calc.get('net_total')}"
        assert calc.get("vat_rate") == 0.21, f"VAT rate incorrect: {calc.get('vat_rate')}"
        assert calc.get("vat_amount") == 3150, f"VAT amount incorrect: {calc.get('vat_amount')}"
        assert calc.get("gross_total") == 18150, f"Gross total incorrect: {calc.get('gross_total')}"
        
        print(f"✓ Contract created with title and correct calculation:")
        print(f"  - Contract ID: {data['contract_id']}")
        print(f"  - Title: {data.get('title')}")
        print(f"  - Net: {calc.get('net_total')} EUR")
        print(f"  - VAT (21%): {calc.get('vat_amount')} EUR")
        print(f"  - Gross: {calc.get('gross_total')} EUR")
        
        return data["contract_id"], test_email


class TestAppendixCreation:
    """Appendix creation tolerates both 'type' and 'appendix_type' fields"""
    
    @pytest.fixture
    def auth_token(self):
        """Get admin auth token"""
        r = requests.post(
            f"{BASE_URL}/api/admin/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=f"username={ADMIN_EMAIL}&password={ADMIN_PASSWORD}"
        )
        assert r.status_code == 200
        return r.json()["access_token"]
    
    @pytest.fixture
    def test_contract(self, auth_token):
        """Create a test contract for appendix tests"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        test_email = f"appendix_test_{uuid.uuid4().hex[:8]}@e2e.de"
        payload = {
            "customer": {"email": test_email, "name": "Appendix Test"},
            "title": "Appendix Test Contract",
            "value": 5000,
            "contract_type": "standard"
        }
        r = requests.post(f"{BASE_URL}/api/admin/contracts", headers=headers, json=payload)
        assert r.status_code == 200
        return r.json()["contract_id"]
    
    def test_appendix_with_appendix_type_field(self, auth_token, test_contract):
        """Create appendix using 'appendix_type' field"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        payload = {
            "appendix_type": "ai_agent",
            "title": "KI-Agent Modul",
            "content": {"scope": "Chatbot Integration", "value": 2500}
        }
        
        r = requests.post(f"{BASE_URL}/api/admin/contracts/{test_contract}/appendices", headers=headers, json=payload)
        assert r.status_code == 200, f"Appendix creation failed: {r.status_code} - {r.text}"
        
        data = r.json()
        assert data.get("appendix_type") == "ai_agent", f"appendix_type not saved: {data}"
        print(f"✓ Appendix created with 'appendix_type' field: {data.get('appendix_id')}")
    
    def test_appendix_with_type_field(self, auth_token, test_contract):
        """Create appendix using 'type' field (backward compatibility)"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        payload = {
            "type": "website",
            "title": "Website Modul",
            "content": {"scope": "Landing Page", "value": 3000}
        }
        
        r = requests.post(f"{BASE_URL}/api/admin/contracts/{test_contract}/appendices", headers=headers, json=payload)
        assert r.status_code == 200, f"Appendix creation with 'type' failed: {r.status_code} - {r.text}"
        
        data = r.json()
        assert data.get("appendix_type") == "website", f"type field not converted: {data}"
        print(f"✓ Appendix created with 'type' field (backward compat): {data.get('appendix_id')}")


class TestPublicContractAcceptanceE2E:
    """Full E2E test for public contract acceptance flow"""
    
    @pytest.fixture
    def auth_token(self):
        """Get admin auth token"""
        r = requests.post(
            f"{BASE_URL}/api/admin/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=f"username={ADMIN_EMAIL}&password={ADMIN_PASSWORD}"
        )
        assert r.status_code == 200
        return r.json()["access_token"]
    
    def test_full_contract_acceptance_e2e(self, auth_token):
        """
        Full E2E flow:
        1. Create contract with value=15000
        2. Add appendix
        3. Send contract → get magic link
        4. GET /api/public/contracts/view (no auth) → verify contract data
        5. POST /api/public/contracts/accept (no auth) → verify acceptance
        """
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        # Step 1: Create contract
        test_email = f"e2e_accept_{uuid.uuid4().hex[:8]}@e2e.de"
        contract_payload = {
            "customer": {
                "email": test_email,
                "name": "E2E Accept Test",
                "company": "E2E Accept GmbH"
            },
            "title": "E2E Acceptance Test Contract",
            "value": 15000,
            "contract_type": "standard"
        }
        
        r = requests.post(f"{BASE_URL}/api/admin/contracts", headers=headers, json=contract_payload)
        assert r.status_code == 200, f"Contract creation failed: {r.text}"
        contract = r.json()
        contract_id = contract["contract_id"]
        print(f"✓ Step 1: Contract created: {contract_id}")
        
        # Verify calculation
        calc = contract.get("calculation", {})
        assert calc.get("net_total") == 15000
        assert calc.get("vat_amount") == 3150
        assert calc.get("gross_total") == 18150
        print(f"  - Calculation verified: net={calc.get('net_total')}, vat={calc.get('vat_amount')}, gross={calc.get('gross_total')}")
        
        # Step 2: Add appendix
        appendix_payload = {
            "appendix_type": "ai_agent",
            "title": "KI-Agent Paket",
            "content": {"scope": "2 KI-Agenten", "value": 5000}
        }
        r = requests.post(f"{BASE_URL}/api/admin/contracts/{contract_id}/appendices", headers=headers, json=appendix_payload)
        assert r.status_code == 200, f"Appendix creation failed: {r.text}"
        print(f"✓ Step 2: Appendix added")
        
        # Step 3: Send contract → get magic link
        r = requests.post(f"{BASE_URL}/api/admin/contracts/{contract_id}/send", headers=headers, json={})
        assert r.status_code == 200, f"Contract send failed: {r.text}"
        send_data = r.json()
        assert send_data.get("sent") == True, f"Contract not sent: {send_data}"
        contract_link = send_data.get("contract_link", "")
        assert "token=" in contract_link and "cid=" in contract_link, f"Invalid contract link: {contract_link}"
        print(f"✓ Step 3: Contract sent, magic link generated")
        print(f"  - Link: {contract_link}")
        
        # Extract token and cid from link
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(contract_link)
        params = parse_qs(parsed.query)
        token = params.get("token", [""])[0]
        cid = params.get("cid", [""])[0]
        assert token and cid, f"Could not extract token/cid from link"
        
        # Step 4: GET /api/public/contracts/view (NO AUTH)
        r = requests.get(f"{BASE_URL}/api/public/contracts/view?token={token}&cid={cid}")
        assert r.status_code == 200, f"Public view failed: {r.status_code} - {r.text}"
        view_data = r.json()
        
        # Verify contract data
        assert view_data.get("contract_id") == contract_id
        assert view_data.get("title") == "E2E Acceptance Test Contract"
        assert "legal_module_definitions" in view_data, "legal_module_definitions missing"
        assert "calculation" in view_data, "calculation missing"
        assert view_data.get("calculation", {}).get("net_total") == 15000
        print(f"✓ Step 4: Public contract view works (no auth)")
        print(f"  - Title: {view_data.get('title')}")
        print(f"  - Legal modules: {len(view_data.get('legal_module_definitions', []))} defined")
        
        # Step 5: POST /api/public/contracts/accept (NO AUTH)
        # Get required legal modules
        legal_modules = view_data.get("legal_module_definitions", [])
        legal_accepted = {}
        for lm in legal_modules:
            if lm.get("required"):
                legal_accepted[lm["key"]] = True
        
        accept_payload = {
            "token": token,
            "contract_id": cid,
            "signature_type": "name",
            "signature_data": "E2E Test Signature",
            "legal_modules_accepted": legal_accepted,
            "customer_name": "E2E Accept Test"
        }
        
        r = requests.post(f"{BASE_URL}/api/public/contracts/accept", json=accept_payload)
        assert r.status_code == 200, f"Public accept failed: {r.status_code} - {r.text}"
        accept_data = r.json()
        assert accept_data.get("accepted") == True, f"Contract not accepted: {accept_data}"
        assert "evidence_id" in accept_data, f"No evidence_id: {accept_data}"
        print(f"✓ Step 5: Contract accepted via public endpoint (no auth)")
        print(f"  - Evidence ID: {accept_data.get('evidence_id')}")
        print(f"  - Status: {accept_data.get('status')}")
        
        print("\n✓✓✓ FULL E2E CONTRACT ACCEPTANCE FLOW PASSED ✓✓✓")


class TestPublicEndpointsNoAuth:
    """Verify public contract endpoints work WITHOUT auth token"""
    
    @pytest.fixture
    def contract_with_link(self):
        """Create a contract and send it to get a magic link"""
        # Login
        r = requests.post(
            f"{BASE_URL}/api/admin/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=f"username={ADMIN_EMAIL}&password={ADMIN_PASSWORD}"
        )
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        # Create contract
        test_email = f"public_test_{uuid.uuid4().hex[:8]}@e2e.de"
        r = requests.post(f"{BASE_URL}/api/admin/contracts", headers=headers, json={
            "customer": {"email": test_email, "name": "Public Test"},
            "title": "Public Endpoint Test",
            "value": 10000
        })
        contract_id = r.json()["contract_id"]
        
        # Send contract
        r = requests.post(f"{BASE_URL}/api/admin/contracts/{contract_id}/send", headers=headers, json={})
        link = r.json().get("contract_link", "")
        
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(link)
        params = parse_qs(parsed.query)
        return {
            "token": params.get("token", [""])[0],
            "cid": params.get("cid", [""])[0],
            "contract_id": contract_id
        }
    
    def test_public_view_no_auth_header(self, contract_with_link):
        """GET /api/public/contracts/view works without Authorization header"""
        token = contract_with_link["token"]
        cid = contract_with_link["cid"]
        
        # Make request WITHOUT any auth header
        r = requests.get(f"{BASE_URL}/api/public/contracts/view?token={token}&cid={cid}")
        assert r.status_code == 200, f"Public view should work without auth: {r.status_code}"
        data = r.json()
        assert data.get("contract_id") == cid
        print(f"✓ Public view works without auth header")
    
    def test_public_view_invalid_token(self):
        """GET /api/public/contracts/view with invalid token returns 403"""
        r = requests.get(f"{BASE_URL}/api/public/contracts/view?token=invalid_token&cid=invalid_cid")
        assert r.status_code == 403, f"Expected 403 for invalid token, got {r.status_code}"
        print(f"✓ Invalid token returns 403")


class TestAdminDashboardAndNavigation:
    """Admin dashboard and navigation views"""
    
    @pytest.fixture
    def auth_token(self):
        """Get admin auth token"""
        r = requests.post(
            f"{BASE_URL}/api/admin/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=f"username={ADMIN_EMAIL}&password={ADMIN_PASSWORD}"
        )
        assert r.status_code == 200
        return r.json()["access_token"]
    
    def test_dashboard_stats(self, auth_token):
        """Dashboard shows real stats"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        r = requests.get(f"{BASE_URL}/api/admin/stats", headers=headers)
        assert r.status_code == 200
        data = r.json()
        assert "leads_total" in data
        assert "bookings_total" in data
        print(f"✓ Dashboard stats: leads={data.get('leads_total')}, bookings={data.get('bookings_total')}")
    
    def test_admin_user_management_list(self, auth_token):
        """Admin user management - list users"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        r = requests.get(f"{BASE_URL}/api/admin/users", headers=headers)
        assert r.status_code == 200
        data = r.json()
        assert "users" in data
        print(f"✓ Admin users list: {len(data.get('users', []))} users")
    
    def test_webhook_event_store(self, auth_token):
        """Webhook event store shows events"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        r = requests.get(f"{BASE_URL}/api/admin/webhooks/events", headers=headers)
        assert r.status_code == 200
        data = r.json()
        assert "events" in data
        print(f"✓ Webhook events: {len(data.get('events', []))} events")


class TestOutboundPipeline:
    """Outbound pipeline E2E tests"""
    
    @pytest.fixture
    def auth_token(self):
        """Get admin auth token"""
        r = requests.post(
            f"{BASE_URL}/api/admin/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=f"username={ADMIN_EMAIL}&password={ADMIN_PASSWORD}"
        )
        assert r.status_code == 200
        return r.json()["access_token"]
    
    def test_outbound_pipeline_stats(self, auth_token):
        """Outbound pipeline returns stats"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        r = requests.get(f"{BASE_URL}/api/admin/outbound/pipeline", headers=headers)
        assert r.status_code == 200
        data = r.json()
        assert "total" in data or "pipeline" in data, f"Pipeline data missing: {data}"
        print(f"✓ Outbound pipeline stats: total={data.get('total')}, conversion={data.get('conversion_rate')}%")
    
    def test_outbound_discover_lead(self, auth_token):
        """Discover a new outbound lead"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        payload = {
            "name": f"E2E Test Company {uuid.uuid4().hex[:6]}",
            "website": "https://e2e-test.de",
            "industry": "IT",
            "email": f"e2e_{uuid.uuid4().hex[:8]}@test.de",
            "country": "DE",
            "notes": "Created by iteration 58 test"
        }
        
        r = requests.post(f"{BASE_URL}/api/admin/outbound/discover", headers=headers, json=payload)
        assert r.status_code == 200, f"Discover failed: {r.status_code} - {r.text}"
        data = r.json()
        lead_id = data.get("lead_id") or data.get("outbound_id") or data.get("outbound_lead_id")
        assert lead_id, f"No lead ID in response: {data}"
        print(f"✓ Outbound lead discovered: {lead_id}")
        return lead_id
    
    def test_outbound_leads_list(self, auth_token):
        """List outbound leads"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        r = requests.get(f"{BASE_URL}/api/admin/outbound/leads", headers=headers)
        assert r.status_code == 200
        data = r.json()
        assert "leads" in data
        print(f"✓ Outbound leads: {len(data.get('leads', []))} leads")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
