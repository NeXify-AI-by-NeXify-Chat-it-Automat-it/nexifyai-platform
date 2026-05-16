"""
Iteration 53 Backend Tests - NeXifyAI B2B Platform
Tests for:
1. Stripe removal verification (only Revolut in payments)
2. Customer list API
3. Customer casefile API
4. Direct email sending
5. Customer note functionality
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "p.courbois@icloud.com"
ADMIN_PASSWORD = "1def!xO2022!!"


class TestAdminAuth:
    """Admin authentication tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get admin authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access_token in response"
        return data["access_token"]
    
    def test_admin_login(self, auth_token):
        """Test admin login returns valid token"""
        assert auth_token is not None
        assert len(auth_token) > 20
        print(f"✓ Admin login successful, token length: {len(auth_token)}")


class TestStripeRemoval:
    """Verify Stripe has been completely removed"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        return response.json().get("access_token")
    
    def test_monitoring_health_no_stripe(self, auth_token):
        """GET /api/admin/monitoring/health should NOT contain stripe in payments"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/monitoring/health", headers=headers)
        
        assert response.status_code == 200, f"Health check failed: {response.text}"
        data = response.json()
        
        # Check that stripe is not in the response
        response_str = str(data).lower()
        assert "stripe" not in response_str, f"Stripe still found in health response: {data}"
        print("✓ Stripe not found in monitoring/health response")
        
        # Verify overall health
        assert data.get("overall") in ["healthy", "degraded"], f"Unexpected overall status: {data.get('overall')}"
        print(f"✓ System health: {data.get('overall')}")
    
    def test_monitoring_status_only_revolut(self, auth_token):
        """GET /api/admin/monitoring/status should only show Revolut in payments"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/monitoring/status", headers=headers)
        
        assert response.status_code == 200, f"Status check failed: {response.text}"
        data = response.json()
        
        # Check payments section
        systems = data.get("systems", {})
        payments = systems.get("payments", {})
        
        # Verify Revolut is present
        assert "revolut" in payments, f"Revolut not found in payments: {payments}"
        print(f"✓ Revolut found in payments: {payments.get('revolut')}")
        
        # Verify Stripe is NOT present
        assert "stripe" not in payments, f"Stripe still in payments: {payments}"
        print("✓ Stripe not in payments section")


class TestCustomerList:
    """Test customer list API"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        return response.json().get("access_token")
    
    def test_get_customers_list(self, auth_token):
        """GET /api/admin/customers returns customers list"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/customers", headers=headers)
        
        assert response.status_code == 200, f"Customers list failed: {response.text}"
        data = response.json()
        
        assert "customers" in data, "No customers key in response"
        customers = data["customers"]
        assert isinstance(customers, list), "Customers should be a list"
        
        # Should have 61+ customers based on test data
        customer_count = len(customers)
        print(f"✓ Found {customer_count} customers")
        assert customer_count >= 1, f"Expected at least 1 customer, got {customer_count}"
        
        # Verify customer structure
        if customers:
            first_customer = customers[0]
            assert "email" in first_customer, "Customer missing email field"
            print(f"✓ First customer email: {first_customer.get('email')}")
    
    def test_customers_search(self, auth_token):
        """Test customer search functionality"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(
            f"{BASE_URL}/api/admin/customers?search=courbois",
            headers=headers
        )
        
        assert response.status_code == 200, f"Customer search failed: {response.text}"
        data = response.json()
        customers = data.get("customers", [])
        
        # Should find the admin user
        found = any("courbois" in c.get("email", "").lower() for c in customers)
        print(f"✓ Search for 'courbois' returned {len(customers)} results, found admin: {found}")


class TestCustomerCasefile:
    """Test customer casefile API"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        return response.json().get("access_token")
    
    def test_get_casefile(self, auth_token):
        """GET /api/admin/customers/{email}/casefile returns full casefile"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        email = ADMIN_EMAIL
        
        response = requests.get(
            f"{BASE_URL}/api/admin/customers/{email}/casefile",
            headers=headers
        )
        
        assert response.status_code == 200, f"Casefile request failed: {response.text}"
        data = response.json()
        
        # Verify casefile structure
        assert "email" in data, "Casefile missing email"
        assert data["email"] == email.lower(), f"Email mismatch: {data['email']}"
        
        # Check for required sections
        required_sections = ["leads", "bookings", "quotes", "invoices", "contracts", "timeline", "emails_sent", "stats"]
        for section in required_sections:
            assert section in data, f"Casefile missing section: {section}"
        
        print(f"✓ Casefile has all required sections: {required_sections}")
        
        # Verify stats structure
        stats = data.get("stats", {})
        stat_fields = ["total_leads", "total_bookings", "total_quotes", "total_invoices", "total_contracts", "total_emails"]
        for field in stat_fields:
            assert field in stats, f"Stats missing field: {field}"
        
        print(f"✓ Stats: leads={stats.get('total_leads')}, bookings={stats.get('total_bookings')}, quotes={stats.get('total_quotes')}")
        
        # Verify contact info if present
        if data.get("contact"):
            print(f"✓ Contact info present")
        
        return data


class TestDirectEmail:
    """Test direct email sending from admin"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        return response.json().get("access_token")
    
    def test_send_direct_email(self, auth_token):
        """POST /api/admin/email/send sends email via SMTP"""
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "to_email": "test-iteration53@example.com",
            "subject": "Test Email - Iteration 53",
            "body": "This is a test email from iteration 53 testing."
        }
        
        response = requests.post(
            f"{BASE_URL}/api/admin/email/send",
            headers=headers,
            json=payload
        )
        
        assert response.status_code == 200, f"Email send failed: {response.text}"
        data = response.json()
        
        assert data.get("status") == "ok", f"Email status not ok: {data}"
        print(f"✓ Email send response: {data}")
        
        # Check result
        result = data.get("result", {})
        print(f"✓ Email result: sent={result.get('sent', 'unknown')}")


class TestCustomerNote:
    """Test customer note functionality"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        return response.json().get("access_token")
    
    def test_add_customer_note(self, auth_token):
        """POST /api/admin/customers/{email}/note adds a note"""
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        email = ADMIN_EMAIL
        note_text = f"Test note from iteration 53 - {os.urandom(4).hex()}"
        
        payload = {
            "text": note_text,
            "category": "test"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/admin/customers/{email}/note",
            headers=headers,
            json=payload
        )
        
        assert response.status_code == 200, f"Add note failed: {response.text}"
        data = response.json()
        
        assert data.get("status") == "ok", f"Note status not ok: {data}"
        assert "note" in data, "No note in response"
        
        note = data["note"]
        assert note.get("text") == note_text, f"Note text mismatch"
        assert "author" in note, "Note missing author"
        assert "created_at" in note, "Note missing created_at"
        
        print(f"✓ Note added successfully: {note.get('text')[:50]}...")
        print(f"✓ Note author: {note.get('author')}")
    
    def test_verify_note_in_casefile(self, auth_token):
        """Verify note appears in casefile after adding"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        email = ADMIN_EMAIL
        
        # First add a unique note
        note_text = f"Verification note - {os.urandom(4).hex()}"
        requests.post(
            f"{BASE_URL}/api/admin/customers/{email}/note",
            headers={**headers, "Content-Type": "application/json"},
            json={"text": note_text}
        )
        
        # Then get casefile and verify
        response = requests.get(
            f"{BASE_URL}/api/admin/customers/{email}/casefile",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Notes should be in contact
        contact = data.get("contact", {})
        notes = contact.get("notes", [])
        
        print(f"✓ Found {len(notes)} notes in casefile contact")


class TestAdditionalEndpoints:
    """Test additional admin endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        return response.json().get("access_token")
    
    def test_admin_stats(self, auth_token):
        """GET /api/admin/stats returns dashboard stats"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/stats", headers=headers)
        
        assert response.status_code == 200, f"Stats failed: {response.text}"
        data = response.json()
        
        assert "total_leads" in data, "Missing total_leads"
        print(f"✓ Stats: total_leads={data.get('total_leads')}, upcoming_bookings={data.get('upcoming_bookings')}")
    
    def test_admin_leads(self, auth_token):
        """GET /api/admin/leads returns leads list"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/leads", headers=headers)
        
        assert response.status_code == 200, f"Leads failed: {response.text}"
        data = response.json()
        
        assert "leads" in data, "Missing leads"
        assert "total" in data, "Missing total"
        print(f"✓ Leads: total={data.get('total')}, returned={len(data.get('leads', []))}")
    
    def test_admin_bookings(self, auth_token):
        """GET /api/admin/bookings returns bookings list"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/bookings", headers=headers)
        
        assert response.status_code == 200, f"Bookings failed: {response.text}"
        data = response.json()
        
        assert "bookings" in data, "Missing bookings"
        print(f"✓ Bookings: total={data.get('total')}, returned={len(data.get('bookings', []))}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
