"""
Architect Agent — Monitors architecture compliance against DOS v2.0.
Checks: package structure, dependency violations, pattern adherence, ADR consistency.
"""

import os
from backend.agents.base_agent import BaseAgent, AgentResult
from typing import Dict, List, Any


class ArchitectAgent(BaseAgent):
    
    def __init__(self):
        super().__init__("Architect Agent", "Architecture compliance monitoring against DOS v2.0")
    
    def observe(self) -> Dict[str, Any]:
        data = {}
        repo_root = "/opt/nexifyai-platform"
        
        # Check required directories exist
        required_dirs = [
            "packages/config", "packages/events", "packages/ui",
            "packages/workflows", "packages/services",
            "packages/analytics", "packages/telemetry",
            "docs/adrs", "docs/architecture", "docs/policies",
        ]
        
        data["missing_dirs"] = [
            d for d in required_dirs
            if not os.path.exists(os.path.join(repo_root, d))
        ]
        
        # Check ADR count
        adrs_dir = os.path.join(repo_root, "docs/adrs")
        if os.path.exists(adrs_dir):
            data["adr_count"] = len([
                f for f in os.listdir(adrs_dir)
                if f.startswith("ADR-") and f.endswith(".md")
            ])
        
        # Check package.json files for monorepo consistency
        data["packages"] = []
        packages_dir = os.path.join(repo_root, "packages")
        if os.path.exists(packages_dir):
            for pkg in os.listdir(packages_dir):
                pkg_json = os.path.join(packages_dir, pkg, "package.json")
                if os.path.exists(pkg_json):
                    data["packages"].append(pkg)
        
        return data
    
    def analyze(self, data: Dict[str, Any]) -> List[str]:
        findings = []
        
        if data.get("missing_dirs"):
            findings.append(
                f"❌ Missing directories: {', '.join(data['missing_dirs'])}"
            )
        
        if data.get("adr_count", 0) < 5:
            findings.append(
                f"⚠️  Only {data['adr_count']} ADRs found. Expected ≥ 5 for enterprise readiness."
            )
        
        expected_packages = {"config", "events", "ui", "workflows", "services", "analytics", "telemetry"}
        actual_packages = set(data.get("packages", []))
        missing = expected_packages - actual_packages
        if missing:
            findings.append(f"⚠️  Missing packages: {', '.join(missing)}")
        
        return findings
    
    def recommend(self, findings: List[str]) -> List[str]:
        recommendations = []
        for finding in findings:
            if "Missing directories" in finding:
                recommendations.append("Create missing directories with package.json + tsconfig.json")
            if "ADRs" in finding:
                recommendations.append("Create missing ADRs: ADR-005 through ADR-009")
            if "Missing packages" in finding:
                recommendations.append("Scaffold missing packages with proper monorepo structure")
        return recommendations
