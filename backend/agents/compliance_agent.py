"""Compliance Agent — DSGVO, Legal, License compliance monitoring."""

from backend.agents.base_agent import BaseAgent
from typing import Dict, List, Any
import os


class ComplianceAgent(BaseAgent):
    
    def __init__(self):
        super().__init__("Compliance Agent", "DSGVO, Legal, and License compliance")
    
    def observe(self) -> Dict[str, Any]:
        data = {
            "cookie_consent": False,
            "privacy_policy": False,
            "imprint": False,
            "license_check": False,
            "data_processing_agreement": False,
        }
        
        repo = "/opt/nexifyai-website-sicherheitskopie"
        
        # Check legal docs
        legal_dir = os.path.join(repo, "docs/legal")
        if os.path.exists(legal_dir):
            legal_files = os.listdir(legal_dir)
            data["privacy_policy"] = any("privacy" in f.lower() for f in legal_files)
            data["imprint"] = any("imprint" in f.lower() or "impressum" in f.lower() for f in legal_files)
        
        # Check license policy
        license_policy = os.path.join(repo, "docs/policies/license-policy.md") if False else None
        # Using security policy as proxy
        data["license_check"] = os.path.exists(
            os.path.join(repo, "docs/policies/vulnerability-policy.md")
        )
        
        return data
    
    def analyze(self, data: Dict[str, Any]) -> List[str]:
        findings = []
        
        if not data.get("privacy_policy"):
            findings.append("⚠️  Privacy policy not found")
        else:
            findings.append("✅ Privacy policy present")
        
        if not data.get("imprint"):
            findings.append("⚠️  Impressum not found (Pflicht in DE)")
        else:
            findings.append("✅ Impressum present")
        
        if not data.get("cookie_consent"):
            findings.append("⚠️  Cookie consent mechanism TBD")
        
        return findings
    
    def recommend(self, findings: List[str]) -> List[str]:
        recommendations = []
        for f in findings:
            if "Privacy policy" in f:
                recommendations.append("Create DSGVO-compliant privacy policy")
            if "Impressum" in f:
                recommendations.append("Create Impressum (legal requirement in Germany)")
            if "Cookie" in f:
                recommendations.append("Implement cookie consent banner with opt-in")
        return recommendations
