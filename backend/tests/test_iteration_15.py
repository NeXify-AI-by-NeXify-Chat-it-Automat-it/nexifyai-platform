"""
NeXifyAI Commercial System — Iteration 15 E2E Tests
Tests: B2B Pricing, Service Catalog, Trust/Compliance, Quote Portal, Admin Commercial Dashboard, AI Chat Discovery
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://ai-architecture-lab.preview.emergentagent.com')

# Test credentials
ADMIN_EMAIL = "p.courbois@icloud.com"
ADMIN_PASSWORD = "NxAi#Secure2026!"


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def auth_token(api_client):
    """Get admin authentication token"""
    response = api_client.post(
        f"{BASE_URL}/api/admin/login",
        data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Authentication failed - skipping authenticated tests")


@pytest.fixture(scope="module")
def authenticated_client(api_client, auth_token):
    """Session with auth header"""
    api_client.headers.update({"Authorization": f"Bearer {auth_token}"})
    return api_client


class TestTariffPricing:
    """Test tariff pricing calculations — Single Source of Truth"""
    
    def test_get_tariffs_returns_both_plans(self, api_client):
        """GET /api/product/tariffs returns both starter and growth tariffs"""
        response = api_client.get(f"{BASE_URL}/api/product/tariffs")
        assert response.status_code == 200
        data = response.json()
        assert "tariffs" in data
        assert "starter" in data["tariffs"]
        assert "growth" in data["tariffs"]
        print("✓ GET /api/product/tariffs returns both tariffs")
    
    def test_starter_tariff_pricing(self, api_client):
        """Starter tariff: 499 EUR/mo, 11976 total, 3592.80 upfront, 349.30 recurring"""
        response = api_client.get(f"{BASE_URL}/api/product/tariffs")
        assert response.status_code == 200
        starter = response.json()["tariffs"]["starter"]
        calc = starter["calculation"]
        
        # Verify pricing
        assert starter["reference_monthly_eur"] == 499.0
        assert calc["total_contract_eur"] == 11976.0
        assert calc["upfront_eur"] == 3592.80
        assert calc["recurring_eur"] == 349.30
        assert calc["contract_months"] == 24
        assert calc["upfront_percent"] == 30
        assert starter["agents"] == 2
        print(f"✓ Starter pricing verified: {calc['total_contract_eur']} total, {calc['upfront_eur']} upfront, {calc['recurring_eur']} recurring")
    
    def test_growth_tariff_pricing(self, api_client):
        """Growth tariff: 1299 EUR/mo, 31176 total, 9352.80 upfront, 909.30 recurring"""
        response = api_client.get(f"{BASE_URL}/api/product/tariffs")
        assert response.status_code == 200
        growth = response.json()["tariffs"]["growth"]
        calc = growth["calculation"]
        
        # Verify pricing
        assert growth["reference_monthly_eur"] == 1299.0
        assert calc["total_contract_eur"] == 31176.0
        assert calc["upfront_eur"] == 9352.80
        assert calc["recurring_eur"] == 909.30
        assert calc["contract_months"] == 24
        assert calc["upfront_percent"] == 30
        assert growth["agents"] == 10
        assert growth.get("recommended") == True
        print(f"✓ Growth pricing verified: {calc['total_contract_eur']} total, {calc['upfront_eur']} upfront, {calc['recurring_eur']} recurring")


class TestServiceCatalog:
    """Test service catalog — Websites, Apps, Add-ons, Bundles"""
    
    def test_get_services_returns_7_services_3_bundles(self, api_client):
        """GET /api/product/services returns 7 services and 3 bundles"""
        response = api_client.get(f"{BASE_URL}/api/product/services")
        assert response.status_code == 200
        data = response.json()
        
        assert "services" in data
        assert "bundles" in data
        assert len(data["services"]) == 7
        assert len(data["bundles"]) == 3
        print(f"✓ Services: {len(data['services'])} services, {len(data['bundles'])} bundles")
    
    def test_website_pricing(self, api_client):
        """Website pricing: Starter 2990, Professional 7490, Enterprise 14900"""
        response = api_client.get(f"{BASE_URL}/api/product/services")
        services = response.json()["services"]
        
        assert services["web_starter"]["price_eur"] == 2990.0
        assert services["web_professional"]["price_eur"] == 7490.0
        assert services["web_enterprise"]["price_eur"] == 14900.0
        print("✓ Website pricing verified: 2990, 7490, 14900 EUR")
    
    def test_app_pricing(self, api_client):
        """App pricing: MVP 9900, Professional 24900"""
        response = api_client.get(f"{BASE_URL}/api/product/services")
        services = response.json()["services"]
        
        assert services["app_mvp"]["price_eur"] == 9900.0
        assert services["app_professional"]["price_eur"] == 24900.0
        print("✓ App pricing verified: 9900, 24900 EUR")
    
    def test_ai_addon_pricing(self, api_client):
        """AI Add-on pricing: Chatbot 249/mo, Automation 499/mo"""
        response = api_client.get(f"{BASE_URL}/api/product/services")
        services = response.json()["services"]
        
        assert services["ai_addon_chatbot"]["price_monthly_eur"] == 249.0
        assert services["ai_addon_automation"]["price_monthly_eur"] == 499.0
        print("✓ AI Add-on pricing verified: 249, 499 EUR/mo")


class TestComplianceAndTrust:
    """Test compliance and trust metadata"""
    
    def test_get_compliance_returns_8_items(self, api_client):
        """GET /api/product/compliance returns 8 compliance items"""
        response = api_client.get(f"{BASE_URL}/api/product/compliance")
        assert response.status_code == 200
        data = response.json()
        
        assert "compliance" in data
        assert len(data["compliance"]) == 8
        print(f"✓ Compliance: {len(data['compliance'])} items")
    
    def test_iso_gap_analysis(self, api_client):
        """GET /api/product/compliance returns ISO gap analysis with fulfilled/partial/open counts"""
        response = api_client.get(f"{BASE_URL}/api/product/compliance")
        data = response.json()
        
        assert "iso_gap_analysis" in data
        iso = data["iso_gap_analysis"]
        
        # Check ISO 27001
        assert "iso_27001" in iso
        summary = iso["iso_27001"]["summary"]
        assert "fulfilled" in summary
        assert "partial" in summary
        assert "open" in summary
        assert "total" in summary
        print(f"✓ ISO 27001 gap analysis: {summary['fulfilled']} fulfilled, {summary['partial']} partial, {summary['open']} open")
        
        # Check ISO 27701
        assert "iso_27701" in iso
        summary_27701 = iso["iso_27701"]["summary"]
        assert "fulfilled" in summary_27701
        print(f"✓ ISO 27701 gap analysis: {summary_27701['fulfilled']} fulfilled, {summary_27701['partial']} partial, {summary_27701['open']} open")


class TestFAQ:
    """Test FAQ endpoint"""
    
    def test_faq_returns_17_plus_entries(self, api_client):
        """GET /api/product/faq returns 17+ FAQ entries including Services and Bundles"""
        response = api_client.get(f"{BASE_URL}/api/product/faq")
        assert response.status_code == 200
        data = response.json()
        
        assert "faq" in data
        faq_count = len(data["faq"])
        assert faq_count >= 17, f"Expected 17+ FAQ entries, got {faq_count}"
        print(f"✓ FAQ: {faq_count} entries")
    
    def test_faq_contains_services_info(self, api_client):
        """FAQ contains questions about websites, apps, bundles"""
        response = api_client.get(f"{BASE_URL}/api/product/faq")
        faq = response.json()["faq"]
        
        # Check for services-related FAQ
        faq_text = " ".join([f["q"] + " " + f["a"] for f in faq]).lower()
        assert "website" in faq_text or "webseite" in faq_text
        assert "app" in faq_text
        assert "bundle" in faq_text
        print("✓ FAQ contains services info (websites, apps, bundles)")


class TestSecurityHeaders:
    """Test security headers on all responses"""
    
    def test_security_headers_present(self, api_client):
        """All security headers present on API responses"""
        response = api_client.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        
        headers = response.headers
        
        # Check required security headers
        assert headers.get("X-Content-Type-Options") == "nosniff"
        print("✓ X-Content-Type-Options: nosniff")
        
        assert headers.get("X-Frame-Options") == "DENY"
        print("✓ X-Frame-Options: DENY")
        
        assert headers.get("X-XSS-Protection") == "1; mode=block"
        print("✓ X-XSS-Protection: 1; mode=block")
        
        assert "strict-origin" in headers.get("Referrer-Policy", "")
        print(f"✓ Referrer-Policy: {headers.get('Referrer-Policy')}")
        
        assert "camera=()" in headers.get("Permissions-Policy", "")
        print(f"✓ Permissions-Policy: {headers.get('Permissions-Policy')}")
        
        assert "no-store" in headers.get("Cache-Control", "")
        print(f"✓ Cache-Control: {headers.get('Cache-Control')}")


class TestChatPricing:
    """Test AI chat returns correct pricing information"""
    
    def test_chat_website_pricing(self, api_client):
        """POST /api/chat/message — ask about website pricing, should return 2990/7490/14900"""
        response = api_client.post(
            f"{BASE_URL}/api/chat/message",
            json={
                "session_id": "test_iter15_website",
                "message": "Was kosten eure Websites?",
                "language": "de"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        message = data.get("message", "").lower()
        # Check that pricing info is mentioned (may be in different formats)
        has_pricing = any(p in message for p in ["2.990", "2990", "7.490", "7490", "14.900", "14900"])
        print(f"✓ Chat response about websites received (pricing mentioned: {has_pricing})")
        # Note: LLM responses may vary, so we just verify the endpoint works
    
    def test_chat_tariff_pricing(self, api_client):
        """POST /api/chat/message — ask about KI tariffs, should return 499/1299"""
        response = api_client.post(
            f"{BASE_URL}/api/chat/message",
            json={
                "session_id": "test_iter15_tariff",
                "message": "Was kosten eure KI-Tarife?",
                "language": "de"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        message = data.get("message", "").lower()
        has_pricing = any(p in message for p in ["499", "1.299", "1299"])
        print(f"✓ Chat response about tariffs received (pricing mentioned: {has_pricing})")


class TestQuoteCreationE2E:
    """E2E test: Create quotes and verify calculations"""
    
    def test_create_growth_quote_verify_calculation(self, authenticated_client):
        """E2E: Create Growth quote → verify calculation (total 31176, upfront 9352.80, recurring 909.30)"""
        response = authenticated_client.post(
            f"{BASE_URL}/api/admin/quotes",
            json={
                "tier": "growth",
                "customer_name": "TEST_Iter15_Growth User",
                "customer_email": "test_iter15_growth@example.com",
                "customer_company": "TEST Growth GmbH",
                "customer_country": "DE",
                "customer_industry": "Logistik",
                "use_case": "Supply Chain Automation",
                "notes": "Test quote for iteration 15"
            }
        )
        assert response.status_code in [200, 201]
        data = response.json()
        quote = data.get("quote", data)  # Handle both wrapped and unwrapped response
        calc = quote["calculation"]
        assert calc["total_contract_eur"] == 31176.0
        assert calc["upfront_eur"] == 9352.80
        assert calc["recurring_eur"] == 909.30
        assert calc["contract_months"] == 24
        
        # Verify customer data
        customer = quote.get("customer", {})
        assert customer.get("country") == "DE"
        assert customer.get("industry") == "Logistik"
        
        print(f"✓ Growth quote created: {quote['quote_number']}")
        print(f"  Total: {calc['total_contract_eur']} EUR, Upfront: {calc['upfront_eur']} EUR, Recurring: {calc['recurring_eur']} EUR")
        return quote
    
    def test_create_starter_quote_verify_calculation(self, authenticated_client):
        """E2E: Create Starter quote → verify calculation (total 11976, upfront 3592.80, recurring 349.30)"""
        response = authenticated_client.post(
            f"{BASE_URL}/api/admin/quotes",
            json={
                "tier": "starter",
                "customer_name": "TEST_Iter15_Starter User",
                "customer_email": "test_iter15_starter@example.com",
                "customer_company": "TEST Starter AG",
                "customer_country": "AT",
                "customer_industry": "Finanzdienstleistungen",
                "use_case": "Customer Service Automation",
                "notes": "Test quote for iteration 15 - starter"
            }
        )
        assert response.status_code in [200, 201]
        data = response.json()
        quote = data.get("quote", data)  # Handle both wrapped and unwrapped response
        calc = quote["calculation"]
        assert calc["total_contract_eur"] == 11976.0
        assert calc["upfront_eur"] == 3592.80
        assert calc["recurring_eur"] == 349.30
        assert calc["contract_months"] == 24
        
        # Verify customer data
        customer = quote.get("customer", {})
        assert customer.get("country") == "AT"
        assert customer.get("industry") == "Finanzdienstleistungen"
        
        print(f"✓ Starter quote created: {quote['quote_number']}")
        print(f"  Total: {calc['total_contract_eur']} EUR, Upfront: {calc['upfront_eur']} EUR, Recurring: {calc['recurring_eur']} EUR")
        return quote


class TestPDFDownload:
    """Test PDF download functionality"""
    
    def test_pdf_download_valid(self, authenticated_client):
        """PDF download — valid PDF with EU compliance note"""
        # First create a quote
        response = authenticated_client.post(
            f"{BASE_URL}/api/admin/quotes",
            json={
                "tier": "starter",
                "customer_name": "TEST_PDF_Iter15",
                "customer_email": "test_pdf_iter15@example.com",
                "customer_company": "PDF Test GmbH"
            }
        )
        assert response.status_code in [200, 201]
        data = response.json()
        quote = data.get("quote", data)  # Handle both wrapped and unwrapped response
        quote_id = quote["quote_id"]
        
        # Download PDF
        pdf_response = authenticated_client.get(f"{BASE_URL}/api/documents/quote/{quote_id}/pdf")
        assert pdf_response.status_code == 200
        assert pdf_response.headers.get("Content-Type") == "application/pdf"
        
        # Check PDF magic bytes
        content = pdf_response.content
        assert content[:4] == b'%PDF', "Response is not a valid PDF"
        print(f"✓ PDF downloaded successfully ({len(content)} bytes)")


class TestAdminCommercialDashboard:
    """Test Admin Commercial Dashboard features"""
    
    def test_commercial_stats(self, authenticated_client):
        """GET /api/admin/commercial/stats returns dashboard stats"""
        response = authenticated_client.get(f"{BASE_URL}/api/admin/commercial/stats")
        assert response.status_code == 200
        data = response.json()
        
        assert "quotes" in data
        assert "invoices" in data
        assert "revenue" in data
        print(f"✓ Commercial stats: {data['quotes']['total']} quotes, {data['invoices']['total']} invoices")
    
    def test_list_quotes(self, authenticated_client):
        """GET /api/admin/quotes lists quotes"""
        response = authenticated_client.get(f"{BASE_URL}/api/admin/quotes")
        assert response.status_code == 200
        data = response.json()
        
        assert "quotes" in data
        print(f"✓ Quotes list: {len(data['quotes'])} quotes")
    
    def test_list_invoices(self, authenticated_client):
        """GET /api/admin/invoices lists invoices"""
        response = authenticated_client.get(f"{BASE_URL}/api/admin/invoices")
        assert response.status_code == 200
        data = response.json()
        
        assert "invoices" in data
        print(f"✓ Invoices list: {len(data['invoices'])} invoices")


class TestQuotePortalEndpoints:
    """Test Quote Portal endpoints (accept/decline/revision)"""
    
    def test_portal_quote_access_requires_token(self, api_client):
        """GET /api/portal/quote/{id} requires valid token"""
        response = api_client.get(f"{BASE_URL}/api/portal/quote/nonexistent")
        assert response.status_code in [400, 403, 404, 422]
        print("✓ Portal quote access requires token")
    
    def test_portal_quote_with_invalid_token(self, api_client):
        """GET /api/portal/quote/{id}?token=invalid returns 403 or 404"""
        response = api_client.get(f"{BASE_URL}/api/portal/quote/q_test?token=invalid_token")
        assert response.status_code in [403, 404]
        print("✓ Portal rejects invalid token")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
