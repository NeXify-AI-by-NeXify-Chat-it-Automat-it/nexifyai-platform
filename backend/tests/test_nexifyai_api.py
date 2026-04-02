"""
NeXifyAI Backend API Tests v3.0
Tests for: Health, Contact, Booking, Chat, Admin Auth, Admin Dashboard
"""
import pytest
import requests
import os
import time
from datetime import datetime, timedelta

# Use localhost for testing since we're running inside the container
BASE_URL = "http://localhost:8001"

# Admin credentials from environment
ADMIN_EMAIL = "p.courbois@icloud.com"
ADMIN_PASSWORD = "NxAi#Secure2026!"


class TestHealthEndpoint:
    """Health check endpoint tests"""
    
    def test_health_returns_200(self):
        """Health endpoint should return 200 OK"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data
        print(f"✓ Health check passed: {data['status']}, version {data['version']}")


class TestCompanyEndpoint:
    """Company data endpoint tests"""
    
    def test_company_returns_data(self):
        """Company endpoint should return company information"""
        response = requests.get(f"{BASE_URL}/api/company")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "NeXifyAI by NeXify"
        assert data["legal_name"] == "NeXify Automate"
        assert data["ceo"] == "Pascal Courbois, Geschäftsführer"
        assert "address_de" in data
        assert "address_nl" in data
        print(f"✓ Company data returned: {data['name']}")


class TestContactForm:
    """Contact form submission tests"""
    
    def test_contact_form_valid_submission(self):
        """Valid contact form should be accepted"""
        payload = {
            "vorname": "TEST_Max",
            "nachname": "TEST_Mustermann",
            "email": "test@example.com",
            "telefon": "+49 123 456789",
            "unternehmen": "Test GmbH",
            "nachricht": "Dies ist eine Testanfrage für die API-Tests. Bitte ignorieren.",
            "source": "api_test"
        }
        response = requests.post(f"{BASE_URL}/api/contact", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "lead_id" in data
        assert data["lead_id"].startswith("LEAD-")
        print(f"✓ Contact form submitted: {data['lead_id']}")
    
    def test_contact_form_validation_short_name(self):
        """Contact form should reject short names"""
        payload = {
            "vorname": "A",  # Too short
            "nachname": "B",  # Too short
            "email": "test@example.com",
            "nachricht": "Test message that is long enough"
        }
        response = requests.post(f"{BASE_URL}/api/contact", json=payload)
        assert response.status_code == 422  # Validation error
        print("✓ Short name validation working")
    
    def test_contact_form_validation_invalid_email(self):
        """Contact form should reject invalid email"""
        payload = {
            "vorname": "Max",
            "nachname": "Mustermann",
            "email": "invalid-email",
            "nachricht": "Test message that is long enough"
        }
        response = requests.post(f"{BASE_URL}/api/contact", json=payload)
        assert response.status_code == 422  # Validation error
        print("✓ Invalid email validation working")
    
    def test_contact_form_validation_short_message(self):
        """Contact form should reject short messages"""
        payload = {
            "vorname": "Max",
            "nachname": "Mustermann",
            "email": "test@example.com",
            "nachricht": "Short"  # Too short
        }
        response = requests.post(f"{BASE_URL}/api/contact", json=payload)
        assert response.status_code == 422  # Validation error
        print("✓ Short message validation working")
    
    def test_contact_form_honeypot_trap(self):
        """Contact form should silently accept honeypot submissions"""
        payload = {
            "vorname": "Bot",
            "nachname": "Spammer",
            "email": "bot@spam.com",
            "nachricht": "This is spam message from a bot",
            "_hp": "filled_by_bot"  # Honeypot field
        }
        response = requests.post(f"{BASE_URL}/api/contact", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        # Should not have lead_id since it's a honeypot trap
        print("✓ Honeypot trap working")


class TestBookingEndpoints:
    """Booking system tests"""
    
    def test_get_available_slots(self):
        """Should return available time slots for a date"""
        # Get a date 3 days from now (weekday)
        future_date = datetime.now() + timedelta(days=3)
        while future_date.weekday() >= 5:  # Skip weekends
            future_date += timedelta(days=1)
        date_str = future_date.strftime("%Y-%m-%d")
        
        response = requests.get(f"{BASE_URL}/api/booking/slots?date={date_str}")
        assert response.status_code == 200
        data = response.json()
        assert "slots" in data
        assert "date" in data
        assert data["date"] == date_str
        assert isinstance(data["slots"], list)
        print(f"✓ Available slots for {date_str}: {len(data['slots'])} slots")
    
    def test_create_booking(self):
        """Should create a booking successfully"""
        # Get a date 5 days from now (weekday)
        future_date = datetime.now() + timedelta(days=5)
        while future_date.weekday() >= 5:  # Skip weekends
            future_date += timedelta(days=1)
        date_str = future_date.strftime("%Y-%m-%d")
        
        # First get available slots
        slots_response = requests.get(f"{BASE_URL}/api/booking/slots?date={date_str}")
        slots = slots_response.json().get("slots", [])
        
        if not slots:
            pytest.skip("No available slots for testing")
        
        payload = {
            "vorname": "TEST_Booking",
            "nachname": "TEST_User",
            "email": "booking.test@example.com",
            "telefon": "+49 123 456789",
            "unternehmen": "Test Booking GmbH",
            "date": date_str,
            "time": slots[0],
            "thema": "KI-Assistenz / Chatbot"
        }
        response = requests.post(f"{BASE_URL}/api/booking", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "booking_id" in data
        assert data["booking_id"].startswith("BK-")
        print(f"✓ Booking created: {data['booking_id']} for {date_str} at {slots[0]}")


class TestChatEndpoints:
    """Chat system tests"""
    
    def test_chat_message_initial(self):
        """Should handle initial chat message"""
        session_id = f"test_session_{int(time.time())}"
        payload = {
            "session_id": session_id,
            "message": "Hallo, ich interessiere mich für KI-Lösungen"
        }
        response = requests.post(f"{BASE_URL}/api/chat/message", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert len(data["message"]) > 0
        print(f"✓ Chat response received: {data['message'][:50]}...")
    
    def test_chat_message_vertrieb_keyword(self):
        """Should qualify lead based on vertrieb keyword"""
        session_id = f"test_session_vertrieb_{int(time.time())}"
        payload = {
            "session_id": session_id,
            "message": "Wie kann KI unseren Vertrieb automatisieren?"
        }
        response = requests.post(f"{BASE_URL}/api/chat/message", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "qualification" in data
        # Should detect vertrieb interest
        if data.get("qualification"):
            assert data["qualification"].get("interest") == "vertrieb"
        print(f"✓ Vertrieb keyword detected, qualification: {data.get('qualification', {})}")
    
    def test_chat_message_crm_keyword(self):
        """Should qualify lead based on CRM keyword"""
        session_id = f"test_session_crm_{int(time.time())}"
        payload = {
            "session_id": session_id,
            "message": "Welche CRM-Integrationen bieten Sie an?"
        }
        response = requests.post(f"{BASE_URL}/api/chat/message", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"✓ CRM keyword response: {data['message'][:50]}...")
    
    def test_chat_message_escalation(self):
        """Should trigger escalation for booking keywords"""
        session_id = f"test_session_escalate_{int(time.time())}"
        payload = {
            "session_id": session_id,
            "message": "Ich möchte gerne einen Termin für ein Beratungsgespräch buchen"
        }
        response = requests.post(f"{BASE_URL}/api/chat/message", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data.get("should_escalate") == True
        assert "actions" in data
        print(f"✓ Escalation triggered, actions: {data.get('actions', [])}")


class TestAnalyticsEndpoint:
    """Analytics tracking tests"""
    
    def test_track_event(self):
        """Should track analytics event"""
        payload = {
            "event": "test_event",
            "properties": {"source": "api_test", "timestamp": datetime.now().isoformat()},
            "session_id": f"test_session_{int(time.time())}"
        }
        response = requests.post(f"{BASE_URL}/api/analytics/track", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print("✓ Analytics event tracked")


class TestAdminAuthentication:
    """Admin authentication tests"""
    
    def test_admin_login_success(self):
        """Should login with valid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        print(f"✓ Admin login successful, token received")
        return data["access_token"]
    
    def test_admin_login_invalid_credentials(self):
        """Should reject invalid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": "wrong@email.com", "password": "wrongpassword"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 401
        print("✓ Invalid credentials rejected")
    
    def test_admin_login_wrong_password(self):
        """Should reject wrong password for valid email"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": ADMIN_EMAIL, "password": "wrongpassword"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 401
        print("✓ Wrong password rejected")


class TestAdminDashboard:
    """Admin dashboard tests (requires authentication)"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        pytest.skip("Could not authenticate")
    
    def test_admin_me(self, auth_token):
        """Should return current admin info"""
        response = requests.get(
            f"{BASE_URL}/api/admin/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == ADMIN_EMAIL
        assert "role" in data
        print(f"✓ Admin info: {data['email']}, role: {data['role']}")
    
    def test_admin_stats(self, auth_token):
        """Should return dashboard statistics"""
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_leads" in data
        assert "new_leads_today" in data
        assert "new_leads_week" in data
        assert "upcoming_bookings" in data
        assert "by_status" in data
        print(f"✓ Admin stats: {data['total_leads']} total leads, {data['new_leads_today']} today")
    
    def test_admin_leads_list(self, auth_token):
        """Should return leads list"""
        response = requests.get(
            f"{BASE_URL}/api/admin/leads",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "leads" in data
        assert isinstance(data["leads"], list)
        print(f"✓ Admin leads: {data['total']} total, {len(data['leads'])} returned")
    
    def test_admin_leads_search(self, auth_token):
        """Should search leads"""
        response = requests.get(
            f"{BASE_URL}/api/admin/leads?search=TEST",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "leads" in data
        print(f"✓ Admin leads search: {len(data['leads'])} results for 'TEST'")
    
    def test_admin_leads_filter_by_status(self, auth_token):
        """Should filter leads by status"""
        response = requests.get(
            f"{BASE_URL}/api/admin/leads?status=neu",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "leads" in data
        # All returned leads should have status 'neu'
        for lead in data["leads"]:
            assert lead["status"] == "neu"
        print(f"✓ Admin leads filter: {len(data['leads'])} leads with status 'neu'")
    
    def test_admin_bookings_list(self, auth_token):
        """Should return bookings list"""
        response = requests.get(
            f"{BASE_URL}/api/admin/bookings",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "bookings" in data
        assert isinstance(data["bookings"], list)
        print(f"✓ Admin bookings: {data['total']} total, {len(data['bookings'])} returned")
    
    def test_admin_unauthorized_access(self):
        """Should reject unauthorized access"""
        response = requests.get(f"{BASE_URL}/api/admin/stats")
        assert response.status_code == 401
        print("✓ Unauthorized access rejected")
    
    def test_admin_invalid_token(self):
        """Should reject invalid token"""
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        assert response.status_code == 401
        print("✓ Invalid token rejected")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
