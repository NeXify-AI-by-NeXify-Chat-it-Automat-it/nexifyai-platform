"""
P4: Legal & Compliance Guardian Tests
=====================================
Tests for Legal Guardian service endpoints:
- Outreach Legal Gate (DSGVO, UWG, Suppression, Opt-Out, Fit-Score)
- Contract Legal Gate (Rechtsmodule, Kalkulation, Kundendaten)
- Communication Legal Gate (Opt-Out, KI-Transparenz, Impressum)
- Invoice Legal Gate (MwSt, Kunde, Rechnungsnummer)
- Risk Management (add, resolve, list)
- Audit Log
- Compliance Summary
- Opt-Out (Admin and Public)
- Contract send blocked when legal_svc detects high/critical risk
"""

import pytest
import requests
import os
import secrets
from datetime import datetime

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# Test data prefixes for cleanup
TEST_PREFIX = "TEST_LEGAL_P4_"


@pytest.fixture(scope="module")
def admin_token():
    """Get admin authentication token."""
    response = requests.post(
        f"{BASE_URL}/api/admin/login",
        data={"username": "p.courbois@icloud.com", "password": "NxAi#Secure2026!"}
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip(f"Admin login failed: {response.status_code} - {response.text}")


@pytest.fixture(scope="module")
def auth_headers(admin_token):
    """Auth headers for admin requests."""
    return {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}


class TestLegalGuardianAuth:
    """Test authentication requirements for Legal Guardian endpoints."""

    def test_legal_endpoints_require_auth(self):
        """All admin legal endpoints should require authentication."""
        endpoints = [
            ("POST", "/api/admin/legal/check-outreach"),
            ("POST", "/api/admin/legal/check-communication"),
            ("POST", "/api/admin/legal/risks"),
            ("GET", "/api/admin/legal/risks"),
            ("GET", "/api/admin/legal/audit"),
            ("GET", "/api/admin/legal/compliance"),
            ("POST", "/api/admin/legal/opt-out"),
        ]
        for method, endpoint in endpoints:
            if method == "POST":
                response = requests.post(f"{BASE_URL}{endpoint}", json={})
            else:
                response = requests.get(f"{BASE_URL}{endpoint}")
            assert response.status_code == 401, f"{endpoint} should require auth, got {response.status_code}"
            print(f"✅ {method} {endpoint} requires authentication (401)")


class TestOutreachLegalGate:
    """Test Outreach Legal Gate - DSGVO, UWG, Suppression, Opt-Out, Fit-Score."""

    def test_outreach_check_approved_with_consent(self, auth_headers):
        """Outreach with consent should be approved."""
        data = {
            "email": f"{TEST_PREFIX}approved@example.com",
            "channel": "email",
            "existing_customer": False,
            "consent_given": True,
            "score": 75,
            "ai_generated": True
        }
        response = requests.post(
            f"{BASE_URL}/api/admin/legal/check-outreach",
            headers=auth_headers,
            json=data
        )
        assert response.status_code == 200
        result = response.json()
        assert result["approved"] is True
        assert result["risk_level"] in ("none", "low")
        assert "audit_id" in result
        print(f"✅ Outreach with consent approved: risk_level={result['risk_level']}")

    def test_outreach_check_uwg_email_without_consent(self, auth_headers):
        """UWG: E-Mail without consent = high risk."""
        data = {
            "email": f"{TEST_PREFIX}uwg_email@example.com",
            "channel": "email",
            "existing_customer": False,
            "consent_given": False,
            "score": 80,
            "ai_generated": True
        }
        response = requests.post(
            f"{BASE_URL}/api/admin/legal/check-outreach",
            headers=auth_headers,
            json=data
        )
        assert response.status_code == 200
        result = response.json()
        assert result["approved"] is False
        assert result["risk_level"] == "high"
        assert "uwg_kaltansprache_email" in result["gate_reasons"]
        print(f"✅ UWG E-Mail Kaltansprache detected: risk_level={result['risk_level']}, gate_reasons={result['gate_reasons']}")

    def test_outreach_check_uwg_phone_b2b(self, auth_headers):
        """UWG: Phone B2B without relationship = medium risk."""
        data = {
            "email": f"{TEST_PREFIX}uwg_phone@example.com",
            "channel": "phone",
            "existing_customer": False,
            "consent_given": False,
            "score": 80,
            "ai_generated": True
        }
        response = requests.post(
            f"{BASE_URL}/api/admin/legal/check-outreach",
            headers=auth_headers,
            json=data
        )
        assert response.status_code == 200
        result = response.json()
        # Phone B2B without relationship = medium risk
        assert result["risk_level"] == "medium"
        assert "uwg_kaltansprache_phone_b2b" in result["gate_reasons"]
        print(f"✅ UWG Phone B2B detected: risk_level={result['risk_level']}")

    def test_outreach_check_existing_customer_ok(self, auth_headers):
        """Existing customer relationship = OK."""
        data = {
            "email": f"{TEST_PREFIX}existing@example.com",
            "channel": "email",
            "existing_customer": True,
            "consent_given": False,
            "score": 60,
            "ai_generated": True
        }
        response = requests.post(
            f"{BASE_URL}/api/admin/legal/check-outreach",
            headers=auth_headers,
            json=data
        )
        assert response.status_code == 200
        result = response.json()
        assert result["approved"] is True
        print(f"✅ Existing customer outreach approved: risk_level={result['risk_level']}")

    def test_outreach_check_low_fit_score(self, auth_headers):
        """Fit-Score below 30 = medium risk."""
        data = {
            "email": f"{TEST_PREFIX}lowscore@example.com",
            "channel": "email",
            "existing_customer": True,
            "consent_given": True,
            "score": 20,
            "ai_generated": True
        }
        response = requests.post(
            f"{BASE_URL}/api/admin/legal/check-outreach",
            headers=auth_headers,
            json=data
        )
        assert response.status_code == 200
        result = response.json()
        assert "low_fit_score" in result["gate_reasons"]
        print(f"✅ Low fit-score detected: risk_level={result['risk_level']}, gate_reasons={result['gate_reasons']}")


class TestSuppressionAndOptOut:
    """Test Suppression and Opt-Out blocking."""

    def test_admin_opt_out_registration(self, auth_headers):
        """Admin can register opt-out."""
        test_email = f"{TEST_PREFIX}optout_{secrets.token_hex(4)}@example.com"
        data = {"email": test_email, "reason": "test_admin_registration"}
        response = requests.post(
            f"{BASE_URL}/api/admin/legal/opt-out",
            headers=auth_headers,
            json=data
        )
        assert response.status_code == 200
        result = response.json()
        assert result.get("opted_out") is True or result.get("already_opted_out") is True
        print(f"✅ Admin opt-out registered: {test_email}")
        return test_email

    def test_public_opt_out_no_auth(self):
        """Public opt-out requires NO authentication."""
        test_email = f"{TEST_PREFIX}public_optout_{secrets.token_hex(4)}@example.com"
        data = {"email": test_email, "reason": "self_service_test"}
        response = requests.post(
            f"{BASE_URL}/api/public/opt-out",
            json=data
        )
        assert response.status_code == 200
        result = response.json()
        assert result.get("opted_out") is True
        print(f"✅ Public opt-out (no auth) registered: {test_email}")
        return test_email

    def test_outreach_blocked_for_opted_out_email(self, auth_headers):
        """Outreach should be blocked for opted-out emails."""
        # First register opt-out
        test_email = f"{TEST_PREFIX}blocked_{secrets.token_hex(4)}@example.com"
        requests.post(
            f"{BASE_URL}/api/public/opt-out",
            json={"email": test_email, "reason": "test_block"}
        )
        # Now check outreach
        data = {
            "email": test_email,
            "channel": "email",
            "existing_customer": True,
            "consent_given": True,
            "score": 90
        }
        response = requests.post(
            f"{BASE_URL}/api/admin/legal/check-outreach",
            headers=auth_headers,
            json=data
        )
        assert response.status_code == 200
        result = response.json()
        assert result["approved"] is False
        assert result["risk_level"] == "critical"
        assert "opt_out" in result["gate_reasons"]
        print(f"✅ Outreach blocked for opted-out email: {test_email}")

    def test_duplicate_opt_out_returns_already_opted_out(self, auth_headers):
        """Duplicate opt-out should return already_opted_out."""
        test_email = f"{TEST_PREFIX}dup_optout_{secrets.token_hex(4)}@example.com"
        # First opt-out
        requests.post(f"{BASE_URL}/api/public/opt-out", json={"email": test_email})
        # Second opt-out
        response = requests.post(
            f"{BASE_URL}/api/public/opt-out",
            json={"email": test_email}
        )
        assert response.status_code == 200
        result = response.json()
        assert result.get("already_opted_out") is True
        print(f"✅ Duplicate opt-out returns already_opted_out")


class TestCommunicationLegalGate:
    """Test Communication Legal Gate."""

    def test_communication_check_approved(self, auth_headers):
        """Communication without opt-out should be approved."""
        data = {
            "channel": "email",
            "recipient": f"{TEST_PREFIX}comm_ok@example.com",
            "content": "Test message with nexify footer and impressum",
            "ai_generated": False
        }
        response = requests.post(
            f"{BASE_URL}/api/admin/legal/check-communication",
            headers=auth_headers,
            json=data
        )
        assert response.status_code == 200
        result = response.json()
        assert result["approved"] is True
        print(f"✅ Communication check approved: risk_level={result['risk_level']}")

    def test_communication_blocked_for_opted_out(self, auth_headers):
        """Communication to opted-out recipient should be blocked."""
        test_email = f"{TEST_PREFIX}comm_blocked_{secrets.token_hex(4)}@example.com"
        # Register opt-out
        requests.post(f"{BASE_URL}/api/public/opt-out", json={"email": test_email})
        # Check communication
        data = {
            "channel": "email",
            "recipient": test_email,
            "content": "Test message",
            "ai_generated": False
        }
        response = requests.post(
            f"{BASE_URL}/api/admin/legal/check-communication",
            headers=auth_headers,
            json=data
        )
        assert response.status_code == 200
        result = response.json()
        assert result["approved"] is False
        assert result["risk_level"] == "critical"
        print(f"✅ Communication blocked for opted-out recipient")

    def test_communication_ai_without_disclosure(self, auth_headers):
        """AI-generated content without disclosure = low risk."""
        data = {
            "channel": "email",
            "recipient": f"{TEST_PREFIX}ai_nodisclosure@example.com",
            "content": "This is a regular message without any AI disclosure",
            "ai_generated": True
        }
        response = requests.post(
            f"{BASE_URL}/api/admin/legal/check-communication",
            headers=auth_headers,
            json=data
        )
        assert response.status_code == 200
        result = response.json()
        # Should have ki_transparenz check failed
        checks = {c["check"]: c["passed"] for c in result.get("checks", [])}
        assert checks.get("ki_transparenz") is False
        print(f"✅ AI content without disclosure detected: risk_level={result['risk_level']}")


class TestBillingLegalGate:
    """Test Invoice/Billing Legal Gate."""

    def test_billing_check_requires_invoice(self, auth_headers):
        """Billing check for non-existent invoice returns 404."""
        response = requests.post(
            f"{BASE_URL}/api/admin/legal/check-billing/nonexistent_invoice_id",
            headers=auth_headers
        )
        assert response.status_code == 404
        print(f"✅ Billing check returns 404 for non-existent invoice")


class TestContractLegalGate:
    """Test Contract Legal Gate."""

    def test_contract_check_requires_contract(self, auth_headers):
        """Contract check for non-existent contract returns 404."""
        response = requests.post(
            f"{BASE_URL}/api/admin/legal/check-contract/nonexistent_contract_id",
            headers=auth_headers
        )
        assert response.status_code == 404
        print(f"✅ Contract check returns 404 for non-existent contract")


class TestRiskManagement:
    """Test Risk Management (add, resolve, list)."""

    def test_add_risk(self, auth_headers):
        """Add a legal risk to an entity."""
        data = {
            "entity_type": "contract",
            "entity_id": f"{TEST_PREFIX}contract_{secrets.token_hex(4)}",
            "risk": {
                "level": "medium",
                "description": "Test risk for P4 testing",
                "mitigation": "Review and approve"
            }
        }
        response = requests.post(
            f"{BASE_URL}/api/admin/legal/risks",
            headers=auth_headers,
            json=data
        )
        assert response.status_code == 200
        result = response.json()
        assert "risk_id" in result
        assert result["level"] == "medium"
        assert result["resolved"] is False
        print(f"✅ Risk added: {result['risk_id']}")
        return result["risk_id"]

    def test_add_risk_requires_entity_type_and_id(self, auth_headers):
        """Add risk requires entity_type and entity_id."""
        data = {"risk": {"level": "low", "description": "Test"}}
        response = requests.post(
            f"{BASE_URL}/api/admin/legal/risks",
            headers=auth_headers,
            json=data
        )
        assert response.status_code == 400
        print(f"✅ Add risk validates required fields")

    def test_list_risks(self, auth_headers):
        """List all risks."""
        response = requests.get(
            f"{BASE_URL}/api/admin/legal/risks",
            headers=auth_headers
        )
        assert response.status_code == 200
        result = response.json()
        assert "risks" in result
        assert isinstance(result["risks"], list)
        print(f"✅ List risks: {len(result['risks'])} risks found")

    def test_list_risks_filter_by_resolved(self, auth_headers):
        """List risks filtered by resolved status."""
        response = requests.get(
            f"{BASE_URL}/api/admin/legal/risks?resolved=false",
            headers=auth_headers
        )
        assert response.status_code == 200
        result = response.json()
        # All returned risks should be unresolved
        for risk in result["risks"]:
            assert risk["resolved"] is False
        print(f"✅ List unresolved risks: {len(result['risks'])} found")

    def test_resolve_risk(self, auth_headers):
        """Resolve a risk."""
        # First add a risk
        data = {
            "entity_type": "outreach",
            "entity_id": f"{TEST_PREFIX}outreach_{secrets.token_hex(4)}",
            "risk": {"level": "low", "description": "Test risk to resolve"}
        }
        add_response = requests.post(
            f"{BASE_URL}/api/admin/legal/risks",
            headers=auth_headers,
            json=data
        )
        risk_id = add_response.json()["risk_id"]
        
        # Resolve it
        resolve_response = requests.patch(
            f"{BASE_URL}/api/admin/legal/risks/{risk_id}/resolve",
            headers=auth_headers,
            json={"resolution": "Reviewed and approved for P4 testing"}
        )
        assert resolve_response.status_code == 200
        result = resolve_response.json()
        assert result["resolved"] is True
        print(f"✅ Risk resolved: {risk_id}")


class TestAuditLog:
    """Test Legal Audit Log."""

    def test_get_audit_log(self, auth_headers):
        """Get legal audit log."""
        response = requests.get(
            f"{BASE_URL}/api/admin/legal/audit",
            headers=auth_headers
        )
        assert response.status_code == 200
        result = response.json()
        assert "audit_log" in result
        assert isinstance(result["audit_log"], list)
        print(f"✅ Audit log: {len(result['audit_log'])} entries")

    def test_audit_log_with_limit(self, auth_headers):
        """Audit log respects limit parameter."""
        response = requests.get(
            f"{BASE_URL}/api/admin/legal/audit?limit=5",
            headers=auth_headers
        )
        assert response.status_code == 200
        result = response.json()
        assert len(result["audit_log"]) <= 5
        print(f"✅ Audit log with limit=5: {len(result['audit_log'])} entries")

    def test_audit_log_filter_by_type(self, auth_headers):
        """Audit log can filter by entity type."""
        response = requests.get(
            f"{BASE_URL}/api/admin/legal/audit?entity_type=outreach",
            headers=auth_headers
        )
        assert response.status_code == 200
        result = response.json()
        # All entries should contain 'outreach' in type
        for entry in result["audit_log"]:
            assert "outreach" in entry.get("type", "")
        print(f"✅ Audit log filtered by outreach: {len(result['audit_log'])} entries")


class TestComplianceSummary:
    """Test Compliance Summary."""

    def test_compliance_summary(self, auth_headers):
        """Get compliance summary."""
        response = requests.get(
            f"{BASE_URL}/api/admin/legal/compliance",
            headers=auth_headers
        )
        assert response.status_code == 200
        result = response.json()
        # Verify structure
        assert "risks" in result
        assert "open" in result["risks"]
        assert "total" in result["risks"]
        assert "resolved" in result["risks"]
        assert "audits" in result
        assert "opt_outs" in result
        assert "suppressions" in result
        assert "recent_gates" in result
        assert "compliance_checks" in result
        print(f"✅ Compliance summary: {result['risks']['open']} open risks, {result['opt_outs']} opt-outs")


class TestContractSendLegalGate:
    """Test Contract send blocked when legal_svc detects high/critical risk."""

    def test_contract_send_endpoint_exists(self, auth_headers):
        """Verify contract send endpoint exists."""
        # Try to send a non-existent contract
        response = requests.post(
            f"{BASE_URL}/api/admin/contracts/nonexistent_id/send",
            headers=auth_headers
        )
        # Should return 404 for non-existent contract, not 405 (method not allowed)
        assert response.status_code == 404
        print(f"✅ Contract send endpoint exists (returns 404 for non-existent)")


class TestIntegrationScenarios:
    """Integration scenarios combining multiple legal checks."""

    def test_full_outreach_flow_with_audit(self, auth_headers):
        """Full outreach flow: check → audit log entry created."""
        test_email = f"{TEST_PREFIX}flow_{secrets.token_hex(4)}@example.com"
        
        # Perform outreach check
        check_response = requests.post(
            f"{BASE_URL}/api/admin/legal/check-outreach",
            headers=auth_headers,
            json={
                "email": test_email,
                "channel": "email",
                "existing_customer": False,
                "consent_given": True,
                "score": 85
            }
        )
        assert check_response.status_code == 200
        audit_id = check_response.json()["audit_id"]
        
        # Verify audit log entry
        audit_response = requests.get(
            f"{BASE_URL}/api/admin/legal/audit?entity_type=outreach&limit=10",
            headers=auth_headers
        )
        audit_entries = audit_response.json()["audit_log"]
        found = any(e.get("audit_id") == audit_id for e in audit_entries)
        assert found, f"Audit entry {audit_id} not found in audit log"
        print(f"✅ Full outreach flow: check created audit entry {audit_id}")

    def test_opt_out_adds_to_suppression(self, auth_headers):
        """Opt-out should also add to suppression list."""
        test_email = f"{TEST_PREFIX}supp_{secrets.token_hex(4)}@example.com"
        
        # Register opt-out
        requests.post(f"{BASE_URL}/api/public/opt-out", json={"email": test_email})
        
        # Check outreach - should be blocked by suppression
        check_response = requests.post(
            f"{BASE_URL}/api/admin/legal/check-outreach",
            headers=auth_headers,
            json={
                "email": test_email,
                "channel": "email",
                "existing_customer": True,
                "consent_given": True,
                "score": 90
            }
        )
        result = check_response.json()
        # Should be blocked by either opt_out or suppression
        assert result["approved"] is False
        assert result["risk_level"] == "critical"
        print(f"✅ Opt-out adds to suppression: email blocked with critical risk")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
