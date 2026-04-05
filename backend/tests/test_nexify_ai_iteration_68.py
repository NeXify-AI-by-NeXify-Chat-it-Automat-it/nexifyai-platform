"""
NeXify AI Iteration 68 - Testing Agent CRUD, Chat Scroll Containment, and Streaming Fixes
Tests:
1. Admin Login
2. Agent CRUD APIs (GET, POST, PUT, DELETE)
3. NeXify AI Tools API (37 tools)
4. Execute Tool API (execute_shell)
5. Master Agent protection (cannot delete)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAdminAuth:
    """Admin authentication tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get admin auth token"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data="username=p.courbois@icloud.com&password=1def!xO2022!!"
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        return data["access_token"]
    
    def test_admin_login(self, auth_token):
        """Test admin login returns valid token"""
        assert auth_token is not None
        assert len(auth_token) > 20


class TestAgentCRUD:
    """Agent CRUD API tests"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data="username=p.courbois@icloud.com&password=1def!xO2022!!"
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    def test_list_agents(self, auth_headers):
        """GET /api/admin/nexify-ai/agents returns agents list with master"""
        response = requests.get(f"{BASE_URL}/api/admin/nexify-ai/agents", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        agents = data["agents"]
        assert len(agents) >= 1, "Should have at least master agent"
        
        # Find master agent
        master = next((a for a in agents if a.get("agent_id") == "nexify-ai-master"), None)
        assert master is not None, "Master agent should exist"
        assert master.get("is_master") == True
        assert master.get("tools_count") == 37, f"Master should have 37 tools, got {master.get('tools_count')}"
        assert master.get("status") == "active"
        assert master.get("name") == "NeXify AI (Master)"
    
    def test_create_agent(self, auth_headers):
        """POST /api/admin/nexify-ai/agents creates new agent"""
        payload = {
            "name": "TEST_Agent_Iter68",
            "role": "test",
            "system_prompt": "Test agent for iteration 68",
            "model": "trinity-large-preview",
            "status": "active"
        }
        response = requests.post(
            f"{BASE_URL}/api/admin/nexify-ai/agents",
            headers=auth_headers,
            json=payload
        )
        assert response.status_code == 200, f"Create failed: {response.text}"
        data = response.json()
        assert "agent_id" in data
        assert data["name"] == "TEST_Agent_Iter68"
        assert data["role"] == "test"
        assert data["status"] == "active"
        
        # Store agent_id for cleanup
        TestAgentCRUD.created_agent_id = data["agent_id"]
        return data["agent_id"]
    
    def test_get_created_agent(self, auth_headers):
        """GET /api/admin/nexify-ai/agents/{id} returns agent details"""
        agent_id = getattr(TestAgentCRUD, 'created_agent_id', None)
        if not agent_id:
            pytest.skip("No agent created to get")
        
        response = requests.get(
            f"{BASE_URL}/api/admin/nexify-ai/agents/{agent_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["agent_id"] == agent_id
        assert data["name"] == "TEST_Agent_Iter68"
    
    def test_update_agent(self, auth_headers):
        """PUT /api/admin/nexify-ai/agents/{id} updates agent"""
        agent_id = getattr(TestAgentCRUD, 'created_agent_id', None)
        if not agent_id:
            pytest.skip("No agent created to update")
        
        payload = {"role": "updated_test", "status": "paused"}
        response = requests.put(
            f"{BASE_URL}/api/admin/nexify-ai/agents/{agent_id}",
            headers=auth_headers,
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("updated") == True
        
        # Verify update
        get_response = requests.get(
            f"{BASE_URL}/api/admin/nexify-ai/agents/{agent_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 200
        updated = get_response.json()
        assert updated["role"] == "updated_test"
        assert updated["status"] == "paused"
    
    def test_update_master_agent(self, auth_headers):
        """PUT /api/admin/nexify-ai/agents/nexify-ai-master updates master config"""
        payload = {"config": {"test_key": "test_value"}}
        response = requests.put(
            f"{BASE_URL}/api/admin/nexify-ai/agents/nexify-ai-master",
            headers=auth_headers,
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("updated") == True
    
    def test_delete_master_agent_forbidden(self, auth_headers):
        """DELETE /api/admin/nexify-ai/agents/nexify-ai-master returns 403"""
        response = requests.delete(
            f"{BASE_URL}/api/admin/nexify-ai/agents/nexify-ai-master",
            headers=auth_headers
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    
    def test_delete_agent(self, auth_headers):
        """DELETE /api/admin/nexify-ai/agents/{id} deletes agent"""
        agent_id = getattr(TestAgentCRUD, 'created_agent_id', None)
        if not agent_id:
            pytest.skip("No agent created to delete")
        
        response = requests.delete(
            f"{BASE_URL}/api/admin/nexify-ai/agents/{agent_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("deleted") == True
        
        # Verify deletion
        get_response = requests.get(
            f"{BASE_URL}/api/admin/nexify-ai/agents/{agent_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404


class TestNeXifyAITools:
    """NeXify AI Tools API tests"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data="username=p.courbois@icloud.com&password=1def!xO2022!!"
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    def test_list_tools(self, auth_headers):
        """GET /api/admin/nexify-ai/tools returns 37 tools"""
        response = requests.get(f"{BASE_URL}/api/admin/nexify-ai/tools", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
        tools = data["tools"]
        assert len(tools) == 37, f"Expected 37 tools, got {len(tools)}"
        
        # Check key tools exist
        expected_tools = ["execute_shell", "list_contacts", "system_stats", "search_brain", "db_query"]
        for tool in expected_tools:
            assert tool in tools, f"Tool {tool} should exist"
    
    def test_execute_shell_tool(self, auth_headers):
        """POST /api/admin/nexify-ai/execute-tool with execute_shell"""
        payload = {
            "tool": "execute_shell",
            "params": {"command": "echo hello"}
        }
        response = requests.post(
            f"{BASE_URL}/api/admin/nexify-ai/execute-tool",
            headers=auth_headers,
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        result = data["result"]
        assert result.get("stdout", "").strip() == "hello"
        assert result.get("exit_code") == 0
    
    def test_system_stats_tool(self, auth_headers):
        """POST /api/admin/nexify-ai/execute-tool with system_stats"""
        payload = {"tool": "system_stats", "params": {}}
        response = requests.post(
            f"{BASE_URL}/api/admin/nexify-ai/execute-tool",
            headers=auth_headers,
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        result = data["result"]
        assert "contacts" in result
        assert "leads" in result
        assert "conversations" in result


class TestNeXifyAIChat:
    """NeXify AI Chat streaming tests"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data="username=p.courbois@icloud.com&password=1def!xO2022!!"
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    def test_chat_endpoint_streaming(self, auth_headers):
        """POST /api/admin/nexify-ai/chat returns streaming response"""
        payload = {
            "message": "Hallo, kurze Antwort bitte",
            "use_memory": False
        }
        response = requests.post(
            f"{BASE_URL}/api/admin/nexify-ai/chat",
            headers=auth_headers,
            json=payload,
            stream=True,
            timeout=60
        )
        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("Content-Type", "")
        
        # Read first few chunks
        chunks_received = 0
        conversation_id = None
        for line in response.iter_lines(decode_unicode=True):
            if line and line.startswith("data: "):
                chunks_received += 1
                try:
                    import json
                    data = json.loads(line[6:])
                    if "conversation_id" in data:
                        conversation_id = data["conversation_id"]
                    if data.get("done"):
                        break
                except:
                    pass
                if chunks_received > 20:
                    break
        
        assert chunks_received > 0, "Should receive streaming chunks"
        assert conversation_id is not None, "Should receive conversation_id"


class TestCleanup:
    """Cleanup any test data"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data="username=p.courbois@icloud.com&password=1def!xO2022!!"
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    def test_cleanup_test_agents(self, auth_headers):
        """Clean up any TEST_ prefixed agents"""
        response = requests.get(f"{BASE_URL}/api/admin/nexify-ai/agents", headers=auth_headers)
        if response.status_code == 200:
            agents = response.json().get("agents", [])
            for agent in agents:
                if agent.get("name", "").startswith("TEST_"):
                    requests.delete(
                        f"{BASE_URL}/api/admin/nexify-ai/agents/{agent['agent_id']}",
                        headers=auth_headers
                    )
        assert True  # Cleanup always passes
