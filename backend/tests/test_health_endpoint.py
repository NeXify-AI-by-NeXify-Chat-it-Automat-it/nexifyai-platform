"""
Integration Test — Health Endpoint
Prüft die /api/health Route auf korrekte Antwort-Struktur
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Skip this test if no connection to backend
pytestmark = pytest.mark.skipif(
    os.environ.get("SKIP_INTEGRATION", "1") == "1",
    reason="Integration test requires running backend"
)


@pytest.mark.asyncio
async def test_health_endpoint_structure():
    """Test: /api/health antwortet mit korrekter Struktur."""
    import httpx
    
    backend_url = os.environ.get("BACKEND_URL", "http://localhost:8001")
    
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"{backend_url}/api/health")
            
            assert response.status_code == 200
            data = response.json()
            
            # Pflichtfelder
            assert "status" in data
            assert "services" in data
            
            # Mindestens diese Services sollten existieren
            required_services = ["mongodb", "supabase", "openrouter"]
            for svc in required_services:
                assert svc in data["services"], f"Service {svc} fehlt"
                
    except httpx.ConnectError:
        pytest.skip("Backend nicht erreichbar")
    except Exception as e:
        pytest.fail(f"Unerwarteter Fehler: {e}")
