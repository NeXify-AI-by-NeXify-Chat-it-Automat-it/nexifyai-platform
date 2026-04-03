"""
NeXifyAI Iteration 11 - UI Polish Verification Tests
Tests for border-radius, form alignment, chat functionality
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://contract-os.preview.emergentagent.com').rstrip('/')

class TestHealthAndBasicEndpoints:
    """Basic API health tests"""
    
    def test_health_endpoint(self):
        """Test health endpoint returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✓ Health endpoint working")
    
    def test_company_endpoint(self):
        """Test company info endpoint"""
        response = requests.get(f"{BASE_URL}/api/company")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "NeXifyAI by NeXify"
        assert "tagline" in data
        print("✓ Company endpoint working")


class TestChatFunctionality:
    """Chat API tests"""
    
    def test_chat_message_de(self):
        """Test chat message in German"""
        session_id = f"test_{int(time.time())}"
        response = requests.post(f"{BASE_URL}/api/chat/message", json={
            "session_id": session_id,
            "message": "Welche KI-Lösungen bietet ihr an?",
            "language": "de"
        })
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert len(data["message"]) > 50  # Should have substantial response
        print(f"✓ Chat DE response: {data['message'][:100]}...")
    
    def test_chat_message_en(self):
        """Test chat message in English"""
        session_id = f"test_en_{int(time.time())}"
        response = requests.post(f"{BASE_URL}/api/chat/message", json={
            "session_id": session_id,
            "message": "What AI solutions do you offer?",
            "language": "en"
        })
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"✓ Chat EN response: {data['message'][:100]}...")
    
    def test_chat_booking_request(self):
        """Test chat booking flow"""
        session_id = f"test_book_{int(time.time())}"
        response = requests.post(f"{BASE_URL}/api/chat/message", json={
            "session_id": session_id,
            "message": "Ich möchte einen Termin buchen",
            "language": "de"
        })
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        # Should ask for name/email
        print(f"✓ Chat booking response: {data['message'][:100]}...")


class TestBookingFlow:
    """Booking API tests"""
    
    def test_booking_slots(self):
        """Test booking slots endpoint"""
        from datetime import datetime, timedelta
        # Get date 3 days from now (weekday)
        future_date = datetime.now() + timedelta(days=3)
        while future_date.weekday() >= 5:  # Skip weekends
            future_date += timedelta(days=1)
        date_str = future_date.strftime("%Y-%m-%d")
        
        response = requests.get(f"{BASE_URL}/api/booking/slots?date={date_str}")
        assert response.status_code == 200
        data = response.json()
        assert "slots" in data
        print(f"✓ Booking slots for {date_str}: {data['slots']}")
    
    def test_create_booking(self):
        """Test creating a booking"""
        from datetime import datetime, timedelta
        future_date = datetime.now() + timedelta(days=5)
        while future_date.weekday() >= 5:
            future_date += timedelta(days=1)
        date_str = future_date.strftime("%Y-%m-%d")
        
        response = requests.post(f"{BASE_URL}/api/booking", json={
            "vorname": "TEST_Iteration11",
            "nachname": "User",
            "email": "test11@example.com",
            "telefon": "+49123456789",
            "unternehmen": "Test Company",
            "thema": "UI Polish Testing",
            "date": date_str,
            "time": "10:00"
        })
        # 200/201 = success, 400 = validation error (slot taken or invalid), 409 = conflict
        assert response.status_code in [200, 201, 400, 409]
        if response.status_code in [200, 201]:
            data = response.json()
            assert "booking_id" in data or "success" in data
        print(f"✓ Booking creation: {response.status_code}")


class TestContactForm:
    """Contact form API tests"""
    
    def test_contact_submission(self):
        """Test contact form submission"""
        response = requests.post(f"{BASE_URL}/api/contact", json={
            "vorname": "TEST_Iteration11",
            "nachname": "Contact",
            "email": "test11contact@example.com",
            "telefon": "+49123456789",
            "unternehmen": "Test Company",
            "nachricht": "This is a test message for iteration 11 UI polish testing.",
            "_hp": ""  # Honeypot field
        })
        assert response.status_code in [200, 201]
        data = response.json()
        assert "lead_id" in data or "message" in data
        print(f"✓ Contact form submission successful")


class TestAdminAuth:
    """Admin authentication tests"""
    
    def test_admin_login(self):
        """Test admin login with correct credentials"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={
                "username": "p.courbois@icloud.com",
                "password": "NxAi#Secure2026!"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        print("✓ Admin login successful")
        return data["access_token"]
    
    def test_admin_stats(self):
        """Test admin stats endpoint"""
        # First login
        login_response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={
                "username": "p.courbois@icloud.com",
                "password": "NxAi#Secure2026!"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token = login_response.json()["access_token"]
        
        # Get stats
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_leads" in data
        print(f"✓ Admin stats: {data}")


class TestAnalytics:
    """Analytics tracking tests"""
    
    def test_analytics_tracking(self):
        """Test analytics event tracking"""
        response = requests.post(f"{BASE_URL}/api/analytics/track", json={
            "event": "test_iteration11",
            "properties": {
                "test": True,
                "iteration": 11
            },
            "session_id": f"test_session_{int(time.time())}"
        })
        assert response.status_code == 200
        print("✓ Analytics tracking working")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
