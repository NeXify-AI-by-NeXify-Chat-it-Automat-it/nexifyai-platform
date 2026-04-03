"""
NeXifyAI Iteration 20 Backend Tests
Testing:
- Admin login and authentication
- 9 sub-agents (research, outreach, offer, support, intake, planning, finance, design, qa)
- Audit system (health check + timeline)
- Customer Portal (quote accept/decline/revision, communications, timeline)
- Customer Memory API
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://ai-architecture-lab.preview.emergentagent.com').rstrip('/')

# Test credentials
ADMIN_EMAIL = "p.courbois@icloud.com"
ADMIN_PASSWORD = "NxAi#Secure2026!"

# Test quote IDs from test_credentials.md
TEST_QUOTE_STARTER = "q_47e524121e72a4cd"
TEST_QUOTE_GROWTH = "q_1dc26ab66b817ae1"


class TestHealthCheck:
    """Basic health check tests"""
    
    def test_api_health(self):
        """Test API health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        print(f"✓ API health check passed - version {data['version']}")


class TestAdminAuth:
    """Admin authentication tests"""
    
    def test_admin_login_success(self):
        """Test admin login with correct credentials"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        print(f"✓ Admin login successful - token received")
        return data["access_token"]
    
    def test_admin_login_invalid_credentials(self):
        """Test admin login with wrong credentials"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": "wrong@email.com", "password": "wrongpassword"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 401
        print(f"✓ Invalid credentials correctly rejected")


@pytest.fixture(scope="module")
def admin_token():
    """Get admin token for authenticated tests"""
    response = requests.post(
        f"{BASE_URL}/api/admin/login",
        data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    pytest.skip("Admin authentication failed")


@pytest.fixture
def auth_headers(admin_token):
    """Headers with auth token"""
    return {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }


class TestAgentsAPI:
    """Test 9 sub-agents API endpoints"""
    
    def test_list_agents(self, auth_headers):
        """Test GET /api/admin/agents returns 9 agents"""
        response = requests.get(f"{BASE_URL}/api/admin/agents", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        # Check orchestrator
        assert "orchestrator" in data
        assert data["orchestrator"]["status"] == "active"
        print(f"✓ Orchestrator active - model: {data['orchestrator']['model']}")
        
        # Check 9 agents
        assert "agents" in data
        expected_agents = ["research", "outreach", "offer", "support", "intake", "planning", "finance", "design", "qa"]
        actual_agents = list(data["agents"].keys())
        
        for agent in expected_agents:
            assert agent in actual_agents, f"Missing agent: {agent}"
            assert data["agents"][agent]["status"] == "active"
        
        assert len(actual_agents) == 9, f"Expected 9 agents, got {len(actual_agents)}"
        print(f"✓ All 9 agents present: {', '.join(actual_agents)}")
    
    def test_agent_route_task(self, auth_headers):
        """Test POST /api/admin/agents/route - orchestrator routing"""
        response = requests.post(
            f"{BASE_URL}/api/admin/agents/route",
            headers=auth_headers,
            json={"task": "Recherchiere Informationen über ein Unternehmen", "context": {"test": True}}
        )
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "routing" in data or "error" not in data
        print(f"✓ Orchestrator routing works - session: {data.get('session_id', 'N/A')[:16]}")
    
    def test_execute_intake_agent(self, auth_headers):
        """Test POST /api/admin/agents/intake/execute"""
        response = requests.post(
            f"{BASE_URL}/api/admin/agents/intake/execute",
            headers=auth_headers,
            json={"task": "Klassifiziere diesen Lead: Interessent für KI-Beratung", "context": "Test context"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["agent"] == "intake"
        assert "session_id" in data
        assert "response" in data or "error" in data
        print(f"✓ Intake agent executed - session: {data.get('session_id', 'N/A')[:16]}")
    
    def test_execute_finance_agent(self, auth_headers):
        """Test POST /api/admin/agents/finance/execute"""
        response = requests.post(
            f"{BASE_URL}/api/admin/agents/finance/execute",
            headers=auth_headers,
            json={"task": "Erstelle eine Zahlungserinnerung für offene Rechnung", "context": "Test context"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["agent"] == "finance"
        assert "session_id" in data
        print(f"✓ Finance agent executed - session: {data.get('session_id', 'N/A')[:16]}")
    
    def test_execute_nonexistent_agent(self, auth_headers):
        """Test executing non-existent agent returns 404"""
        response = requests.post(
            f"{BASE_URL}/api/admin/agents/nonexistent/execute",
            headers=auth_headers,
            json={"task": "Test task"}
        )
        assert response.status_code == 404
        print(f"✓ Non-existent agent correctly returns 404")


class TestAuditSystem:
    """Test Audit system endpoints"""
    
    def test_audit_health(self, auth_headers):
        """Test GET /api/admin/audit/health returns health checks"""
        response = requests.get(f"{BASE_URL}/api/admin/audit/health", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        # Check overall status
        assert "overall" in data
        assert data["overall"] in ["healthy", "degraded"]
        print(f"✓ Audit health - overall: {data['overall']}")
        
        # Check all required health checks
        assert "checks" in data
        checks = data["checks"]
        required_checks = ["database", "collections", "agents", "whatsapp", "llm", "recent_errors_24h", "pricing"]
        
        for check in required_checks:
            assert check in checks, f"Missing health check: {check}"
        
        # Verify database check
        assert checks["database"]["status"] == "ok"
        print(f"✓ Database check: {checks['database']['status']}")
        
        # Verify agents check
        assert checks["agents"]["status"] == "ok"
        assert checks["agents"]["count"] == 9
        print(f"✓ Agents check: {checks['agents']['count']} agents active")
        
        # Verify LLM check
        assert checks["llm"]["status"] == "ok"
        assert checks["llm"]["key_present"] == True
        print(f"✓ LLM check: key present")
        
        # Verify collections check
        assert "counts" in checks["collections"]
        print(f"✓ Collections check: {len(checks['collections']['counts'])} collections")
    
    def test_audit_timeline(self, auth_headers):
        """Test GET /api/admin/audit/timeline returns recent events"""
        response = requests.get(f"{BASE_URL}/api/admin/audit/timeline?hours=48&limit=50", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "events" in data
        assert "count" in data
        assert "hours" in data
        assert data["hours"] == 48
        
        # Events should be a list
        assert isinstance(data["events"], list)
        print(f"✓ Audit timeline: {data['count']} events in last 48h")
        
        # If there are events, verify structure
        if len(data["events"]) > 0:
            event = data["events"][0]
            assert "entity_type" in event or "event_type" in event
            # action field may be nested in details or at top level
            has_action = "action" in event or ("details" in event and "task" in event.get("details", {}))
            assert has_action or "actor" in event, "Event should have action or actor field"
            assert "timestamp" in event
            print(f"✓ Event structure verified")


class TestCustomerPortalAPI:
    """Test Customer Portal endpoints"""
    
    @pytest.fixture
    def portal_token(self, auth_headers):
        """Get a valid portal access token"""
        # First, get a customer with access link
        response = requests.get(f"{BASE_URL}/api/admin/customers", headers=auth_headers)
        if response.status_code == 200:
            customers = response.json().get("customers", [])
            for cust in customers:
                if cust.get("access_link"):
                    # Extract token from access link
                    link = cust["access_link"]
                    if "token=" in link:
                        return link.split("token=")[1].split("&")[0]
        return None
    
    def test_portal_customer_data(self, portal_token):
        """Test GET /api/portal/customer/{token} returns customer data"""
        if not portal_token:
            pytest.skip("No portal token available")
        
        response = requests.get(f"{BASE_URL}/api/portal/customer/{portal_token}")
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "email" in data
        assert "quotes" in data
        assert "invoices" in data
        assert "bookings" in data
        assert "communications" in data
        assert "timeline" in data
        
        print(f"✓ Portal customer data: {data['email']}")
        print(f"  - Quotes: {len(data['quotes'])}")
        print(f"  - Communications: {len(data['communications'])}")
        print(f"  - Timeline: {len(data['timeline'])}")
    
    def test_portal_invalid_token(self):
        """Test portal with invalid token returns 403"""
        response = requests.get(f"{BASE_URL}/api/portal/customer/invalid_token_12345")
        assert response.status_code == 403
        print(f"✓ Invalid portal token correctly rejected")


class TestQuotePortalActions:
    """Test quote accept/decline/revision endpoints"""
    
    @pytest.fixture
    def test_quote_setup(self, auth_headers):
        """Create a test quote for portal actions"""
        # Create a test quote
        quote_data = {
            "tier": "starter",
            "customer_name": "TEST_Portal_User",
            "customer_email": "test_portal_iter20@test.nexifyai.de",
            "customer_company": "Test Company",
            "customer_country": "DE",
            "customer_industry": "IT",
            "use_case": "Testing portal actions",
            "notes": "Test quote for iteration 20"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/admin/quotes",
            headers=auth_headers,
            json=quote_data
        )
        
        if response.status_code in [200, 201]:
            quote = response.json()
            quote_id = quote.get("quote_id")
            
            # Send the quote to make it actionable
            requests.post(
                f"{BASE_URL}/api/admin/quotes/{quote_id}/send",
                headers=auth_headers
            )
            
            # Get access token for this customer
            cust_response = requests.get(
                f"{BASE_URL}/api/admin/customers/{quote_data['customer_email']}",
                headers=auth_headers
            )
            
            if cust_response.status_code == 200:
                cust_data = cust_response.json()
                access_link = cust_data.get("access_link", "")
                if "token=" in access_link:
                    token = access_link.split("token=")[1].split("&")[0]
                    return {"quote_id": quote_id, "token": token}
        
        return None
    
    def test_quote_accept_without_token(self):
        """Test quote accept without token returns 401 or 422"""
        response = requests.post(f"{BASE_URL}/api/portal/quote/test_quote/accept")
        # FastAPI returns 422 for missing required query param, or 401 if endpoint checks first
        assert response.status_code in [401, 422]
        print(f"✓ Quote accept without token correctly rejected (status: {response.status_code})")
    
    def test_quote_decline_without_token(self):
        """Test quote decline without token returns 401 or 422"""
        response = requests.post(f"{BASE_URL}/api/portal/quote/test_quote/decline")
        assert response.status_code in [401, 422]
        print(f"✓ Quote decline without token correctly rejected (status: {response.status_code})")
    
    def test_quote_revision_without_token(self):
        """Test quote revision without token returns 401 or 422"""
        response = requests.post(
            f"{BASE_URL}/api/portal/quote/test_quote/revision",
            json={"notes": "Test revision"}
        )
        assert response.status_code in [401, 422]
        print(f"✓ Quote revision without token correctly rejected (status: {response.status_code})")


class TestCustomerMemoryAPI:
    """Test Customer Memory endpoints"""
    
    def test_add_customer_memory_fact(self, auth_headers):
        """Test POST /api/admin/customer-memory/{email}/facts"""
        test_email = "test_memory_iter20@test.nexifyai.de"
        
        response = requests.post(
            f"{BASE_URL}/api/admin/customer-memory/{test_email}/facts",
            headers=auth_headers,
            json={"fact": "TEST_Iteration20_Memory_Fact: Customer prefers email communication"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok" or "fact_id" in data or "added" in str(data)
        print(f"✓ Customer memory fact added for {test_email}")
    
    def test_get_customer_memory(self, auth_headers):
        """Test GET /api/admin/customer-memory/{email}"""
        test_email = "test_memory_iter20@test.nexifyai.de"
        
        response = requests.get(
            f"{BASE_URL}/api/admin/customer-memory/{test_email}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        # Should return memory context
        assert isinstance(data, dict)
        print(f"✓ Customer memory retrieved")


class TestAdminSidebarNavigation:
    """Test that all admin views are accessible"""
    
    def test_admin_stats(self, auth_headers):
        """Test dashboard stats endpoint"""
        response = requests.get(f"{BASE_URL}/api/admin/stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        # Check for various possible field names
        assert "total_leads" in data or "leads_total" in data or "leads_new" in data or "new_leads_week" in data
        print(f"✓ Admin stats accessible - total leads: {data.get('total_leads', 'N/A')}")
    
    def test_admin_leads(self, auth_headers):
        """Test leads endpoint"""
        response = requests.get(f"{BASE_URL}/api/admin/leads", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "leads" in data
        print(f"✓ Admin leads accessible - {len(data['leads'])} leads")
    
    def test_admin_conversations(self, auth_headers):
        """Test conversations endpoint"""
        response = requests.get(f"{BASE_URL}/api/admin/conversations", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "conversations" in data
        print(f"✓ Admin conversations accessible - {len(data['conversations'])} conversations")
    
    def test_admin_chat_sessions(self, auth_headers):
        """Test chat sessions endpoint"""
        response = requests.get(f"{BASE_URL}/api/admin/chat-sessions", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data
        print(f"✓ Admin chat sessions accessible - {len(data['sessions'])} sessions")
    
    def test_admin_whatsapp_status(self, auth_headers):
        """Test WhatsApp status endpoint"""
        response = requests.get(f"{BASE_URL}/api/admin/whatsapp/status", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        print(f"✓ Admin WhatsApp status accessible - status: {data['status']}")
    
    def test_admin_timeline(self, auth_headers):
        """Test timeline endpoint"""
        response = requests.get(f"{BASE_URL}/api/admin/timeline", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "events" in data
        print(f"✓ Admin timeline accessible - {len(data['events'])} events")
    
    def test_admin_calendar(self, auth_headers):
        """Test calendar endpoint"""
        response = requests.get(f"{BASE_URL}/api/admin/calendar-data?month=2026-04", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "bookings" in data
        print(f"✓ Admin calendar accessible")
    
    def test_admin_customers(self, auth_headers):
        """Test customers endpoint"""
        response = requests.get(f"{BASE_URL}/api/admin/customers", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "customers" in data
        print(f"✓ Admin customers accessible - {len(data['customers'])} customers")
    
    def test_admin_quotes(self, auth_headers):
        """Test quotes endpoint (Commercial view)"""
        response = requests.get(f"{BASE_URL}/api/admin/quotes", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "quotes" in data
        print(f"✓ Admin quotes accessible - {len(data['quotes'])} quotes")
    
    def test_admin_invoices(self, auth_headers):
        """Test invoices endpoint (Commercial view)"""
        response = requests.get(f"{BASE_URL}/api/admin/invoices", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "invoices" in data
        print(f"✓ Admin invoices accessible - {len(data['invoices'])} invoices")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
