"""
Iteration 37 Tests: Cookie Banner Fix, Monitoring Dashboard, Email Delivery, E2E Flow Verification
Tests for:
- GET /api/admin/monitoring/status — Full system monitoring data
- GET /api/admin/email/stats — Email delivery statistics and history
- POST /api/admin/email/test — Test email sending via Resend
- POST /api/admin/billing/reconcile — Reconciliation across all entities
- GET /api/admin/webhooks/history — Webhook audit log
- POST /api/admin/e2e/verify-flow — E2E flow verification
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

@pytest.fixture(scope="module")
def admin_token():
    """Get admin authentication token"""
    response = requests.post(
        f"{BASE_URL}/api/admin/login",
        data={"username": "p.courbois@icloud.com", "password": "NxAi#Secure2026!"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Admin authentication failed")

@pytest.fixture
def auth_headers(admin_token):
    """Headers with admin auth token"""
    return {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}


class TestHealthAndBasics:
    """Basic health checks"""
    
    def test_api_health(self):
        """Test API health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        print(f"✅ API Health: {data['status']}, version: {data['version']}")


class TestMonitoringDashboard:
    """P7: Monitoring Dashboard - Consolidated System Status"""
    
    def test_monitoring_status_endpoint(self, auth_headers):
        """GET /api/admin/monitoring/status — Full system monitoring data"""
        response = requests.get(f"{BASE_URL}/api/admin/monitoring/status", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        # Check structure
        assert "timestamp" in data
        assert "systems" in data
        assert "overall_status" in data
        
        systems = data["systems"]
        
        # Check all required system status cards
        required_systems = ["api", "database", "workers", "email", "payments", "webhooks", "memory_audit", "llm", "dead_letter_queue"]
        for sys_name in required_systems:
            assert sys_name in systems, f"Missing system: {sys_name}"
            print(f"  ✅ {sys_name}: {systems[sys_name].get('status', 'present')}")
        
        # Validate API status
        assert systems["api"]["status"] == "ok"
        assert "version" in systems["api"]
        
        # Validate Database status
        assert systems["database"]["status"] == "ok"
        assert "collections" in systems["database"]
        
        # Validate Email status
        assert "provider" in systems["email"]
        assert "api_key_set" in systems["email"]
        
        # Validate LLM status
        assert "active_provider" in systems["llm"]
        
        # Validate Payments status
        assert "revolut" in systems["payments"]
        assert "stripe" in systems["payments"]
        
        print(f"✅ Monitoring Status: {data['overall_status']}")
        print(f"  - API: {systems['api']['status']}, DB: {systems['database']['status']}")
        print(f"  - Email: {systems['email']['status']}, LLM: {systems['llm']['active_provider']}")
        print(f"  - Dead Letter Queue: {systems['dead_letter_queue']['count']} items")


class TestEmailDelivery:
    """P3: Resend E-Mail with Audit Trail"""
    
    def test_email_stats_endpoint(self, auth_headers):
        """GET /api/admin/email/stats — Email delivery statistics and history"""
        response = requests.get(f"{BASE_URL}/api/admin/email/stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        # Check structure
        assert "total" in data
        assert "sent" in data
        assert "failed" in data
        assert "success_rate" in data
        assert "resend_configured" in data
        assert "sender" in data
        assert "recent_events" in data
        
        print(f"✅ Email Stats: Total={data['total']}, Sent={data['sent']}, Failed={data['failed']}")
        print(f"  - Success Rate: {data['success_rate']}")
        print(f"  - Resend Configured: {data['resend_configured']}")
        print(f"  - Sender: {data['sender']}")
        print(f"  - Recent Events: {len(data['recent_events'])} entries")
    
    def test_email_test_endpoint(self, auth_headers):
        """POST /api/admin/email/test — Test email sending via Resend"""
        response = requests.post(
            f"{BASE_URL}/api/admin/email/test",
            headers=auth_headers,
            json={"to": "p.courbois@icloud.com"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check structure
        assert "sent" in data
        assert "to" in data
        assert "provider" in data
        
        print(f"✅ Email Test: sent={data['sent']}, to={data['to']}, provider={data['provider']}")
        if data.get("resend_id"):
            print(f"  - Resend ID: {data['resend_id']}")


class TestReconciliation:
    """P4: Reconciliation hardened, Webhook History"""
    
    def test_billing_reconcile_endpoint(self, auth_headers):
        """POST /api/admin/billing/reconcile — Reconciliation across all entities"""
        response = requests.post(f"{BASE_URL}/api/admin/billing/reconcile", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        # Check structure
        assert "reconciled" in data
        assert data["reconciled"] == True
        assert "fixed" in data
        assert "issues" in data
        assert "timestamp" in data
        
        print(f"✅ Billing Reconcile: reconciled={data['reconciled']}")
        print(f"  - Fixed: {len(data['fixed'])} items")
        print(f"  - Issues: {len(data['issues'])} items")
        if data["fixed"]:
            for fix in data["fixed"][:3]:
                print(f"    - {fix}")
        if data["issues"]:
            for issue in data["issues"][:3]:
                print(f"    - {issue}")
    
    def test_webhook_history_endpoint(self, auth_headers):
        """GET /api/admin/webhooks/history — Webhook audit log"""
        response = requests.get(f"{BASE_URL}/api/admin/webhooks/history", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        # Check structure
        assert "events" in data
        assert "count" in data
        assert isinstance(data["events"], list)
        
        print(f"✅ Webhook History: {data['count']} events")
        if data["events"]:
            for event in data["events"][:3]:
                print(f"  - {event.get('provider', 'unknown')}: {event.get('event_type', 'unknown')}")


class TestE2EFlowVerification:
    """P5: E2E Flow Verification with 6 Check Types"""
    
    def test_verify_e2e_flow_endpoint(self, auth_headers):
        """POST /api/admin/e2e/verify-flow — E2E flow verification"""
        response = requests.post(f"{BASE_URL}/api/admin/e2e/verify-flow", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        # Check structure - actual response has e2e_verification, checks, issues, passed, failed
        assert "checks" in data
        assert "issues" in data
        assert "e2e_verification" in data or "passed" in data
        
        print(f"✅ E2E Flow Verification:")
        print(f"  - Checks performed: {len(data['checks'])}")
        print(f"  - Issues found: {len(data['issues'])}")
        print(f"  - Passed: {data.get('passed', 'N/A')}, Failed: {data.get('failed', 'N/A')}")
        
        # Check types should include: quote_has_invoice, contract_has_quote, payment_status_sync, etc.
        check_types = set()
        for check in data["checks"]:
            if "check" in check:
                check_types.add(check["check"])
        
        print(f"  - Check types: {', '.join(check_types) if check_types else 'none'}")
        
        if data["issues"]:
            print(f"  - Issues:")
            for issue in data["issues"][:5]:
                print(f"    - {issue.get('check', 'unknown')}: {issue.get('issue', 'unknown')}")


class TestAdminAuthentication:
    """Admin authentication tests"""
    
    def test_admin_login(self):
        """Test admin login endpoint"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": "p.courbois@icloud.com", "password": "NxAi#Secure2026!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data.get("token_type") == "bearer"
        print(f"✅ Admin Login: token received")
    
    def test_admin_login_invalid(self):
        """Test admin login with invalid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": "invalid@test.com", "password": "wrongpassword"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 401
        print(f"✅ Admin Login Invalid: correctly rejected")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
