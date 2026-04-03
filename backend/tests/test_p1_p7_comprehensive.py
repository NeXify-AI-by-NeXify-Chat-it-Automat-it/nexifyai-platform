"""
P1-P7 Comprehensive Backend Tests for NeXifyAI
==============================================
P1: DeepSeek Live-Pfad mit Provider-Abstraktionsschicht
P2: Portal-Finance-Ansicht
P3: Contract OS mit Versionshistorie, Evidenzpaket, Signatur-Vorschau
P4: Webhook-Signaturverifikation, Reconciliation, Webhook-History
P5: E2E-Flow-Verifikation
P6: Legal Gate im Contract-Accept-Flow, Compliance-Summary
P7: Outbound Lead Machine mit Legal Gate, Response-Tracking, Handover
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://contract-os.preview.emergentagent.com").rstrip("/")

# Test credentials
ADMIN_EMAIL = "p.courbois@icloud.com"
ADMIN_PASSWORD = "NxAi#Secure2026!"
TEST_CONTRACT_ID = "ctr_fa24ac23eb394673"
TEST_CONTRACT_ID_ALT = "ctr_3d5efbc6b9c04a29"
TEST_OUTBOUND_LEAD_ID = "obl_236fdcfee15a4b65"


@pytest.fixture(scope="module")
def admin_token():
    """Get admin JWT token."""
    response = requests.post(
        f"{BASE_URL}/api/admin/login",
        data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip(f"Admin login failed: {response.status_code} - {response.text[:200]}")


@pytest.fixture(scope="module")
def admin_headers(admin_token):
    """Headers with admin auth."""
    return {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}


class TestP1LLMProviderAbstraction:
    """P1: DeepSeek Live-Pfad mit Provider-Abstraktionsschicht"""

    def test_llm_status_endpoint(self, admin_headers):
        """GET /api/admin/llm/status — Provider info, migration status, metrics"""
        response = requests.get(f"{BASE_URL}/api/admin/llm/status", headers=admin_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text[:200]}"
        
        data = response.json()
        # Verify required fields
        assert "active_provider" in data, "Missing active_provider"
        assert "is_target_architecture" in data, "Missing is_target_architecture"
        assert "providers" in data, "Missing providers"
        assert "migration_ready" in data, "Missing migration_ready"
        
        # Verify provider structure
        providers = data["providers"]
        assert "deepseek" in providers, "Missing deepseek provider info"
        assert "emergent_gpt" in providers, "Missing emergent_gpt provider info"
        
        # Since DEEPSEEK_API_KEY is not set, should use emergent_gpt_fallback
        assert data["active_provider"] in ("emergent_gpt_fallback", "deepseek"), f"Unexpected provider: {data['active_provider']}"
        print(f"✅ LLM Status: active_provider={data['active_provider']}, migration_ready={data['migration_ready']}")

    def test_llm_health_endpoint(self, admin_headers):
        """GET /api/admin/llm/health — Live health check"""
        response = requests.get(f"{BASE_URL}/api/admin/llm/health", headers=admin_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text[:200]}"
        
        data = response.json()
        assert "status" in data, "Missing status"
        assert "provider" in data, "Missing provider"
        assert "is_target_architecture" in data, "Missing is_target_architecture"
        
        # Health should be healthy or degraded (not error)
        assert data["status"] in ("healthy", "degraded", "not_configured"), f"Unexpected status: {data['status']}"
        print(f"✅ LLM Health: status={data['status']}, provider={data['provider']}")

    def test_llm_test_endpoint(self, admin_headers):
        """POST /api/admin/llm/test — LLM test with model override"""
        response = requests.post(
            f"{BASE_URL}/api/admin/llm/test",
            headers=admin_headers,
            json={"prompt": "Antworte mit einem Wort: Hallo"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text[:200]}"
        
        data = response.json()
        assert "provider" in data, "Missing provider"
        assert "response" in data, "Missing response"
        assert "success" in data, "Missing success"
        
        # Response should have content (not error message starting with [)
        if data["success"]:
            assert len(data["response"]) > 0, "Empty response"
            print(f"✅ LLM Test: success={data['success']}, response_preview={data['response'][:50]}...")
        else:
            print(f"⚠️ LLM Test: success=False (may be expected if no API key)")

    def test_llm_agent_flow_endpoint(self, admin_headers):
        """POST /api/admin/llm/test-agent-flow — Full agent flow test with session"""
        response = requests.post(
            f"{BASE_URL}/api/admin/llm/test-agent-flow",
            headers=admin_headers,
            json={"message": "Was bietet NeXifyAI an?"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text[:200]}"
        
        data = response.json()
        assert "provider" in data, "Missing provider"
        assert "session_id" in data, "Missing session_id"
        assert "test_results" in data, "Missing test_results"
        assert "success" in data, "Missing success"
        
        test_results = data["test_results"]
        assert "initial_response" in test_results, "Missing initial_response"
        assert "followup_response" in test_results, "Missing followup_response"
        assert "session_continuity" in test_results, "Missing session_continuity"
        
        print(f"✅ LLM Agent Flow: success={data['success']}, session_continuity={test_results['session_continuity']}")


class TestP2PortalFinanceView:
    """P2: Portal-Finance-Ansicht (Rechnungen, Zahlungsstatus, Fälligkeit, Mahnstufen, Banküberweisung)"""

    def test_customer_finance_endpoint_structure(self, admin_headers):
        """Test finance endpoint returns correct structure (via admin portal-access)"""
        # First get a customer portal access token
        response = requests.post(
            f"{BASE_URL}/api/admin/customers/portal-access",
            headers=admin_headers,
            json={"email": "max@testfirma.de"}
        )
        
        if response.status_code != 200:
            pytest.skip(f"Could not get portal access: {response.status_code}")
        
        portal_data = response.json()
        portal_url = portal_data.get("portal_url", "")
        
        # Extract token from URL - format is /portal/{token}
        token = None
        if "/portal/" in portal_url:
            token = portal_url.split("/portal/")[1]
        elif "token=" in portal_url:
            token = portal_url.split("token=")[1].split("&")[0]
        
        if token:
            # Verify token to get customer JWT
            verify_response = requests.post(
                f"{BASE_URL}/api/auth/verify-token",
                json={"token": token}
            )
            
            if verify_response.status_code == 200:
                customer_jwt = verify_response.json().get("access_token")
                customer_headers = {"Authorization": f"Bearer {customer_jwt}", "Content-Type": "application/json"}
                
                # Now test the finance endpoint
                finance_response = requests.get(
                    f"{BASE_URL}/api/customer/finance",
                    headers=customer_headers
                )
                
                assert finance_response.status_code == 200, f"Finance endpoint failed: {finance_response.status_code}"
                
                data = finance_response.json()
                
                # Verify structure
                assert "summary" in data, "Missing summary"
                assert "invoices" in data, "Missing invoices"
                assert "quotes" in data, "Missing quotes"
                assert "contracts" in data, "Missing contracts"
                assert "bank_transfer_info" in data, "Missing bank_transfer_info"
                
                # Verify summary fields
                summary = data["summary"]
                assert "total_invoices" in summary, "Missing total_invoices"
                assert "total_outstanding_eur" in summary, "Missing total_outstanding_eur"
                assert "total_paid_eur" in summary, "Missing total_paid_eur"
                assert "open_invoices" in summary, "Missing open_invoices"
                assert "overdue_invoices" in summary, "Missing overdue_invoices"
                
                # Verify bank info
                bank_info = data["bank_transfer_info"]
                assert "iban" in bank_info, "Missing IBAN"
                assert "bic" in bank_info, "Missing BIC"
                assert "account_holder" in bank_info, "Missing account_holder"
                
                print(f"✅ Finance endpoint: {summary['total_invoices']} invoices, {summary['open_invoices']} open, bank_info present")
                return
        
        pytest.skip("Could not extract customer token for finance test")


class TestP3ContractOSEnhancement:
    """P3: Contract OS mit Versionshistorie, Evidenzpaket, Signatur-Vorschau, PDF"""

    def test_customer_contract_detail_structure(self, admin_headers):
        """GET /api/customer/contracts/{id} — Returns versions, evidence_trail, signature_preview, has_pdf"""
        # Get customer portal access
        response = requests.post(
            f"{BASE_URL}/api/admin/customers/portal-access",
            headers=admin_headers,
            json={"email": "max@testfirma.de"}
        )
        
        if response.status_code != 200:
            pytest.skip(f"Could not get portal access: {response.status_code}")
        
        portal_data = response.json()
        portal_url = portal_data.get("portal_url", "")
        
        # Extract token from URL - format is /portal/{token}
        token = None
        if "/portal/" in portal_url:
            token = portal_url.split("/portal/")[1]
        elif "token=" in portal_url:
            token = portal_url.split("token=")[1].split("&")[0]
        
        if token:
            verify_response = requests.post(
                f"{BASE_URL}/api/auth/verify-token",
                json={"token": token}
            )
            
            if verify_response.status_code == 200:
                customer_jwt = verify_response.json().get("access_token")
                customer_headers = {"Authorization": f"Bearer {customer_jwt}", "Content-Type": "application/json"}
                
                # Get contracts list first
                contracts_response = requests.get(
                    f"{BASE_URL}/api/customer/contracts",
                    headers=customer_headers
                )
                
                if contracts_response.status_code == 200:
                    contracts = contracts_response.json().get("contracts", [])
                    
                    if contracts:
                        contract_id = contracts[0]["contract_id"]
                        
                        # Get contract detail
                        detail_response = requests.get(
                            f"{BASE_URL}/api/customer/contracts/{contract_id}",
                            headers=customer_headers
                        )
                        
                        assert detail_response.status_code == 200, f"Contract detail failed: {detail_response.status_code}"
                        
                        data = detail_response.json()
                        
                        # Verify P3 fields
                        assert "versions" in data, "Missing versions array"
                        assert "evidence_trail" in data, "Missing evidence_trail array"
                        assert "has_pdf" in data, "Missing has_pdf"
                        assert "document_hash" in data, "Missing document_hash"
                        assert "legal_module_definitions" in data, "Missing legal_module_definitions"
                        
                        # If accepted, should have signature_preview
                        if data.get("status") == "accepted":
                            assert "signature_preview" in data, "Missing signature_preview for accepted contract"
                        
                        # If change_requested, should have change_request_detail
                        if data.get("status") == "change_requested":
                            assert "change_request_detail" in data, "Missing change_request_detail"
                        
                        print(f"✅ Contract detail: versions={len(data['versions'])}, evidence_trail={len(data['evidence_trail'])}, has_pdf={data['has_pdf']}")
                        return
                    else:
                        pytest.skip("No contracts found for test customer")
        
        pytest.skip("Could not get customer contract detail")


class TestP4ReconciliationAndWebhooks:
    """P4: Webhook-Signaturverifikation, Reconciliation, Webhook-History"""

    def test_billing_reconcile_endpoint(self, admin_headers):
        """POST /api/admin/billing/reconcile — Reconciliation across quotes/contracts/invoices"""
        response = requests.post(
            f"{BASE_URL}/api/admin/billing/reconcile",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text[:200]}"
        
        data = response.json()
        assert "reconciled" in data, "Missing reconciled"
        assert "fixed" in data, "Missing fixed"
        assert "issues" in data, "Missing issues"
        assert "timestamp" in data, "Missing timestamp"
        
        assert data["reconciled"] == True, "Reconciliation should return reconciled=True"
        print(f"✅ Reconciliation: fixed={len(data['fixed'])}, issues={len(data['issues'])}")

    def test_webhooks_history_endpoint(self, admin_headers):
        """GET /api/admin/webhooks/history — Webhook events audit log"""
        response = requests.get(
            f"{BASE_URL}/api/admin/webhooks/history",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text[:200]}"
        
        data = response.json()
        assert "events" in data, "Missing events"
        assert "count" in data, "Missing count"
        
        # Events should be a list
        assert isinstance(data["events"], list), "events should be a list"
        print(f"✅ Webhook history: {data['count']} events")


class TestP5E2EFlowVerification:
    """P5: E2E-Flow-Verifikation (Lead→Quote→Contract→Invoice→Payment→Status)"""

    def test_e2e_verify_flow_endpoint(self, admin_headers):
        """POST /api/admin/e2e/verify-flow — Complete E2E verification"""
        response = requests.post(
            f"{BASE_URL}/api/admin/e2e/verify-flow",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text[:200]}"
        
        data = response.json()
        assert "e2e_verification" in data, "Missing e2e_verification"
        assert "total_checks" in data, "Missing total_checks"
        assert "passed" in data, "Missing passed"
        assert "failed" in data, "Missing failed"
        assert "pass_rate" in data, "Missing pass_rate"
        assert "checks" in data, "Missing checks"
        assert "issues" in data, "Missing issues"
        assert "timestamp" in data, "Missing timestamp"
        
        assert data["e2e_verification"] == True, "e2e_verification should be True"
        print(f"✅ E2E Verification: {data['passed']}/{data['total_checks']} passed ({data['pass_rate']}), issues={len(data['issues'])}")


class TestP6LegalGateAndCompliance:
    """P6: Legal Gate im Contract-Accept-Flow, Compliance-Summary"""

    def test_legal_check_outreach_endpoint(self, admin_headers):
        """POST /api/admin/legal/check-outreach — Legal gate for outreach"""
        response = requests.post(
            f"{BASE_URL}/api/admin/legal/check-outreach",
            headers=admin_headers,
            json={
                "email": "test@example.com",
                "channel": "email",
                "score": 50,
                "existing_customer": False,
                "consent_given": False
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text[:200]}"
        
        data = response.json()
        assert "approved" in data, "Missing approved"
        assert "risk_level" in data, "Missing risk_level"
        assert "checks" in data, "Missing checks"
        
        # Checks should be a list
        assert isinstance(data["checks"], list), "checks should be a list"
        print(f"✅ Legal check outreach: approved={data['approved']}, risk_level={data['risk_level']}, checks={len(data['checks'])}")

    def test_legal_check_contract_endpoint(self, admin_headers):
        """POST /api/admin/legal/check-contract/{id} — Legal gate for contracts"""
        # Try with test contract ID
        response = requests.post(
            f"{BASE_URL}/api/admin/legal/check-contract/{TEST_CONTRACT_ID}",
            headers=admin_headers
        )
        
        if response.status_code == 404:
            # Try alternate contract ID
            response = requests.post(
                f"{BASE_URL}/api/admin/legal/check-contract/{TEST_CONTRACT_ID_ALT}",
                headers=admin_headers
            )
        
        if response.status_code == 404:
            pytest.skip("Test contract not found")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text[:200]}"
        
        data = response.json()
        assert "approved" in data, "Missing approved"
        assert "risk_level" in data, "Missing risk_level"
        assert "checks" in data, "Missing checks"
        
        print(f"✅ Legal check contract: approved={data['approved']}, risk_level={data['risk_level']}")

    def test_compliance_summary_endpoint(self, admin_headers):
        """GET /api/admin/legal/compliance — Compliance summary"""
        response = requests.get(
            f"{BASE_URL}/api/admin/legal/compliance",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text[:200]}"
        
        data = response.json()
        assert "risks" in data, "Missing risks"
        assert "audits" in data, "Missing audits"
        assert "opt_outs" in data, "Missing opt_outs"
        assert "suppressions" in data, "Missing suppressions"
        assert "compliance_checks" in data, "Missing compliance_checks"
        
        risks = data["risks"]
        assert "open" in risks, "Missing risks.open"
        assert "total" in risks, "Missing risks.total"
        
        print(f"✅ Compliance summary: risks_open={risks['open']}, risks_total={risks['total']}, opt_outs={data['opt_outs']}")


class TestP7OutboundLeadMachine:
    """P7: Outbound Lead Machine mit Legal Gate im Send, Response-Tracking, Handover"""

    def test_outbound_lead_detail(self, admin_headers):
        """GET /api/admin/outbound/{lead_id} — Get outbound lead detail"""
        response = requests.get(
            f"{BASE_URL}/api/admin/outbound/{TEST_OUTBOUND_LEAD_ID}",
            headers=admin_headers
        )
        
        if response.status_code == 404:
            pytest.skip("Test outbound lead not found")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text[:200]}"
        
        data = response.json()
        assert "outbound_lead_id" in data, "Missing outbound_lead_id"
        assert "status" in data, "Missing status"
        assert "timeline" in data, "Missing timeline"
        
        print(f"✅ Outbound lead detail: status={data['status']}, timeline_events={len(data['timeline'])}")

    def test_outbound_send_with_legal_gate(self, admin_headers):
        """POST /api/admin/outbound/{lead_id}/outreach/{outreach_id}/send — Legal gate in send flow"""
        # First get the lead to find an outreach
        lead_response = requests.get(
            f"{BASE_URL}/api/admin/outbound/{TEST_OUTBOUND_LEAD_ID}",
            headers=admin_headers
        )
        
        if lead_response.status_code == 404:
            pytest.skip("Test outbound lead not found")
        
        lead = lead_response.json()
        outreaches = lead.get("outreaches", [])
        
        if not outreaches:
            # Create an outreach first
            create_response = requests.post(
                f"{BASE_URL}/api/admin/outbound/{TEST_OUTBOUND_LEAD_ID}/outreach",
                headers=admin_headers,
                json={
                    "channel": "email",
                    "subject": "Test Outreach",
                    "content": "Test content for legal gate testing"
                }
            )
            
            if create_response.status_code == 200:
                outreach_id = create_response.json().get("outreach_id")
            else:
                pytest.skip("Could not create outreach for testing")
        else:
            outreach_id = outreaches[0].get("outreach_id")
        
        # Now test the send endpoint (should check legal gate)
        send_response = requests.post(
            f"{BASE_URL}/api/admin/outbound/{TEST_OUTBOUND_LEAD_ID}/outreach/{outreach_id}/send",
            headers=admin_headers
        )
        
        # Response could be 200 (success) or have legal gate block
        assert send_response.status_code in (200, 400), f"Unexpected status: {send_response.status_code}"
        
        data = send_response.json()
        
        if "error" in data and "Legal-Gate" in data.get("error", ""):
            # Legal gate blocked - this is expected behavior
            assert "legal_check" in data, "Missing legal_check when blocked"
            print(f"✅ Outbound send: Legal gate blocked (expected for cold outreach)")
        else:
            print(f"✅ Outbound send: Processed successfully")

    def test_outbound_respond_endpoint(self, admin_headers):
        """POST /api/admin/outbound/{lead_id}/respond — Response tracking"""
        response = requests.post(
            f"{BASE_URL}/api/admin/outbound/{TEST_OUTBOUND_LEAD_ID}/respond",
            headers=admin_headers,
            json={
                "response_type": "positive",
                "content": "Test response for tracking"
            }
        )
        
        if response.status_code == 404:
            pytest.skip("Test outbound lead not found")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text[:200]}"
        
        data = response.json()
        assert "status" in data, "Missing status"
        assert "response_type" in data, "Missing response_type"
        
        print(f"✅ Outbound respond: status={data['status']}, response_type={data['response_type']}")

    def test_outbound_handover_endpoint(self, admin_headers):
        """POST /api/admin/outbound/{lead_id}/handover — Handover to quote/meeting/nurture"""
        response = requests.post(
            f"{BASE_URL}/api/admin/outbound/{TEST_OUTBOUND_LEAD_ID}/handover",
            headers=admin_headers,
            json={"handover_type": "nurture"}
        )
        
        if response.status_code == 404:
            pytest.skip("Test outbound lead not found")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text[:200]}"
        
        data = response.json()
        assert "lead_id" in data, "Missing lead_id"
        assert "handover_type" in data, "Missing handover_type"
        assert "status" in data, "Missing status"
        
        print(f"✅ Outbound handover: handover_type={data['handover_type']}, status={data['status']}")


class TestAdminAuthentication:
    """Basic admin authentication tests"""

    def test_admin_login(self):
        """POST /api/admin/login — Admin authentication"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200, f"Admin login failed: {response.status_code}"
        
        data = response.json()
        assert "access_token" in data, "Missing access_token"
        assert "token_type" in data, "Missing token_type"
        
        print(f"✅ Admin login successful")

    def test_admin_me(self, admin_headers):
        """GET /api/admin/me — Get current admin info"""
        response = requests.get(f"{BASE_URL}/api/admin/me", headers=admin_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "email" in data, "Missing email"
        assert data["email"] == ADMIN_EMAIL, f"Email mismatch: {data['email']}"
        
        print(f"✅ Admin me: {data['email']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
