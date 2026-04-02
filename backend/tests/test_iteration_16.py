"""
NeXifyAI Iteration 16 Backend Tests
Testing: Integrations UI, SEO pages, KI-SEO product, Services/Bundles, PDF tariff sheets, Trust section, Legal pages
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthAndBasics:
    """Basic health and API availability tests"""
    
    def test_health_endpoint(self):
        """Health check endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✓ Health endpoint working")

    def test_company_endpoint(self):
        """Company info endpoint returns data"""
        response = requests.get(f"{BASE_URL}/api/company")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "email" in data
        print("✓ Company endpoint working")


class TestTariffSheetPDF:
    """PDF tariff sheet download tests"""
    
    def test_tariff_sheet_all_categories(self):
        """PDF tariff sheet with category=all returns valid PDF"""
        response = requests.get(f"{BASE_URL}/api/product/tariff-sheet?category=all")
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/pdf"
        # Check PDF magic bytes
        assert response.content[:4] == b'%PDF'
        print(f"✓ Tariff sheet PDF (all) - {len(response.content)} bytes")

    def test_tariff_sheet_seo_category(self):
        """PDF tariff sheet with category=seo returns valid PDF"""
        response = requests.get(f"{BASE_URL}/api/product/tariff-sheet?category=seo")
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/pdf"
        assert response.content[:4] == b'%PDF'
        print(f"✓ Tariff sheet PDF (seo) - {len(response.content)} bytes")

    def test_tariff_sheet_agents_category(self):
        """PDF tariff sheet with category=agents returns valid PDF"""
        response = requests.get(f"{BASE_URL}/api/product/tariff-sheet?category=agents")
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/pdf"
        assert response.content[:4] == b'%PDF'
        print(f"✓ Tariff sheet PDF (agents) - {len(response.content)} bytes")

    def test_tariff_sheet_websites_category(self):
        """PDF tariff sheet with category=websites returns valid PDF"""
        response = requests.get(f"{BASE_URL}/api/product/tariff-sheet?category=websites")
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/pdf"
        assert response.content[:4] == b'%PDF'
        print(f"✓ Tariff sheet PDF (websites) - {len(response.content)} bytes")

    def test_tariff_sheet_bundles_category(self):
        """PDF tariff sheet with category=bundles returns valid PDF"""
        response = requests.get(f"{BASE_URL}/api/product/tariff-sheet?category=bundles")
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/pdf"
        assert response.content[:4] == b'%PDF'
        print(f"✓ Tariff sheet PDF (bundles) - {len(response.content)} bytes")

    def test_tariff_sheet_invalid_category(self):
        """PDF tariff sheet with invalid category returns 400"""
        response = requests.get(f"{BASE_URL}/api/product/tariff-sheet?category=invalid")
        assert response.status_code == 400
        print("✓ Tariff sheet invalid category returns 400")


class TestProductEndpoints:
    """Product/tariff/services API tests"""
    
    def test_tariffs_endpoint(self):
        """GET /api/product/tariffs returns tariff data"""
        response = requests.get(f"{BASE_URL}/api/product/tariffs")
        assert response.status_code == 200
        data = response.json()
        assert "tariffs" in data
        tariffs = data["tariffs"]
        # Should have starter and growth
        assert "starter" in tariffs or len(tariffs) >= 1
        print(f"✓ Tariffs endpoint - {len(tariffs)} tariffs")

    def test_services_endpoint(self):
        """GET /api/product/services returns services and bundles"""
        response = requests.get(f"{BASE_URL}/api/product/services")
        assert response.status_code == 200
        data = response.json()
        assert "services" in data
        assert "bundles" in data
        services = data["services"]
        bundles = data["bundles"]
        # Should have multiple services
        assert len(services) >= 5
        # Should have bundles
        assert len(bundles) >= 2
        print(f"✓ Services endpoint - {len(services)} services, {len(bundles)} bundles")

    def test_compliance_endpoint(self):
        """GET /api/product/compliance returns compliance data"""
        response = requests.get(f"{BASE_URL}/api/product/compliance")
        assert response.status_code == 200
        data = response.json()
        assert "compliance" in data
        compliance = data["compliance"]
        # Should have GDPR, EU AI Act, etc.
        assert len(compliance) >= 4
        print(f"✓ Compliance endpoint - {len(compliance)} items")

    def test_faq_endpoint(self):
        """GET /api/product/faq returns FAQ data"""
        response = requests.get(f"{BASE_URL}/api/product/faq")
        assert response.status_code == 200
        data = response.json()
        assert "faq" in data
        faq = data["faq"]
        # Should have multiple FAQ entries
        assert len(faq) >= 10
        print(f"✓ FAQ endpoint - {len(faq)} entries")


class TestFrontendPages:
    """Frontend page loading tests"""
    
    def test_landing_page_de(self):
        """German landing page loads"""
        response = requests.get(f"{BASE_URL}/de")
        assert response.status_code == 200
        assert "NeXify" in response.text
        print("✓ German landing page loads")

    def test_landing_page_nl(self):
        """Dutch landing page loads"""
        response = requests.get(f"{BASE_URL}/nl")
        assert response.status_code == 200
        assert "NeXify" in response.text
        print("✓ Dutch landing page loads")

    def test_landing_page_en(self):
        """English landing page loads"""
        response = requests.get(f"{BASE_URL}/en")
        assert response.status_code == 200
        assert "NeXify" in response.text
        print("✓ English landing page loads")


class TestLegalPages:
    """Legal pages loading tests"""
    
    def test_datenschutz_de(self):
        """German privacy page loads at /de/datenschutz"""
        response = requests.get(f"{BASE_URL}/de/datenschutz")
        assert response.status_code == 200
        print("✓ /de/datenschutz loads")

    def test_agb_de(self):
        """German terms page loads at /de/agb"""
        response = requests.get(f"{BASE_URL}/de/agb")
        assert response.status_code == 200
        print("✓ /de/agb loads")

    def test_impressum_de(self):
        """German imprint page loads at /de/impressum"""
        response = requests.get(f"{BASE_URL}/de/impressum")
        assert response.status_code == 200
        print("✓ /de/impressum loads")

    def test_ki_hinweise_de(self):
        """German AI transparency page loads at /de/ki-hinweise"""
        response = requests.get(f"{BASE_URL}/de/ki-hinweise")
        assert response.status_code == 200
        print("✓ /de/ki-hinweise loads")


class TestIntegrationDetailPages:
    """Integration detail SEO pages tests"""
    
    def test_salesforce_integration_page(self):
        """Salesforce integration page loads at /integrationen/salesforce"""
        response = requests.get(f"{BASE_URL}/integrationen/salesforce")
        assert response.status_code == 200
        print("✓ /integrationen/salesforce loads")

    def test_hubspot_integration_page(self):
        """HubSpot integration page loads at /integrationen/hubspot"""
        response = requests.get(f"{BASE_URL}/integrationen/hubspot")
        assert response.status_code == 200
        print("✓ /integrationen/hubspot loads")

    def test_datev_integration_page(self):
        """DATEV integration page loads at /integrationen/datev"""
        response = requests.get(f"{BASE_URL}/integrationen/datev")
        assert response.status_code == 200
        print("✓ /integrationen/datev loads")


class TestSecurityHeaders:
    """Security headers verification"""
    
    def test_security_headers_present(self):
        """API responses include security headers"""
        response = requests.get(f"{BASE_URL}/api/health")
        headers = response.headers
        
        assert headers.get("X-Content-Type-Options") == "nosniff"
        assert headers.get("X-Frame-Options") == "DENY"
        assert "X-XSS-Protection" in headers
        assert "Referrer-Policy" in headers
        assert "Permissions-Policy" in headers
        assert "Cache-Control" in headers
        print("✓ Security headers present")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
