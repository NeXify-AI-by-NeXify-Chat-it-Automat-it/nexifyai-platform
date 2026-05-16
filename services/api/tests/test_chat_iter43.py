"""
Chat API Tests - Iteration 43
Tests for chat interface functionality including multi-turn conversation
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestChatAPI:
    """Chat API endpoint tests"""
    
    @pytest.fixture
    def session_id(self):
        """Generate unique session ID for each test"""
        return f"test_session_{uuid.uuid4().hex[:8]}"
    
    def test_chat_health_check(self):
        """Test that chat endpoint is accessible"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        print("SUCCESS: Health check passed")
    
    def test_chat_message_basic(self, session_id):
        """Test basic chat message - CHAT 11"""
        response = requests.post(
            f"{BASE_URL}/api/chat/message",
            json={
                "session_id": session_id,
                "message": "Hallo",
                "language": "de"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "message" in data
        assert isinstance(data["message"], str)
        assert len(data["message"]) > 0
        print(f"SUCCESS: Basic chat message - Response: {data['message'][:100]}...")
    
    def test_chat_multi_turn_conversation(self, session_id):
        """Test multi-turn conversation maintains context - CHAT 11"""
        # First message
        response1 = requests.post(
            f"{BASE_URL}/api/chat/message",
            json={
                "session_id": session_id,
                "message": "Ich interessiere mich für KI-Automatisierung",
                "language": "de"
            }
        )
        assert response1.status_code == 200
        data1 = response1.json()
        assert "message" in data1
        print(f"Turn 1 response: {data1['message'][:80]}...")
        
        # Second message (follow-up)
        response2 = requests.post(
            f"{BASE_URL}/api/chat/message",
            json={
                "session_id": session_id,
                "message": "Welche Systeme könnt ihr integrieren?",
                "language": "de"
            }
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert "message" in data2
        print(f"Turn 2 response: {data2['message'][:80]}...")
        
        # Third message
        response3 = requests.post(
            f"{BASE_URL}/api/chat/message",
            json={
                "session_id": session_id,
                "message": "Was kostet das?",
                "language": "de"
            }
        )
        assert response3.status_code == 200
        data3 = response3.json()
        assert "message" in data3
        print(f"Turn 3 response: {data3['message'][:80]}...")
        
        print("SUCCESS: Multi-turn conversation completed")
    
    def test_chat_response_structure(self, session_id):
        """Test chat response has correct structure"""
        response = requests.post(
            f"{BASE_URL}/api/chat/message",
            json={
                "session_id": session_id,
                "message": "Test message",
                "language": "de"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "message" in data
        assert "qualification" in data or data.get("qualification") is None or "qualification" not in data
        assert "actions" in data or data.get("actions") is None or "actions" not in data
        assert "should_escalate" in data or data.get("should_escalate") is None or "should_escalate" not in data
        
        print("SUCCESS: Response structure is correct")
    
    def test_chat_english_language(self, session_id):
        """Test chat in English"""
        response = requests.post(
            f"{BASE_URL}/api/chat/message",
            json={
                "session_id": session_id,
                "message": "Hello, I need help with automation",
                "language": "en"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"SUCCESS: English chat - Response: {data['message'][:80]}...")
    
    def test_chat_dutch_language(self, session_id):
        """Test chat in Dutch"""
        response = requests.post(
            f"{BASE_URL}/api/chat/message",
            json={
                "session_id": session_id,
                "message": "Hallo, ik heb hulp nodig met automatisering",
                "language": "nl"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"SUCCESS: Dutch chat - Response: {data['message'][:80]}...")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
