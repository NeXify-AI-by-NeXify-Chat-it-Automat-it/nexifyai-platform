"""
Iteration 47 - Quote API and Pricing Tests
Tests for:
- QUOTE API 1: POST /api/quote/request returns quote_request_id and lead_id
- QUOTE API 2: Creates lead in MongoDB (verify via /api/admin/leads)
- QUOTE API 3: Creates timeline event (verify via /api/admin/stats)
- QUOTE API 4: Duplicate email updates existing lead instead of creating new one
- REGRESSION: Admin login, Chat, Legal pages
"""
import pytest
import requests
import os
import secrets
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestQuoteAPI:
    """Quote Request API Tests - Triple-connected verification"""
    
    @pytest.fixture(scope="class")
    def unique_email(self):
        """Generate unique email for testing"""
        return f"test_quote_{secrets.token_hex(4)}@testfirma.de"
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": "p.courbois@icloud.com", "password": "NxAi#Secure2026!"}
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Admin authentication failed")
    
    def test_quote_request_returns_ids(self, unique_email):
        """QUOTE API 1: POST /api/quote/request returns quote_request_id and lead_id"""
        payload = {
            "vorname": "Test",
            "nachname": "QuoteUser",
            "email": unique_email,
            "interesse": "Ich benötige eine individuelle Lösung für KI-Automation",
            "tarif": "growth",
            "budget": "5000-10000",
            "source": "website",
            "language": "de"
        }
        response = requests.post(f"{BASE_URL}/api/quote/request", json=payload)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify quote_request_id is returned
        assert "quote_request_id" in data, "Response missing quote_request_id"
        assert data["quote_request_id"].startswith("QR-"), f"Invalid quote_request_id format: {data['quote_request_id']}"
        
        # Verify lead_id is returned
        assert "lead_id" in data, "Response missing lead_id"
        assert data["lead_id"].startswith("LEAD-"), f"Invalid lead_id format: {data['lead_id']}"
        
        # Verify status
        assert data.get("status") == "eingegangen", f"Expected status 'eingegangen', got {data.get('status')}"
        
        print(f"PASSED: Quote request created - quote_request_id: {data['quote_request_id']}, lead_id: {data['lead_id']}")
        return data
    
    def test_quote_creates_lead_in_mongodb(self, unique_email, admin_token):
        """QUOTE API 2: POST /api/quote/request creates lead in MongoDB"""
        # First create a quote request
        payload = {
            "vorname": "LeadTest",
            "nachname": "QuoteUser",
            "email": unique_email,
            "interesse": "Testing lead creation via quote request",
            "tarif": "starter",
            "source": "website"
        }
        quote_response = requests.post(f"{BASE_URL}/api/quote/request", json=payload)
        assert quote_response.status_code == 200
        quote_data = quote_response.json()
        lead_id = quote_data.get("lead_id")
        
        # Verify lead exists via admin API
        headers = {"Authorization": f"Bearer {admin_token}"}
        leads_response = requests.get(f"{BASE_URL}/api/admin/leads", headers=headers)
        
        assert leads_response.status_code == 200, f"Failed to get leads: {leads_response.text}"
        leads_data = leads_response.json()
        
        # Find the created lead
        leads = leads_data.get("leads", [])
        found_lead = None
        for lead in leads:
            if lead.get("email") == unique_email.lower():
                found_lead = lead
                break
        
        assert found_lead is not None, f"Lead with email {unique_email} not found in MongoDB"
        assert found_lead.get("interesse") == payload["interesse"], "Lead interesse not saved correctly"
        assert "angebot_angefragt" in found_lead.get("tags", []), "Lead missing 'angebot_angefragt' tag"
        
        print(f"PASSED: Lead created in MongoDB - lead_id: {lead_id}, email: {unique_email}")
    
    def test_quote_creates_timeline_event(self, admin_token):
        """QUOTE API 3: POST /api/quote/request creates timeline event"""
        # Create a new quote request
        test_email = f"timeline_test_{secrets.token_hex(4)}@testfirma.de"
        payload = {
            "vorname": "Timeline",
            "nachname": "TestUser",
            "email": test_email,
            "interesse": "Testing timeline event creation",
            "tarif": "growth",
            "source": "website"
        }
        quote_response = requests.post(f"{BASE_URL}/api/quote/request", json=payload)
        assert quote_response.status_code == 200
        quote_data = quote_response.json()
        quote_request_id = quote_data.get("quote_request_id")
        
        # Verify timeline event via admin stats
        headers = {"Authorization": f"Bearer {admin_token}"}
        stats_response = requests.get(f"{BASE_URL}/api/admin/stats", headers=headers)
        
        assert stats_response.status_code == 200, f"Failed to get stats: {stats_response.text}"
        stats_data = stats_response.json()
        
        # Check timeline events exist
        timeline = stats_data.get("timeline", [])
        assert len(timeline) > 0, "No timeline events found"
        
        # Look for quote_request event type
        quote_events = [e for e in timeline if e.get("type") == "quote_request"]
        assert len(quote_events) > 0, "No quote_request timeline events found"
        
        print(f"PASSED: Timeline event created for quote_request_id: {quote_request_id}")
    
    def test_duplicate_email_updates_existing_lead(self, admin_token):
        """QUOTE API 4: Duplicate email updates existing lead instead of creating new one"""
        test_email = f"duplicate_test_{secrets.token_hex(4)}@testfirma.de"
        
        # First request
        payload1 = {
            "vorname": "First",
            "nachname": "Request",
            "email": test_email,
            "interesse": "First interest - KI Chatbot",
            "tarif": "starter",
            "source": "website"
        }
        response1 = requests.post(f"{BASE_URL}/api/quote/request", json=payload1)
        assert response1.status_code == 200
        data1 = response1.json()
        lead_id_1 = data1.get("lead_id")
        
        # Second request with same email but different data
        payload2 = {
            "vorname": "Second",
            "nachname": "Request",
            "email": test_email,
            "interesse": "Updated interest - Full Automation Suite",
            "tarif": "growth",
            "budget": "10000+",
            "source": "website"
        }
        response2 = requests.post(f"{BASE_URL}/api/quote/request", json=payload2)
        assert response2.status_code == 200
        data2 = response2.json()
        lead_id_2 = data2.get("lead_id")
        
        # Verify same lead_id is returned (lead was updated, not created new)
        assert lead_id_1 == lead_id_2, f"Expected same lead_id, got {lead_id_1} vs {lead_id_2}"
        
        # Verify lead was updated with new data
        headers = {"Authorization": f"Bearer {admin_token}"}
        leads_response = requests.get(f"{BASE_URL}/api/admin/leads", headers=headers)
        leads_data = leads_response.json()
        
        found_lead = None
        for lead in leads_data.get("leads", []):
            if lead.get("email") == test_email.lower():
                found_lead = lead
                break
        
        assert found_lead is not None, "Lead not found"
        assert found_lead.get("interesse") == payload2["interesse"], "Lead interesse not updated"
        assert found_lead.get("tarif") == payload2["tarif"], "Lead tarif not updated"
        
        print(f"PASSED: Duplicate email updated existing lead - lead_id: {lead_id_1}")


class TestRegressionAdmin:
    """Regression tests for admin functionality"""
    
    def test_admin_login(self):
        """REGRESSION: Admin login works"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": "p.courbois@icloud.com", "password": "NxAi#Secure2026!"}
        )
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access_token in response"
        print("PASSED: Admin login works")
    
    def test_admin_stats_lead_counts(self):
        """REGRESSION: Admin stats show updated lead counts"""
        # Login first
        login_response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": "p.courbois@icloud.com", "password": "NxAi#Secure2026!"}
        )
        token = login_response.json().get("access_token")
        
        headers = {"Authorization": f"Bearer {token}"}
        stats_response = requests.get(f"{BASE_URL}/api/admin/stats", headers=headers)
        
        assert stats_response.status_code == 200
        stats = stats_response.json()
        
        assert "total_leads" in stats, "Missing total_leads in stats"
        assert stats["total_leads"] > 0, "Expected at least 1 lead"
        
        print(f"PASSED: Admin stats - total_leads: {stats['total_leads']}")


class TestRegressionChat:
    """Regression tests for chat functionality"""
    
    def test_chat_responds_to_messages(self):
        """REGRESSION: Chat still responds to messages"""
        session_id = f"test_session_{secrets.token_hex(8)}"
        payload = {
            "session_id": session_id,
            "message": "Hallo, ich interessiere mich für KI-Automation",
            "language": "de"
        }
        response = requests.post(f"{BASE_URL}/api/chat/message", json=payload)
        
        assert response.status_code == 200, f"Chat failed: {response.text}"
        data = response.json()
        
        assert "message" in data, "No message in chat response"
        assert len(data["message"]) > 10, "Chat response too short"
        
        print(f"PASSED: Chat responds - response length: {len(data['message'])} chars")


class TestRegressionLegalPages:
    """Regression tests for legal pages"""
    
    @pytest.mark.parametrize("path", ["/impressum", "/datenschutz", "/agb", "/ki-hinweise"])
    def test_legal_page_accessible(self, path):
        """REGRESSION: Legal pages accessible"""
        response = requests.get(f"{BASE_URL}{path}", allow_redirects=True)
        # Frontend routes return 200 (SPA routing)
        assert response.status_code == 200, f"Legal page {path} not accessible: {response.status_code}"
        print(f"PASSED: Legal page {path} accessible")


class TestPricingEndpoints:
    """Tests for pricing-related endpoints"""
    
    def test_tariffs_endpoint(self):
        """Verify tariffs endpoint returns pricing data"""
        response = requests.get(f"{BASE_URL}/api/product/tariffs")
        assert response.status_code == 200
        data = response.json()
        
        assert "tariffs" in data, "Missing tariffs in response"
        tariffs = data["tariffs"]
        assert len(tariffs) >= 2, "Expected at least 2 tariffs"
        
        # Verify tariff structure
        for key, tariff in tariffs.items():
            assert "name" in tariff, f"Tariff {key} missing name"
            assert "calculation" in tariff, f"Tariff {key} missing calculation"
        
        print(f"PASSED: Tariffs endpoint - {len(tariffs)} tariffs returned")
    
    def test_services_endpoint(self):
        """Verify services endpoint returns service catalog"""
        response = requests.get(f"{BASE_URL}/api/product/services")
        assert response.status_code == 200
        data = response.json()
        
        assert "services" in data, "Missing services in response"
        assert "bundles" in data, "Missing bundles in response"
        
        print(f"PASSED: Services endpoint - {len(data['services'])} services, {len(data['bundles'])} bundles")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
