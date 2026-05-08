"""Compliance Agent — Real DSGVO/Legal checks via filesystem scanning."""

import os
from backend.agents.base_agent import BaseAgent


class ComplianceAgent(BaseAgent):
    
    def __init__(self):
        super().__init__("Compliance Agent", "DSGVO, Legal, and License compliance")
    
    def observe(self) -> dict:
        data = {
            "privacy_policy": False,
            "imprint": False,
            "cookie_consent": False,
            "license_policy": False,
            "vulnerability_policy": False,
            "data_processing_agreement": False,
            "security_txt": False,
            "missing_files": [],
        }
        
        repo = "/opt/nexifyai-website-sicherheitskopie"
        
        # Check legal docs directory
        legal_dir = os.path.join(repo, "docs/legal")
        if os.path.exists(legal_dir):
            legal_files = [f.lower() for f in os.listdir(legal_dir)]
            data["privacy_policy"] = any("privacy" in f or "datenschutz" in f for f in legal_files)
            data["imprint"] = any("imprint" in f or "impressum" in f for f in legal_files)
            data["data_processing_agreement"] = any("processing" in f or "avv" in f or "auftrags" in f for f in legal_files)
        
        if not data["privacy_policy"]:
            data["missing_files"].append("Privacy Policy / Datenschutzerklärung")
        if not data["imprint"]:
            data["missing_files"].append("Impressum (Pflicht in DE)")
        if not data["data_processing_agreement"]:
            data["missing_files"].append("Data Processing Agreement / AVV")
        
        # Check policies
        policies_dir = os.path.join(repo, "docs/policies")
        if os.path.exists(policies_dir):
            policy_files = [f.lower() for f in os.listdir(policies_dir)]
            data["license_policy"] = any("license" in f for f in policy_files)
            data["vulnerability_policy"] = any("vulnerability" in f for f in policy_files)
        
        if not data["license_policy"]:
            data["missing_files"].append("License Policy")
        
        # Check security.txt
        security_txt = os.path.join(repo, "public/.well-known/security.txt")
        data["security_txt"] = os.path.exists(security_txt)
        if not data["security_txt"]:
            data["missing_files"].append("security.txt (RFC 9116)")
        
        # Count GDPR-relevant issues
        data["total_issues"] = len(data["missing_files"])
        
        return data
    
    def analyze(self, data: dict) -> list:
        findings = []
        
        status_map = {
            "privacy_policy": "Privacy Policy",
            "imprint": "Impressum",
            "license_policy": "License Policy",
            "vulnerability_policy": "Vulnerability Policy",
            "security_txt": "security.txt",
            "data_processing_agreement": "Data Processing Agreement",
        }
        
        for key, label in status_map.items():
            if data.get(key):
                findings.append(f"✅ {label} present")
            else:
                findings.append(f"❌ {label} MISSING")
        
        if data["total_issues"] == 0:
            findings.append("✅ Full legal compliance")
        else:
            findings.append(f"⚠️  {data['total_issues']} legal document gaps")
        
        return findings
    
    def recommend(self, findings: list) -> list:
        recommendations = []
        for f in findings:
            if "❌" in f:
                name = f.replace("❌", "").replace("MISSING", "").strip()
                if "Privacy" in name:
                    recommendations.append("Create DSGVO-compliant privacy policy (Datenschutzerklärung)")
                elif "Impressum" in name:
                    recommendations.append("Create Impressum with §5 TMG requirements")
                elif "License" in name:
                    recommendations.append("Create license policy documenting approved/prohibited licenses")
                elif "security.txt" in name:
                    recommendations.append("Create security.txt per RFC 9116 for vulnerability disclosure")
                elif "Processing" in name:
                    recommendations.append("Create Data Processing Agreement (AVV) template")
        return recommendations
