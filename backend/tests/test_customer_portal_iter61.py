"""
Iteration 61 - Customer Portal Backend API Tests
Tests for: Customer Requests, Bookings, Messages, Support Tickets
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Customer JWT token (expires 2026-04-05)
CUSTOMER_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMmVAZTJlLXRlc3QuZGUiLCJyb2xlIjoiY3VzdG9tZXIiLCJleHAiOjE3NzUzNzYxMDR9.9OC_ao69s0CxsCPzGnMIoVbpqZqeTdPX7wJwuuDw570"
CUSTOMER_EMAIL = "e2e@e2e-test.de"


@pytest.fixture
def customer_headers():
    """Headers with customer JWT auth."""
    return {
        "Authorization": f"Bearer {CUSTOMER_JWT}",
        "Content-Type": "application/json"
    }


class TestCustomerDashboard:
    """Test customer dashboard endpoint."""
    
    def test_dashboard_access(self, customer_headers):
        """Test customer can access dashboard."""
        response = requests.get(f"{BASE_URL}/api/customer/dashboard", headers=customer_headers)
        print(f"Dashboard response: {response.status_code}")
        assert response.status_code == 200
        data = response.json()
        # Dashboard should return customer info
        assert "customer_name" in data or "email" in data


class TestCustomerRequests:
    """Test customer request endpoints: POST/GET /api/customer/requests"""
    
    def test_create_request(self, customer_headers):
        """Test creating a new customer request."""
        unique_id = uuid.uuid4().hex[:8]
        payload = {
            "type": "project",
            "subject": f"TEST_Request_{unique_id}",
            "description": "Test request description for iteration 61",
            "budget_range": "5.000 - 10.000 EUR",
            "urgency": "normal"
        }
        response = requests.post(f"{BASE_URL}/api/customer/requests", json=payload, headers=customer_headers)
        print(f"Create request response: {response.status_code} - {response.text}")
        assert response.status_code == 200
        data = response.json()
        assert "request_id" in data
        assert data["status"] == "new"
        return data["request_id"]
    
    def test_list_requests(self, customer_headers):
        """Test listing customer requests."""
        response = requests.get(f"{BASE_URL}/api/customer/requests", headers=customer_headers)
        print(f"List requests response: {response.status_code}")
        assert response.status_code == 200
        data = response.json()
        assert "requests" in data
        assert isinstance(data["requests"], list)
    
    def test_create_and_verify_request(self, customer_headers):
        """Create request and verify it appears in list."""
        unique_id = uuid.uuid4().hex[:8]
        payload = {
            "type": "quote",
            "subject": f"TEST_Verify_{unique_id}",
            "description": "Verify request appears in list",
            "urgency": "high"
        }
        # Create
        create_resp = requests.post(f"{BASE_URL}/api/customer/requests", json=payload, headers=customer_headers)
        assert create_resp.status_code == 200
        request_id = create_resp.json()["request_id"]
        
        # Verify in list
        list_resp = requests.get(f"{BASE_URL}/api/customer/requests", headers=customer_headers)
        assert list_resp.status_code == 200
        requests_list = list_resp.json()["requests"]
        found = any(r["request_id"] == request_id for r in requests_list)
        assert found, f"Request {request_id} not found in list"
        print(f"Request {request_id} verified in list")


class TestCustomerBookings:
    """Test customer booking endpoint: POST /api/customer/bookings"""
    
    def test_create_booking(self, customer_headers):
        """Test creating a new booking."""
        payload = {
            "date": "2026-02-15",
            "time": "14:00",
            "type": "beratung",
            "notes": "Test booking for iteration 61"
        }
        response = requests.post(f"{BASE_URL}/api/customer/bookings", json=payload, headers=customer_headers)
        print(f"Create booking response: {response.status_code} - {response.text}")
        assert response.status_code == 200
        data = response.json()
        assert "booking_id" in data
        assert data["status"] == "requested"
    
    def test_create_booking_review_type(self, customer_headers):
        """Test creating a review booking."""
        payload = {
            "date": "2026-02-20",
            "time": "10:30",
            "type": "review",
            "notes": "Project review meeting"
        }
        response = requests.post(f"{BASE_URL}/api/customer/bookings", json=payload, headers=customer_headers)
        assert response.status_code == 200
        data = response.json()
        assert "booking_id" in data


class TestCustomerMessages:
    """Test customer message endpoints: POST/GET /api/customer/messages"""
    
    def test_send_message(self, customer_headers):
        """Test sending a customer message."""
        unique_id = uuid.uuid4().hex[:8]
        payload = {
            "subject": f"TEST_Message_{unique_id}",
            "content": "Test message content for iteration 61",
            "category": "general"
        }
        response = requests.post(f"{BASE_URL}/api/customer/messages", json=payload, headers=customer_headers)
        print(f"Send message response: {response.status_code} - {response.text}")
        assert response.status_code == 200
        data = response.json()
        assert "message_id" in data
        assert data["status"] == "sent"
    
    def test_list_messages(self, customer_headers):
        """Test listing customer messages."""
        response = requests.get(f"{BASE_URL}/api/customer/messages", headers=customer_headers)
        print(f"List messages response: {response.status_code}")
        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert isinstance(data["messages"], list)
    
    def test_send_and_verify_message(self, customer_headers):
        """Send message and verify it appears in list."""
        unique_id = uuid.uuid4().hex[:8]
        payload = {
            "subject": f"TEST_VerifyMsg_{unique_id}",
            "content": "Verify message appears in list",
            "category": "support"
        }
        # Send
        send_resp = requests.post(f"{BASE_URL}/api/customer/messages", json=payload, headers=customer_headers)
        assert send_resp.status_code == 200
        message_id = send_resp.json()["message_id"]
        
        # Verify in list
        list_resp = requests.get(f"{BASE_URL}/api/customer/messages", headers=customer_headers)
        assert list_resp.status_code == 200
        messages_list = list_resp.json()["messages"]
        found = any(m["message_id"] == message_id for m in messages_list)
        assert found, f"Message {message_id} not found in list"
        print(f"Message {message_id} verified in list")


class TestCustomerSupport:
    """Test customer support ticket endpoints: POST/GET /api/customer/support"""
    
    def test_create_support_ticket(self, customer_headers):
        """Test creating a support ticket."""
        unique_id = uuid.uuid4().hex[:8]
        payload = {
            "subject": f"TEST_Ticket_{unique_id}",
            "description": "Test support ticket for iteration 61",
            "category": "technical",
            "priority": "normal"
        }
        response = requests.post(f"{BASE_URL}/api/customer/support", json=payload, headers=customer_headers)
        print(f"Create ticket response: {response.status_code} - {response.text}")
        assert response.status_code == 200
        data = response.json()
        assert "ticket_id" in data
        assert data["status"] == "open"
    
    def test_list_support_tickets(self, customer_headers):
        """Test listing support tickets."""
        response = requests.get(f"{BASE_URL}/api/customer/support", headers=customer_headers)
        print(f"List tickets response: {response.status_code}")
        assert response.status_code == 200
        data = response.json()
        assert "tickets" in data
        assert isinstance(data["tickets"], list)
    
    def test_create_and_verify_ticket(self, customer_headers):
        """Create ticket and verify it appears in list."""
        unique_id = uuid.uuid4().hex[:8]
        payload = {
            "subject": f"TEST_VerifyTicket_{unique_id}",
            "description": "Verify ticket appears in list",
            "category": "billing",
            "priority": "high"
        }
        # Create
        create_resp = requests.post(f"{BASE_URL}/api/customer/support", json=payload, headers=customer_headers)
        assert create_resp.status_code == 200
        ticket_id = create_resp.json()["ticket_id"]
        
        # Verify in list
        list_resp = requests.get(f"{BASE_URL}/api/customer/support", headers=customer_headers)
        assert list_resp.status_code == 200
        tickets_list = list_resp.json()["tickets"]
        found = any(t["ticket_id"] == ticket_id for t in tickets_list)
        assert found, f"Ticket {ticket_id} not found in list"
        print(f"Ticket {ticket_id} verified in list")


class TestCustomerProfile:
    """Test customer profile endpoint."""
    
    def test_get_profile(self, customer_headers):
        """Test getting customer profile."""
        response = requests.get(f"{BASE_URL}/api/customer/profile", headers=customer_headers)
        print(f"Get profile response: {response.status_code}")
        # Profile endpoint should exist
        assert response.status_code in [200, 404]  # 404 if no profile yet


class TestCustomerContracts:
    """Test customer contracts endpoint."""
    
    def test_list_contracts(self, customer_headers):
        """Test listing customer contracts."""
        response = requests.get(f"{BASE_URL}/api/customer/contracts", headers=customer_headers)
        print(f"List contracts response: {response.status_code}")
        assert response.status_code == 200
        data = response.json()
        assert "contracts" in data


class TestCustomerProjects:
    """Test customer projects endpoint."""
    
    def test_list_projects(self, customer_headers):
        """Test listing customer projects."""
        response = requests.get(f"{BASE_URL}/api/customer/projects", headers=customer_headers)
        print(f"List projects response: {response.status_code}")
        assert response.status_code == 200
        data = response.json()
        assert "projects" in data


class TestUnauthorizedAccess:
    """Test that endpoints require authentication."""
    
    def test_requests_without_auth(self):
        """Test requests endpoint without auth."""
        response = requests.get(f"{BASE_URL}/api/customer/requests")
        assert response.status_code in [401, 403, 422]
    
    def test_messages_without_auth(self):
        """Test messages endpoint without auth."""
        response = requests.get(f"{BASE_URL}/api/customer/messages")
        assert response.status_code in [401, 403, 422]
    
    def test_support_without_auth(self):
        """Test support endpoint without auth."""
        response = requests.get(f"{BASE_URL}/api/customer/support")
        assert response.status_code in [401, 403, 422]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
