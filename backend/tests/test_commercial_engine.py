"""
NeXifyAI Commercial Engine v2.0 - Backend API Tests
Tests for: Tariffs, FAQ, Quotes, Invoices, PDF generation, Revolut webhook, Commercial stats
"""
import pytest
import requests
import os
import json

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://ai-architecture-lab.preview.emergentagent.com').rstrip('/')

# Test credentials from test_credentials.md
ADMIN_EMAIL = "p.courbois@icloud.com"
ADMIN_PASSWORD = "NxAi#Secure2026!"

# Expected pricing values (Single Source of Truth)
EXPECTED_PRICING = {
    "starter": {
        "reference_monthly_eur": 499.0,
        "contract_months": 24,
        "upfront_percent": 30,
        "total_contract_eur": 11976.0,
        "upfront_eur": 3592.80,
        "agents": 2
    },
    "growth": {
        "reference_monthly_eur": 1299.0,
        "contract_months": 24,
        "upfront_percent": 30,
        "total_contract_eur": 31176.0,
        "upfront_eur": 9352.80,
        "agents": 10
    }
}


class TestPublicProductEndpoints:
    """Test public product endpoints (no auth required)"""
    
    def test_get_tariffs_returns_both_plans(self):
        """GET /api/product/tariffs — returns both tariffs with correct pricing"""
        response = requests.get(f"{BASE_URL}/api/product/tariffs")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "tariffs" in data, "Response should contain 'tariffs' key"
        tariffs = data["tariffs"]
        
        # Verify exactly 2 tariffs (starter and growth)
        assert len(tariffs) == 2, f"Expected 2 tariffs, got {len(tariffs)}"
        assert "starter" in tariffs, "Missing 'starter' tariff"
        assert "growth" in tariffs, "Missing 'growth' tariff"
        print("✓ Both tariffs (starter, growth) present")
    
    def test_starter_tariff_pricing(self):
        """Verify Starter tariff has correct pricing values"""
        response = requests.get(f"{BASE_URL}/api/product/tariffs")
        assert response.status_code == 200
        
        starter = response.json()["tariffs"]["starter"]
        expected = EXPECTED_PRICING["starter"]
        
        # Verify monthly price
        assert starter["reference_monthly_eur"] == expected["reference_monthly_eur"], \
            f"Starter monthly: expected {expected['reference_monthly_eur']}, got {starter['reference_monthly_eur']}"
        
        # Verify contract months
        assert starter["contract_months"] == expected["contract_months"], \
            f"Starter months: expected {expected['contract_months']}, got {starter['contract_months']}"
        
        # Verify upfront percent
        assert starter["upfront_percent"] == expected["upfront_percent"], \
            f"Starter upfront %: expected {expected['upfront_percent']}, got {starter['upfront_percent']}"
        
        # Verify agents
        assert starter["agents"] == expected["agents"], \
            f"Starter agents: expected {expected['agents']}, got {starter['agents']}"
        
        # Verify calculation values
        calc = starter.get("calculation", {})
        assert calc.get("total_contract_eur") == expected["total_contract_eur"], \
            f"Starter total: expected {expected['total_contract_eur']}, got {calc.get('total_contract_eur')}"
        assert calc.get("upfront_eur") == expected["upfront_eur"], \
            f"Starter upfront: expected {expected['upfront_eur']}, got {calc.get('upfront_eur')}"
        
        print(f"✓ Starter pricing correct: {expected['reference_monthly_eur']} EUR/mo, {expected['total_contract_eur']} EUR total, {expected['upfront_eur']} EUR upfront")
    
    def test_growth_tariff_pricing(self):
        """Verify Growth tariff has correct pricing values"""
        response = requests.get(f"{BASE_URL}/api/product/tariffs")
        assert response.status_code == 200
        
        growth = response.json()["tariffs"]["growth"]
        expected = EXPECTED_PRICING["growth"]
        
        # Verify monthly price
        assert growth["reference_monthly_eur"] == expected["reference_monthly_eur"], \
            f"Growth monthly: expected {expected['reference_monthly_eur']}, got {growth['reference_monthly_eur']}"
        
        # Verify contract months
        assert growth["contract_months"] == expected["contract_months"], \
            f"Growth months: expected {expected['contract_months']}, got {growth['contract_months']}"
        
        # Verify upfront percent
        assert growth["upfront_percent"] == expected["upfront_percent"], \
            f"Growth upfront %: expected {expected['upfront_percent']}, got {growth['upfront_percent']}"
        
        # Verify agents
        assert growth["agents"] == expected["agents"], \
            f"Growth agents: expected {expected['agents']}, got {growth['agents']}"
        
        # Verify calculation values
        calc = growth.get("calculation", {})
        assert calc.get("total_contract_eur") == expected["total_contract_eur"], \
            f"Growth total: expected {expected['total_contract_eur']}, got {calc.get('total_contract_eur')}"
        assert calc.get("upfront_eur") == expected["upfront_eur"], \
            f"Growth upfront: expected {expected['upfront_eur']}, got {calc.get('upfront_eur')}"
        
        # Verify recommended flag
        assert growth.get("recommended") == True, "Growth should be marked as recommended"
        
        print(f"✓ Growth pricing correct: {expected['reference_monthly_eur']} EUR/mo, {expected['total_contract_eur']} EUR total, {expected['upfront_eur']} EUR upfront")
    
    def test_tariffs_include_company_info(self):
        """Verify tariffs response includes company info"""
        response = requests.get(f"{BASE_URL}/api/product/tariffs")
        assert response.status_code == 200
        
        data = response.json()
        assert "company" in data, "Response should contain 'company' key"
        company = data["company"]
        
        assert company.get("name") == "NeXify Automate", f"Company name mismatch: {company.get('name')}"
        assert company.get("brand") == "NeXifyAI", f"Brand mismatch: {company.get('brand')}"
        assert "phone" in company, "Missing phone"
        assert "email" in company, "Missing email"
        
        print(f"✓ Company info present: {company.get('brand')}")
    
    def test_get_faq_returns_15_entries(self):
        """GET /api/product/faq — returns 15 FAQ entries"""
        response = requests.get(f"{BASE_URL}/api/product/faq")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "faq" in data, "Response should contain 'faq' key"
        faq = data["faq"]
        
        assert len(faq) == 15, f"Expected 15 FAQ entries, got {len(faq)}"
        
        # Verify FAQ structure
        for i, item in enumerate(faq):
            assert "q" in item, f"FAQ item {i} missing 'q' (question)"
            assert "a" in item, f"FAQ item {i} missing 'a' (answer)"
        
        print(f"✓ FAQ returns {len(faq)} entries with correct structure")
    
    def test_faq_contains_tariff_info(self):
        """Verify FAQ contains tariff-related questions"""
        response = requests.get(f"{BASE_URL}/api/product/faq")
        assert response.status_code == 200
        
        faq = response.json()["faq"]
        questions = [item["q"] for item in faq]
        
        # Check for key tariff-related questions
        tariff_keywords = ["Tarif", "Starter", "Growth", "Anzahlung", "Laufzeit", "Bankdaten"]
        found_keywords = []
        for q in questions:
            for kw in tariff_keywords:
                if kw.lower() in q.lower():
                    found_keywords.append(kw)
        
        assert len(found_keywords) >= 3, f"FAQ should contain tariff-related questions. Found: {found_keywords}"
        print(f"✓ FAQ contains tariff-related content: {set(found_keywords)}")


class TestAdminAuthentication:
    """Test admin authentication"""
    
    def test_admin_login_success(self):
        """POST /api/admin/login — successful login returns token"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200, f"Login failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert "access_token" in data, "Response should contain 'access_token'"
        assert data.get("token_type") == "bearer", "Token type should be 'bearer'"
        
        print(f"✓ Admin login successful, token received")
        return data["access_token"]
    
    def test_admin_login_invalid_credentials(self):
        """POST /api/admin/login — invalid credentials return 401"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": "wrong@email.com", "password": "wrongpassword"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Invalid credentials correctly rejected with 401")


@pytest.fixture
def auth_token():
    """Get admin authentication token"""
    response = requests.post(
        f"{BASE_URL}/api/admin/login",
        data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Authentication failed - skipping authenticated tests")


class TestQuoteManagement:
    """Test quote CRUD operations (requires auth)"""
    
    def test_create_quote_starter(self, auth_token):
        """POST /api/admin/quotes — creates quote with correct calculation for starter tier"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        payload = {
            "tier": "starter",
            "customer_name": "TEST_Commercial_Starter",
            "customer_email": "test_starter@example.com",
            "customer_company": "Test Company GmbH",
            "use_case": "Testing commercial engine"
        }
        
        response = requests.post(f"{BASE_URL}/api/admin/quotes", json=payload, headers=headers)
        assert response.status_code == 200, f"Create quote failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert "quote" in data, "Response should contain 'quote'"
        quote = data["quote"]
        
        # Verify quote structure
        assert quote.get("tier") == "starter", f"Tier mismatch: {quote.get('tier')}"
        assert quote.get("status") == "draft", f"Status should be 'draft': {quote.get('status')}"
        assert "quote_id" in quote, "Missing quote_id"
        assert "quote_number" in quote, "Missing quote_number"
        
        # Verify calculation
        calc = quote.get("calculation", {})
        expected = EXPECTED_PRICING["starter"]
        assert calc.get("total_contract_eur") == expected["total_contract_eur"], \
            f"Total mismatch: expected {expected['total_contract_eur']}, got {calc.get('total_contract_eur')}"
        assert calc.get("upfront_eur") == expected["upfront_eur"], \
            f"Upfront mismatch: expected {expected['upfront_eur']}, got {calc.get('upfront_eur')}"
        
        # Verify PDF was generated
        assert data.get("pdf_available") == True, "PDF should be available"
        
        print(f"✓ Starter quote created: {quote.get('quote_number')} with correct pricing")
        return quote
    
    def test_create_quote_growth(self, auth_token):
        """POST /api/admin/quotes — creates quote with correct calculation for growth tier"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        payload = {
            "tier": "growth",
            "customer_name": "TEST_Commercial_Growth",
            "customer_email": "test_growth@example.com",
            "customer_company": "Enterprise Corp AG",
            "use_case": "Testing growth tier"
        }
        
        response = requests.post(f"{BASE_URL}/api/admin/quotes", json=payload, headers=headers)
        assert response.status_code == 200, f"Create quote failed: {response.status_code} - {response.text}"
        
        data = response.json()
        quote = data["quote"]
        
        # Verify calculation
        calc = quote.get("calculation", {})
        expected = EXPECTED_PRICING["growth"]
        assert calc.get("total_contract_eur") == expected["total_contract_eur"], \
            f"Total mismatch: expected {expected['total_contract_eur']}, got {calc.get('total_contract_eur')}"
        assert calc.get("upfront_eur") == expected["upfront_eur"], \
            f"Upfront mismatch: expected {expected['upfront_eur']}, got {calc.get('upfront_eur')}"
        
        print(f"✓ Growth quote created: {quote.get('quote_number')} with correct pricing")
        return quote
    
    def test_list_quotes(self, auth_token):
        """GET /api/admin/quotes — lists quotes"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.get(f"{BASE_URL}/api/admin/quotes", headers=headers)
        assert response.status_code == 200, f"List quotes failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert "quotes" in data, "Response should contain 'quotes'"
        quotes = data["quotes"]
        
        assert isinstance(quotes, list), "Quotes should be a list"
        print(f"✓ Listed {len(quotes)} quotes")
    
    def test_get_quote_detail(self, auth_token):
        """GET /api/admin/quotes/{id} — get quote details"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        # First create a quote
        payload = {
            "tier": "starter",
            "customer_name": "TEST_Detail_Quote",
            "customer_email": "test_detail@example.com",
            "customer_company": "Detail Test GmbH"
        }
        create_resp = requests.post(f"{BASE_URL}/api/admin/quotes", json=payload, headers=headers)
        assert create_resp.status_code == 200
        quote_id = create_resp.json()["quote"]["quote_id"]
        
        # Get quote detail
        response = requests.get(f"{BASE_URL}/api/admin/quotes/{quote_id}", headers=headers)
        assert response.status_code == 200, f"Get quote detail failed: {response.status_code} - {response.text}"
        
        quote = response.json()
        assert quote.get("quote_id") == quote_id, "Quote ID mismatch"
        assert "customer" in quote, "Missing customer info"
        assert "calculation" in quote, "Missing calculation"
        
        print(f"✓ Quote detail retrieved: {quote_id}")
    
    def test_send_quote(self, auth_token):
        """POST /api/admin/quotes/{id}/send — sends quote email"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        # First create a quote
        payload = {
            "tier": "starter",
            "customer_name": "TEST_Send_Quote",
            "customer_email": "test_send@example.com",
            "customer_company": "Send Test GmbH"
        }
        create_resp = requests.post(f"{BASE_URL}/api/admin/quotes", json=payload, headers=headers)
        assert create_resp.status_code == 200
        quote_id = create_resp.json()["quote"]["quote_id"]
        
        # Send quote
        response = requests.post(f"{BASE_URL}/api/admin/quotes/{quote_id}/send", headers=headers)
        assert response.status_code == 200, f"Send quote failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert data.get("sent") == True or "to" in data or "portal_link" in data, \
            f"Response should contain send confirmation: {data}"
        
        print(f"✓ Quote sent successfully: {quote_id}")


class TestPDFGeneration:
    """Test PDF document generation"""
    
    def test_download_quote_pdf(self, auth_token):
        """GET /api/documents/quote/{id}/pdf — downloads valid PDF"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        # First create a quote
        payload = {
            "tier": "starter",
            "customer_name": "TEST_PDF_Quote",
            "customer_email": "test_pdf@example.com",
            "customer_company": "PDF Test GmbH"
        }
        create_resp = requests.post(f"{BASE_URL}/api/admin/quotes", json=payload, headers=headers)
        assert create_resp.status_code == 200
        quote_id = create_resp.json()["quote"]["quote_id"]
        
        # Download PDF
        response = requests.get(f"{BASE_URL}/api/documents/quote/{quote_id}/pdf")
        assert response.status_code == 200, f"PDF download failed: {response.status_code} - {response.text}"
        
        # Verify it's a PDF
        content_type = response.headers.get("content-type", "")
        assert "application/pdf" in content_type, f"Expected PDF content type, got: {content_type}"
        
        # Verify PDF magic bytes
        content = response.content
        assert content[:4] == b'%PDF', "Content should start with PDF magic bytes"
        
        print(f"✓ PDF downloaded successfully: {len(content)} bytes")


class TestCommercialStats:
    """Test commercial dashboard stats"""
    
    def test_get_commercial_stats(self, auth_token):
        """GET /api/admin/commercial/stats — returns commercial dashboard stats"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.get(f"{BASE_URL}/api/admin/commercial/stats", headers=headers)
        assert response.status_code == 200, f"Get stats failed: {response.status_code} - {response.text}"
        
        data = response.json()
        
        # Verify structure
        assert "quotes" in data, "Missing 'quotes' stats"
        assert "invoices" in data, "Missing 'invoices' stats"
        assert "revenue" in data, "Missing 'revenue' stats"
        
        # Verify quotes stats
        quotes = data["quotes"]
        assert "total" in quotes, "Missing quotes total"
        assert "accepted" in quotes, "Missing quotes accepted"
        
        # Verify invoices stats
        invoices = data["invoices"]
        assert "total" in invoices, "Missing invoices total"
        assert "paid" in invoices, "Missing invoices paid"
        
        # Verify revenue stats
        revenue = data["revenue"]
        assert "total_gross" in revenue, "Missing total_gross"
        assert revenue.get("currency") == "EUR", "Currency should be EUR"
        
        print(f"✓ Commercial stats: {quotes['total']} quotes, {invoices['total']} invoices, {revenue['total_gross']} EUR revenue")


class TestInvoiceManagement:
    """Test invoice operations"""
    
    def test_list_invoices(self, auth_token):
        """GET /api/admin/invoices — lists invoices"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.get(f"{BASE_URL}/api/admin/invoices", headers=headers)
        assert response.status_code == 200, f"List invoices failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert "invoices" in data, "Response should contain 'invoices'"
        
        print(f"✓ Listed {len(data['invoices'])} invoices")
    
    def test_mark_invoice_paid_nonexistent(self, auth_token):
        """POST /api/admin/invoices/{id}/mark-paid — returns 404 for nonexistent invoice"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.post(f"{BASE_URL}/api/admin/invoices/nonexistent_id/mark-paid", headers=headers)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        
        print("✓ Mark-paid correctly returns 404 for nonexistent invoice")


class TestRevolutWebhook:
    """Test Revolut webhook endpoint"""
    
    def test_webhook_accepts_payload(self):
        """POST /api/webhooks/revolut — accepts webhook payload (idempotent)"""
        payload = {
            "event": "ORDER_COMPLETED",
            "order_id": "test_order_123",
            "timestamp": "2026-01-15T10:00:00Z"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/webhooks/revolut",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Webhook failed: {response.status_code} - {response.text}"
        
        data = response.json()
        assert data.get("status") in ["ok", "already_processed"], f"Unexpected status: {data.get('status')}"
        
        print(f"✓ Webhook accepted: status={data.get('status')}")
    
    def test_webhook_idempotent(self):
        """POST /api/webhooks/revolut — is idempotent (same event processed once)"""
        payload = {
            "event": "ORDER_COMPLETED",
            "order_id": "test_idempotent_order_456",
            "timestamp": "2026-01-15T10:00:00Z"
        }
        
        # First call
        response1 = requests.post(f"{BASE_URL}/api/webhooks/revolut", json=payload)
        assert response1.status_code == 200
        
        # Second call with same order_id and event
        response2 = requests.post(f"{BASE_URL}/api/webhooks/revolut", json=payload)
        assert response2.status_code == 200
        
        data2 = response2.json()
        assert data2.get("status") == "already_processed", "Second call should return 'already_processed'"
        
        print("✓ Webhook is idempotent")
    
    def test_webhook_rejects_invalid_json(self):
        """POST /api/webhooks/revolut — rejects invalid JSON"""
        response = requests.post(
            f"{BASE_URL}/api/webhooks/revolut",
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        
        print("✓ Webhook correctly rejects invalid JSON")


class TestUnauthorizedAccess:
    """Test that protected endpoints require authentication"""
    
    def test_quotes_requires_auth(self):
        """GET /api/admin/quotes — requires authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/quotes")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Quotes endpoint requires auth")
    
    def test_invoices_requires_auth(self):
        """GET /api/admin/invoices — requires authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/invoices")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Invoices endpoint requires auth")
    
    def test_commercial_stats_requires_auth(self):
        """GET /api/admin/commercial/stats — requires authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/commercial/stats")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Commercial stats endpoint requires auth")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
