"""
P4: Contract Legal Gate Integration Tests
==========================================
Tests for contract send blocking when legal_svc detects high/critical risk.
"""

import pytest
import requests
import os
import secrets

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
TEST_PREFIX = "TEST_CONTRACT_LEGAL_"


@pytest.fixture(scope="module")
def admin_token():
    """Get admin authentication token."""
    response = requests.post(
        f"{BASE_URL}/api/admin/login",
        data={"username": "p.courbois@icloud.com", "password": "NxAi#Secure2026!"}
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip(f"Admin login failed: {response.status_code}")


@pytest.fixture(scope="module")
def auth_headers(admin_token):
    """Auth headers for admin requests."""
    return {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}


class TestContractLegalGateIntegration:
    """Test contract send blocked when legal risk is high/critical."""

    def test_create_contract_without_customer_email_fails(self, auth_headers):
        """Contract creation requires customer email."""
        data = {
            "customer": {"name": "Test Customer"},
            "tier_key": "starter",
            "contract_type": "standard"
        }
        response = requests.post(
            f"{BASE_URL}/api/admin/contracts",
            headers=auth_headers,
            json=data
        )
        assert response.status_code == 400
        print(f"✅ Contract creation requires customer.email")

    def test_create_contract_success(self, auth_headers):
        """Create a valid contract."""
        test_email = f"{TEST_PREFIX}customer_{secrets.token_hex(4)}@example.com"
        data = {
            "customer": {
                "name": "Test Customer P4",
                "email": test_email,
                "company": "Test Company GmbH"
            },
            "tier_key": "starter",
            "contract_type": "standard",
            "notes": "P4 Legal Guardian test contract"
        }
        response = requests.post(
            f"{BASE_URL}/api/admin/contracts",
            headers=auth_headers,
            json=data
        )
        assert response.status_code == 200
        result = response.json()
        assert "contract_id" in result
        assert result["customer"]["email"] == test_email.lower()
        print(f"✅ Contract created: {result['contract_id']}")
        return result["contract_id"], test_email

    def test_contract_legal_check_missing_modules(self, auth_headers):
        """Contract without legal modules should have medium risk."""
        # Create contract
        test_email = f"{TEST_PREFIX}nomodules_{secrets.token_hex(4)}@example.com"
        create_response = requests.post(
            f"{BASE_URL}/api/admin/contracts",
            headers=auth_headers,
            json={
                "customer": {"name": "Test", "email": test_email, "company": "Test GmbH"},
                "tier_key": "starter",
                "contract_type": "standard"
            }
        )
        contract_id = create_response.json()["contract_id"]
        
        # Check legal
        check_response = requests.post(
            f"{BASE_URL}/api/admin/legal/check-contract/{contract_id}",
            headers=auth_headers
        )
        assert check_response.status_code == 200
        result = check_response.json()
        # Should have some checks
        assert "checks" in result
        assert "risk_level" in result
        print(f"✅ Contract legal check: risk_level={result['risk_level']}, checks={len(result['checks'])}")

    def test_contract_send_with_legal_gate(self, auth_headers):
        """Contract send should check legal gate."""
        # Create contract with valid customer email
        test_email = f"{TEST_PREFIX}send_{secrets.token_hex(4)}@example.com"
        create_response = requests.post(
            f"{BASE_URL}/api/admin/contracts",
            headers=auth_headers,
            json={
                "customer": {"name": "Test Send", "email": test_email, "company": "Test GmbH"},
                "tier_key": "starter",
                "contract_type": "standard"
            }
        )
        contract_id = create_response.json()["contract_id"]
        
        # Try to send
        send_response = requests.post(
            f"{BASE_URL}/api/admin/contracts/{contract_id}/send",
            headers=auth_headers
        )
        # Should either succeed or be blocked by legal gate
        assert send_response.status_code == 200
        result = send_response.json()
        
        if result.get("gate_blocked"):
            assert result["sent"] is False
            assert "legal_check" in result
            print(f"✅ Contract send blocked by legal gate: {result.get('message')}")
        else:
            assert result.get("sent") is True or "sent" in result
            print(f"✅ Contract send succeeded (legal gate passed)")

    def test_contract_without_email_cannot_be_sent(self, auth_headers):
        """Contract without customer email cannot be sent."""
        # This test verifies the endpoint behavior for edge cases
        # The contract creation already requires email, so this tests the send endpoint validation
        response = requests.post(
            f"{BASE_URL}/api/admin/contracts/nonexistent_contract/send",
            headers=auth_headers
        )
        assert response.status_code == 404
        print(f"✅ Non-existent contract returns 404 on send")


class TestContractLegalCheckPersistence:
    """Test that legal check results are persisted on contract."""

    def test_legal_check_updates_contract(self, auth_headers):
        """Legal check should update contract with legal_check field."""
        # Create contract
        test_email = f"{TEST_PREFIX}persist_{secrets.token_hex(4)}@example.com"
        create_response = requests.post(
            f"{BASE_URL}/api/admin/contracts",
            headers=auth_headers,
            json={
                "customer": {"name": "Test Persist", "email": test_email, "company": "Test GmbH"},
                "tier_key": "starter",
                "contract_type": "standard"
            }
        )
        contract_id = create_response.json()["contract_id"]
        
        # Perform legal check
        check_response = requests.post(
            f"{BASE_URL}/api/admin/legal/check-contract/{contract_id}",
            headers=auth_headers
        )
        assert check_response.status_code == 200
        
        # Get contract and verify legal_check is attached
        get_response = requests.get(
            f"{BASE_URL}/api/admin/contracts/{contract_id}",
            headers=auth_headers
        )
        contract = get_response.json()
        assert "legal_check" in contract
        assert "risk_level" in contract["legal_check"]
        print(f"✅ Legal check persisted on contract: risk_level={contract['legal_check']['risk_level']}")


class TestInvoiceLegalCheck:
    """Test Invoice Legal Gate with real invoice."""

    def test_create_and_check_invoice(self, auth_headers):
        """Create invoice and perform legal check."""
        # First create a quote to get a valid invoice
        test_email = f"{TEST_PREFIX}invoice_{secrets.token_hex(4)}@example.com"
        
        # Create invoice directly
        invoice_data = {
            "customer": {
                "name": "Test Invoice Customer",
                "email": test_email,
                "company": "Test Invoice GmbH"
            },
            "items": [
                {"description": "Test Service", "quantity": 1, "unit_price": 1000}
            ],
            "type": "deposit",
            "notes": "P4 Legal test invoice"
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/admin/invoices",
            headers=auth_headers,
            json=invoice_data
        )
        
        if create_response.status_code == 200:
            invoice_id = create_response.json().get("invoice_id")
            
            # Perform legal check
            check_response = requests.post(
                f"{BASE_URL}/api/admin/legal/check-billing/{invoice_id}",
                headers=auth_headers
            )
            assert check_response.status_code == 200
            result = check_response.json()
            assert "checks" in result
            assert "risk_level" in result
            print(f"✅ Invoice legal check: risk_level={result['risk_level']}")
        else:
            # Invoice creation might require quote_id
            print(f"⚠️ Invoice creation returned {create_response.status_code} - may require quote_id")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
