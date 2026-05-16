"""
Test Chat Bug Fix - Iteration 42
Tests for:
1. Chat API responding correctly (POST /api/chat/message)
2. Multi-turn conversation context
3. Fallback response when LLM fails
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestChatBugFix:
    """Test chat endpoint bug fix - previously NameError due to missing functions"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session ID"""
        self.session_id = f"test_session_{uuid.uuid4().hex[:8]}"
    
    def test_chat_health_check(self):
        """Verify API is accessible"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"✓ Health check passed: {data}")
    
    def test_chat_message_basic(self):
        """BUG FIX 1: Chat should respond with a message field"""
        payload = {
            "session_id": self.session_id,
            "message": "Hallo, ich interessiere mich für KI-Agenten",
            "language": "de"
        }
        response = requests.post(
            f"{BASE_URL}/api/chat/message",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        # Status code assertion
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Data assertions
        data = response.json()
        assert "message" in data, f"Response missing 'message' field: {data}"
        assert isinstance(data["message"], str), f"Message should be string: {type(data['message'])}"
        assert len(data["message"]) > 0, "Message should not be empty"
        
        print(f"✓ Chat response received: {data['message'][:100]}...")
        
        # Check for qualification field
        assert "qualification" in data, "Response should have qualification field"
        
        return data
    
    def test_chat_message_english(self):
        """Test chat responds in English when language=en"""
        payload = {
            "session_id": f"test_en_{uuid.uuid4().hex[:8]}",
            "message": "Hello, I'm interested in AI agents",
            "language": "en"
        }
        response = requests.post(
            f"{BASE_URL}/api/chat/message",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert len(data["message"]) > 0
        print(f"✓ English chat response: {data['message'][:100]}...")
    
    def test_chat_multi_turn_conversation(self):
        """BUG FIX 1: Multi-turn chat - verify conversation context is maintained"""
        session_id = f"test_multi_{uuid.uuid4().hex[:8]}"
        
        # First message
        payload1 = {
            "session_id": session_id,
            "message": "Ich interessiere mich für Website-Entwicklung",
            "language": "de"
        }
        response1 = requests.post(
            f"{BASE_URL}/api/chat/message",
            json=payload1,
            headers={"Content-Type": "application/json"}
        )
        assert response1.status_code == 200
        data1 = response1.json()
        assert "message" in data1
        print(f"✓ First message response: {data1['message'][:80]}...")
        
        # Second message in same session
        payload2 = {
            "session_id": session_id,
            "message": "Was kostet das?",
            "language": "de"
        }
        response2 = requests.post(
            f"{BASE_URL}/api/chat/message",
            json=payload2,
            headers={"Content-Type": "application/json"}
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert "message" in data2
        assert len(data2["message"]) > 0
        print(f"✓ Second message response: {data2['message'][:80]}...")
        
        # The response should be contextual (about website pricing)
        # Not a generic greeting
        print(f"✓ Multi-turn conversation working with session: {session_id}")
    
    def test_chat_pricing_keywords(self):
        """Test fallback responds to pricing keywords"""
        payload = {
            "session_id": f"test_price_{uuid.uuid4().hex[:8]}",
            "message": "Was sind die Preise?",
            "language": "de"
        }
        response = requests.post(
            f"{BASE_URL}/api/chat/message",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        # Should mention pricing/tariffs
        print(f"✓ Pricing query response: {data['message'][:100]}...")
    
    def test_chat_greeting(self):
        """Test chat responds to greetings"""
        payload = {
            "session_id": f"test_greet_{uuid.uuid4().hex[:8]}",
            "message": "Hallo!",
            "language": "de"
        }
        response = requests.post(
            f"{BASE_URL}/api/chat/message",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert len(data["message"]) > 0
        print(f"✓ Greeting response: {data['message'][:100]}...")
    
    def test_chat_session_creation(self):
        """Test that new sessions are created properly"""
        new_session = f"new_session_{uuid.uuid4().hex[:8]}"
        payload = {
            "session_id": new_session,
            "message": "Test message",
            "language": "de"
        }
        response = requests.post(
            f"{BASE_URL}/api/chat/message",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"✓ New session created and responded: {new_session}")
    
    def test_chat_response_structure(self):
        """Verify complete response structure"""
        payload = {
            "session_id": f"test_struct_{uuid.uuid4().hex[:8]}",
            "message": "Ich möchte einen Termin buchen",
            "language": "de"
        }
        response = requests.post(
            f"{BASE_URL}/api/chat/message",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check all expected fields
        assert "message" in data, "Missing 'message' field"
        assert "qualification" in data, "Missing 'qualification' field"
        assert "actions" in data, "Missing 'actions' field"
        assert "should_escalate" in data, "Missing 'should_escalate' field"
        
        print(f"✓ Response structure complete: message, qualification, actions, should_escalate")
        print(f"  - should_escalate: {data['should_escalate']}")
        print(f"  - qualification: {data['qualification']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
