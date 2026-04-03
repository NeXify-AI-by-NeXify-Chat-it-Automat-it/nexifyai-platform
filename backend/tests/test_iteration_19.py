"""
Iteration 19 Backend Tests - NeXifyAI Platform
Tests for:
- WhatsApp QR-Bridge endpoints (pair, status, reconnect, simulate-connect, send, disconnect, reset, messages)
- AI Agent endpoints (list agents, route task, execute agent)
- Customer Memory endpoints (get memory, add facts)
- Conversations endpoints (list, get detail, reply)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
ADMIN_EMAIL = "p.courbois@icloud.com"
ADMIN_PASSWORD = "NxAi#Secure2026!"


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
        assert "access_token" in data
        return data["access_token"]
    
    def test_admin_login_success(self):
        """Test admin login with valid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_admin_login_invalid_credentials(self):
        """Test admin login with invalid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": "wrong@email.com", "password": "wrongpassword"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 401


class TestWhatsAppEndpoints:
    """WhatsApp QR-Bridge connector tests"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get authenticated headers"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    def test_whatsapp_status(self, auth_headers):
        """GET /api/admin/whatsapp/status - Get WhatsApp session status"""
        response = requests.get(f"{BASE_URL}/api/admin/whatsapp/status", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "session_id" in data
        assert data["status"] in ["unpaired", "pairing", "connected", "reconnecting", "disconnected", "failed"]
    
    def test_whatsapp_reset(self, auth_headers):
        """POST /api/admin/whatsapp/reset - Reset WhatsApp session"""
        response = requests.post(f"{BASE_URL}/api/admin/whatsapp/reset", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "reset"
        assert "session_id" in data
    
    def test_whatsapp_pair(self, auth_headers):
        """POST /api/admin/whatsapp/pair - Initiate QR pairing"""
        response = requests.post(f"{BASE_URL}/api/admin/whatsapp/pair", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pairing"
        assert "qr_code" in data
        assert "session_id" in data
        assert "message" in data
    
    def test_whatsapp_simulate_connect(self, auth_headers):
        """POST /api/admin/whatsapp/simulate-connect - Simulate successful connection"""
        # First ensure we're in pairing state
        requests.post(f"{BASE_URL}/api/admin/whatsapp/pair", headers=auth_headers)
        
        response = requests.post(f"{BASE_URL}/api/admin/whatsapp/simulate-connect", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "connected"
        assert "session_id" in data
        assert data["phone_number"] == "+31613318856"
    
    def test_whatsapp_status_after_connect(self, auth_headers):
        """Verify status shows connected after simulate-connect"""
        response = requests.get(f"{BASE_URL}/api/admin/whatsapp/status", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "connected"
        assert data["phone_number"] == "+31613318856"
    
    def test_whatsapp_send_message(self, auth_headers):
        """POST /api/admin/whatsapp/send - Send WhatsApp message when connected"""
        # Ensure connected
        requests.post(f"{BASE_URL}/api/admin/whatsapp/simulate-connect", headers=auth_headers)
        
        response = requests.post(
            f"{BASE_URL}/api/admin/whatsapp/send",
            headers=auth_headers,
            json={"to": "+49171234567", "content": "TEST_Iteration19_Message"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "sent"
        assert "message_id" in data
        assert "conversation_id" in data
    
    def test_whatsapp_send_empty_message_fails(self, auth_headers):
        """POST /api/admin/whatsapp/send - Empty message should fail"""
        response = requests.post(
            f"{BASE_URL}/api/admin/whatsapp/send",
            headers=auth_headers,
            json={"to": "+49171234567", "content": ""}
        )
        assert response.status_code == 400
    
    def test_whatsapp_messages(self, auth_headers):
        """GET /api/admin/whatsapp/messages - List WhatsApp messages"""
        response = requests.get(f"{BASE_URL}/api/admin/whatsapp/messages?limit=10", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert isinstance(data["messages"], list)
    
    def test_whatsapp_disconnect(self, auth_headers):
        """POST /api/admin/whatsapp/disconnect - Disconnect session"""
        response = requests.post(f"{BASE_URL}/api/admin/whatsapp/disconnect", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "disconnected"
    
    def test_whatsapp_reconnect(self, auth_headers):
        """POST /api/admin/whatsapp/reconnect - Reconnect disconnected session"""
        # Ensure disconnected first
        requests.post(f"{BASE_URL}/api/admin/whatsapp/disconnect", headers=auth_headers)
        
        response = requests.post(f"{BASE_URL}/api/admin/whatsapp/reconnect", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["reconnecting", "already_connected"]


class TestAgentEndpoints:
    """AI Agent orchestrator and sub-agent tests"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get authenticated headers"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    def test_list_agents(self, auth_headers):
        """GET /api/admin/agents - List all available agents"""
        response = requests.get(f"{BASE_URL}/api/admin/agents", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        # Check orchestrator
        assert "orchestrator" in data
        assert data["orchestrator"]["status"] == "active"
        assert "model" in data["orchestrator"]
        
        # Check sub-agents (research, outreach, offer, support)
        assert "agents" in data
        agents = data["agents"]
        expected_agents = ["research", "outreach", "offer", "support"]
        for agent_name in expected_agents:
            assert agent_name in agents, f"Agent '{agent_name}' not found"
            assert agents[agent_name]["status"] == "active"
            assert "role" in agents[agent_name]
    
    def test_agent_route_empty_task_fails(self, auth_headers):
        """POST /api/admin/agents/route - Empty task should fail"""
        response = requests.post(
            f"{BASE_URL}/api/admin/agents/route",
            headers=auth_headers,
            json={"task": "", "context": {}}
        )
        assert response.status_code == 400
    
    def test_agent_execute_invalid_agent(self, auth_headers):
        """POST /api/admin/agents/{agent}/execute - Invalid agent should return 404"""
        response = requests.post(
            f"{BASE_URL}/api/admin/agents/nonexistent/execute",
            headers=auth_headers,
            json={"task": "Test task"}
        )
        assert response.status_code == 404
    
    def test_agent_execute_empty_task_fails(self, auth_headers):
        """POST /api/admin/agents/{agent}/execute - Empty task should fail"""
        response = requests.post(
            f"{BASE_URL}/api/admin/agents/research/execute",
            headers=auth_headers,
            json={"task": ""}
        )
        assert response.status_code == 400


class TestConversationEndpoints:
    """Unified conversation management tests"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get authenticated headers"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    def test_list_conversations(self, auth_headers):
        """GET /api/admin/conversations - List all conversations"""
        response = requests.get(f"{BASE_URL}/api/admin/conversations?limit=30", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "conversations" in data
        assert isinstance(data["conversations"], list)
    
    def test_conversation_detail_not_found(self, auth_headers):
        """GET /api/admin/conversations/{id} - Non-existent conversation returns 404"""
        response = requests.get(
            f"{BASE_URL}/api/admin/conversations/nonexistent_id_12345",
            headers=auth_headers
        )
        assert response.status_code == 404
    
    def test_conversation_reply_not_found(self, auth_headers):
        """POST /api/admin/conversations/{id}/reply - Non-existent conversation returns 404"""
        response = requests.post(
            f"{BASE_URL}/api/admin/conversations/nonexistent_id_12345/reply",
            headers=auth_headers,
            json={"content": "Test reply", "channel": "chat"}
        )
        assert response.status_code == 404
    
    def test_conversation_reply_empty_content_fails(self, auth_headers):
        """POST /api/admin/conversations/{id}/reply - Empty content should fail"""
        # First get a valid conversation if exists
        list_response = requests.get(f"{BASE_URL}/api/admin/conversations?limit=1", headers=auth_headers)
        conversations = list_response.json().get("conversations", [])
        
        if conversations:
            convo_id = conversations[0]["conversation_id"]
            response = requests.post(
                f"{BASE_URL}/api/admin/conversations/{convo_id}/reply",
                headers=auth_headers,
                json={"content": "", "channel": "chat"}
            )
            assert response.status_code == 400
        else:
            pytest.skip("No conversations available to test reply")


class TestCustomerMemoryEndpoints:
    """Customer memory and context tests"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get authenticated headers"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    def test_get_customer_memory(self, auth_headers):
        """GET /api/admin/customer-memory/{email} - Get customer memory context"""
        test_email = "test@example.com"
        response = requests.get(
            f"{BASE_URL}/api/admin/customer-memory/{test_email}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert data["email"] == test_email
        # Memory context fields
        assert "memory_context" in data or "lead" in data or "quotes" in data
    
    def test_add_customer_memory_fact(self, auth_headers):
        """POST /api/admin/customer-memory/{email}/facts - Add memory fact"""
        test_email = "test_iter19@example.com"
        response = requests.post(
            f"{BASE_URL}/api/admin/customer-memory/{test_email}/facts",
            headers=auth_headers,
            json={"fact": "TEST_Iteration19_Fact: Customer prefers email communication"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok" or "fact_id" in data or "memory_id" in data


class TestExistingEndpoints:
    """Verify existing endpoints still work (regression)"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get authenticated headers"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    def test_health_endpoint(self):
        """GET /api/health - Health check"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_admin_stats(self, auth_headers):
        """GET /api/admin/stats - Admin dashboard stats"""
        response = requests.get(f"{BASE_URL}/api/admin/stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_leads" in data or "by_status" in data
    
    def test_admin_leads(self, auth_headers):
        """GET /api/admin/leads - List leads"""
        response = requests.get(f"{BASE_URL}/api/admin/leads", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "leads" in data
    
    def test_admin_chat_sessions(self, auth_headers):
        """GET /api/admin/chat-sessions - List chat sessions"""
        response = requests.get(f"{BASE_URL}/api/admin/chat-sessions?limit=10", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data
    
    def test_admin_timeline(self, auth_headers):
        """GET /api/admin/timeline - Get timeline events"""
        response = requests.get(f"{BASE_URL}/api/admin/timeline?limit=10", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "events" in data
    
    def test_product_tariffs(self):
        """GET /api/product/tariffs - Get product tariffs"""
        response = requests.get(f"{BASE_URL}/api/product/tariffs")
        assert response.status_code == 200
        data = response.json()
        assert "tariffs" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
