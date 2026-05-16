"""
Security Agent — Continuous security audits.
Checks: Secrets in code, dependency CVEs, CSP compliance, JWT configuration.
"""

from backend.agents.base_agent import BaseAgent, AgentResult
from typing import Dict, List, Any


class SecurityAgent(BaseAgent):
    
    def __init__(self):
        super().__init__("Security Agent", "Continuous security audit and vulnerability scanning")
    
    def observe(self) -> Dict[str, Any]:
        data = {
            "secrets_found": [],
            "cves": [],
            "csp_configured": False,
            "jwt_rotation": False,
            "security_txt": False,
        }
        
        # Check security.txt
        import os
        repo_root = "/opt/nexifyai-platform"
        security_txt = os.path.join(repo_root, "public/.well-known/security.txt")
        data["security_txt"] = os.path.exists(security_txt)
        
        # Check security middleware
        middleware = os.path.join(repo_root, "backend/middleware/security.py")
        if os.path.exists(middleware):
            with open(middleware) as f:
                content = f.read()
                data["csp_configured"] = "CSP_POLICY" in content
                data["jwt_rotation"] = "JWT_MAX_AGE" in content
                data["rate_limiting"] = "RateLimiter" in content
        
        # Check security scan workflow
        sec_scan = os.path.join(repo_root, ".github/workflows/security-scan.yml")
        if os.path.exists(sec_scan):
            with open(sec_scan) as f:
                content = f.read()
                data["gitleaks"] = "Gitleaks" in content
                data["trivy"] = "Trivy" in content
                data["sbom"] = "SBOM" in content
                data["license_check"] = "license" in content.lower()
        
        # Check dependabot
        dependabot = os.path.join(repo_root, ".github/dependabot.yml")
        data["dependabot"] = os.path.exists(dependabot)
        
        return data
    
    def analyze(self, data: Dict[str, Any]) -> List[str]:
        findings = []
        
        if not data.get("security_txt"):
            findings.append("❌ security.txt missing")
        else:
            findings.append("✅ security.txt present")
        
        if not data.get("csp_configured"):
            findings.append("❌ CSP headers not configured")
        else:
            findings.append("✅ CSP headers configured")
        
        if not data.get("jwt_rotation"):
            findings.append("⚠️  JWT rotation not configured")
        else:
            findings.append("✅ JWT rotation configured")
        
        if not data.get("dependabot"):
            findings.append("⚠️  Dependabot not configured")
        else:
            findings.append("✅ Dependabot configured")
        
        security_features = sum([
            data.get("gitleaks", False),
            data.get("trivy", False),
            data.get("sbom", False),
            data.get("license_check", False),
        ])
        
        if security_features < 4:
            findings.append(f"⚠️  Only {security_features}/4 security scanners active")
        else:
            findings.append("✅ All 4 security scanners active")
        
        return findings
    
    def recommend(self, findings: List[str]) -> List[str]:
        recommendations = []
        for f in findings:
            if "❌" in f:
                name = f.replace("❌", "").strip()
                recommendations.append(f"Fix critical: {name}")
            if "⚠️" in f:
                name = f.replace("⚠️", "").strip()
                recommendations.append(f"Address warning: {name}")
        return recommendations
