"""QA Agent — Test coverage validation and quality gates."""

from backend.agents.base_agent import BaseAgent
from typing import Dict, List, Any
import os


class QAAgent(BaseAgent):
    
    def __init__(self):
        super().__init__("QA Agent", "Test validation and quality gate enforcement")
    
    def observe(self) -> Dict[str, Any]:
        data = {
            "backend_tests": 0,
            "frontend_tests": 0,
            "e2e_tests": False,
            "coverage_pct": 0,
        }
        
        repo = "/opt/nexifyai-platform"
        
        # Count backend tests
        backend_tests = os.path.join(repo, "backend/tests")
        if os.path.exists(backend_tests):
            count = 0
            for root, _, files in os.walk(backend_tests):
                count += sum(1 for f in files if f.startswith("test_") and f.endswith(".py"))
            data["backend_tests"] = count
        
        # Check frontend test config
        jest_config = os.path.join(repo, "frontend/jest.config.ts")
        data["frontend_configured"] = os.path.exists(jest_config)
        
        # Check Playwright
        playwright_config = os.path.join(repo, "playwright.config.ts")
        data["e2e_tests"] = os.path.exists(playwright_config)
        
        # Check pytest config
        pytest_ini = os.path.join(repo, "backend/pytest.ini")
        data["pytest_configured"] = os.path.exists(pytest_ini)
        
        # Estimate coverage based on test file count vs source files
        backend_src = os.path.join(repo, "backend")
        if os.path.exists(backend_src):
            src_count = 0
            for root, _, files in os.walk(backend_src):
                if 'tests' not in root and '__pycache__' not in root and 'migrations' not in root:
                    src_count += sum(1 for f in files if f.endswith('.py') and not f.startswith('__'))
            if src_count > 0:
                data["coverage_pct"] = min(100, (data["backend_tests"] / max(1, src_count)) * 50)
        
        return data
    
    def analyze(self, data: Dict[str, Any]) -> List[str]:
        findings = []
        
        if data["backend_tests"] == 0:
            findings.append("❌ No backend tests found")
        elif data["backend_tests"] < 10:
            findings.append(f"⚠️  Only {data['backend_tests']} backend tests (target: 50+)")
        else:
            findings.append(f"✅ {data['backend_tests']} backend tests")
        
        if not data.get("pytest_configured"):
            findings.append("⚠️  pytest not configured")
        else:
            findings.append("✅ pytest configured with coverage targets")
        
        if not data.get("frontend_configured"):
            findings.append("⚠️  Frontend test framework not configured")
        else:
            findings.append("✅ Frontend Jest configured")
        
        if not data["e2e_tests"]:
            findings.append("⚠️  No E2E tests (Playwright) configured")
        
        if data["coverage_pct"] < 80:
            findings.append(f"⚠️  Estimated coverage: {data['coverage_pct']:.0f}% (target: 80%)")
        
        return findings
    
    def recommend(self, findings: List[str]) -> List[str]:
        recommendations = []
        for f in findings:
            if "No backend tests" in f:
                recommendations.append("Write pytest tests for all API endpoints")
            if "E2E" in f:
                recommendations.append("Set up Playwright for critical user flows")
            if "coverage" in f:
                recommendations.append("Add unit tests for uncovered modules")
        return recommendations
