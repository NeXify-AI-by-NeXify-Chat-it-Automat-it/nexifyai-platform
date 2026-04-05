"""
Iteration 79 - DeepSeek Live-Migration, Crawl4AI, Nutrient AI, Intelligence Testing
Tests for:
1. GET /api/admin/nexify-ai/status - DeepSeek primary, Arcee fallback
2. GET /api/health - All 8 services including deepseek, arcee, workers
3. POST /api/admin/intelligence/crawl - Web crawling with Crawl4AI
4. POST /api/admin/intelligence/research-company - Company research
5. GET /api/admin/intelligence/status - Crawl4AI and Nutrient status
6. GET /api/admin/oracle/leitstelle - German status names
7. GET /api/admin/service-templates - 9 templates
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://contract-os.preview.emergentagent.com').rstrip('/')

class TestDeepSeekMigration:
    """Tests for DeepSeek as primary LLM with Arcee fallback"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get admin authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": "p.courbois@icloud.com", "password": "1def!xO2022!!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access_token in response"
        return data["access_token"]
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Get headers with auth token"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
    
    def test_nexify_ai_status_deepseek_primary(self, auth_headers):
        """Test GET /api/admin/nexify-ai/status returns DeepSeek as primary LLM"""
        response = requests.get(f"{BASE_URL}/api/admin/nexify-ai/status", headers=auth_headers)
        assert response.status_code == 200, f"Status check failed: {response.text}"
        
        data = response.json()
        # Verify master_llm is deepseek
        assert data.get("master_llm") == "deepseek", f"Expected master_llm='deepseek', got {data.get('master_llm')}"
        
        # Verify deepseek is configured and connected
        deepseek = data.get("deepseek", {})
        assert deepseek.get("configured") == True, "DeepSeek should be configured"
        assert deepseek.get("connected") == True, f"DeepSeek should be connected, got: {deepseek}"
        assert deepseek.get("primary") == True, "DeepSeek should be marked as primary"
        
        # Verify arcee is configured as fallback
        arcee = data.get("arcee", {})
        assert arcee.get("configured") == True, "Arcee should be configured"
        assert arcee.get("fallback") == True, "Arcee should be marked as fallback"
        
        print(f"NeXify AI Status: master_llm={data.get('master_llm')}, deepseek.connected={deepseek.get('connected')}, arcee.fallback={arcee.get('fallback')}")
    
    def test_health_endpoint_all_services(self):
        """Test GET /api/health returns all 8 services"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.text}"
        
        data = response.json()
        services = data.get("services", {})
        
        # Verify all 8 expected services are present
        expected_services = ["mongodb", "supabase", "deepseek", "arcee", "mem0", "resend", "revolut", "workers"]
        for svc in expected_services:
            assert svc in services, f"Service '{svc}' missing from health check"
            print(f"  {svc}: {services[svc].get('status')}")
        
        # Verify deepseek and arcee are OK
        assert services.get("deepseek", {}).get("status") == "ok", f"DeepSeek should be OK, got: {services.get('deepseek')}"
        assert services.get("arcee", {}).get("status") == "ok", f"Arcee should be OK, got: {services.get('arcee')}"
        assert services.get("workers", {}).get("status") == "ok", f"Workers should be OK, got: {services.get('workers')}"
        
        print(f"Health check: status={data.get('status')}, services_count={len(services)}")


class TestIntelligenceEndpoints:
    """Tests for Crawl4AI and Nutrient AI Intelligence endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get admin authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": "p.courbois@icloud.com", "password": "1def!xO2022!!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Get headers with auth token"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
    
    def test_intelligence_status(self, auth_headers):
        """Test GET /api/admin/intelligence/status returns Crawl4AI and Nutrient status"""
        response = requests.get(f"{BASE_URL}/api/admin/intelligence/status", headers=auth_headers)
        assert response.status_code == 200, f"Intelligence status failed: {response.text}"
        
        data = response.json()
        
        # Verify crawl4ai status
        crawl4ai = data.get("crawl4ai", {})
        assert "installed" in crawl4ai, "crawl4ai.installed should be present"
        assert crawl4ai.get("installed") == True, f"Crawl4AI should be installed, got: {crawl4ai}"
        
        # Verify nutrient status (may not be configured)
        nutrient = data.get("nutrient", {})
        assert "configured" in nutrient, "nutrient.configured should be present"
        
        print(f"Intelligence Status: crawl4ai.installed={crawl4ai.get('installed')}, nutrient.configured={nutrient.get('configured')}")
    
    def test_crawl_url_endpoint(self, auth_headers):
        """Test POST /api/admin/intelligence/crawl with example.com"""
        response = requests.post(
            f"{BASE_URL}/api/admin/intelligence/crawl",
            headers=auth_headers,
            json={"url": "https://example.com", "extract_mode": "markdown"},
            timeout=60  # Crawling can take time
        )
        assert response.status_code == 200, f"Crawl failed: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, f"Crawl should succeed, got: {data}"
        assert "title" in data, "Response should contain title"
        assert "content" in data, "Response should contain content"
        
        # Verify we got actual content
        content = data.get("content", "")
        assert len(content) > 50, f"Content should have meaningful length, got {len(content)} chars"
        
        print(f"Crawl result: success={data.get('success')}, title='{data.get('title', '')[:50]}', content_length={len(content)}")
    
    def test_research_company_endpoint(self, auth_headers):
        """Test POST /api/admin/intelligence/research-company with example.com"""
        response = requests.post(
            f"{BASE_URL}/api/admin/intelligence/research-company",
            headers=auth_headers,
            json={"url": "https://example.com"},
            timeout=90  # Company research can take longer
        )
        assert response.status_code == 200, f"Research company failed: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, f"Research should succeed, got: {data}"
        assert "company" in data, "Response should contain company data"
        
        company = data.get("company", {})
        assert "title" in company, "Company data should have title"
        
        print(f"Research result: success={data.get('success')}, company_title='{company.get('title', '')[:50]}'")


class TestOracleAndTemplates:
    """Tests for Oracle Leitstelle and Service Templates"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get admin authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": "p.courbois@icloud.com", "password": "1def!xO2022!!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Get headers with auth token"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
    
    def test_oracle_leitstelle_german_status(self, auth_headers):
        """Test GET /api/admin/oracle/leitstelle returns German status names"""
        response = requests.get(f"{BASE_URL}/api/admin/oracle/leitstelle", headers=auth_headers)
        assert response.status_code == 200, f"Leitstelle failed: {response.text}"
        
        data = response.json()
        pipeline = data.get("pipeline", {})
        
        # Verify German status names are present
        expected_german_statuses = ["erkannt", "in_arbeit", "wartend", "in_loop", "validiert_24h", "fehlgeschlagen_24h", "eskaliert"]
        for status in expected_german_statuses:
            assert status in pipeline, f"German status '{status}' missing from pipeline"
        
        print(f"Leitstelle pipeline statuses: {list(pipeline.keys())}")
    
    def test_service_templates_count(self, auth_headers):
        """Test GET /api/admin/service-templates returns 9 templates"""
        response = requests.get(f"{BASE_URL}/api/admin/service-templates", headers=auth_headers)
        assert response.status_code == 200, f"Service templates failed: {response.text}"
        
        data = response.json()
        templates = data.get("templates", [])
        
        assert len(templates) == 9, f"Expected 9 templates, got {len(templates)}"
        
        # Verify expected template keys
        expected_keys = [
            "starter_ai_agenten", "growth_ai_agenten", "seo_starter", "seo_growth",
            "website_starter", "website_professional", "website_enterprise",
            "app_mvp", "app_professional"
        ]
        template_keys = [t.get("key") for t in templates]
        for key in expected_keys:
            assert key in template_keys, f"Template '{key}' missing"
        
        print(f"Service templates: {len(templates)} templates found")
        for t in templates:
            print(f"  - {t.get('key')}: {t.get('name')}")


class TestAdminLogin:
    """Test admin login flow"""
    
    def test_admin_login_success(self):
        """Test POST /api/admin/login with valid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": "p.courbois@icloud.com", "password": "1def!xO2022!!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        
        data = response.json()
        assert "access_token" in data, "Response should contain access_token"
        assert len(data["access_token"]) > 20, "Token should be substantial"
        
        print(f"Login successful, token length: {len(data['access_token'])}")
    
    def test_admin_login_invalid_credentials(self):
        """Test POST /api/admin/login with invalid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/admin/login",
            data={"username": "wrong@email.com", "password": "wrongpassword"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code in [401, 403], f"Expected 401/403 for invalid credentials, got {response.status_code}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
