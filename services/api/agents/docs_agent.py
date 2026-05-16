"""Docs Agent — Documentation completeness and freshness monitoring."""

from backend.agents.base_agent import BaseAgent
from typing import Dict, List, Any
import os
import time


class DocsAgent(BaseAgent):
    
    def __init__(self):
        super().__init__("Docs Agent", "Documentation monitoring and gap detection")
    
    def observe(self) -> Dict[str, Any]:
        data = {
            "total_docs": 0,
            "stale_docs": 0,
            "missing_docs": [],
            "doc_structure": {},
        }
        
        repo = "/opt/nexifyai-platform/docs"
        if os.path.exists(repo):
            for root, dirs, files in os.walk(repo):
                for f in files:
                    if f.endswith('.md'):
                        data["total_docs"] += 1
                        filepath = os.path.join(root, f)
                        age_days = (time.time() - os.path.getmtime(filepath)) / 86400
                        if age_days > 30:
                            data["stale_docs"] += 1
        
        # Required docs checklist
        required = [
            "DOS-v2.0.md",
            "architecture/zielarchitektur-v2.md",
            "architecture/bauplan.md",
            "governance/rollen-kompendium.md",
            "governance/raci.yaml",
            "policies/security-policy.md",
            "policies/vulnerability-policy.md",
        ]
        
        for doc in required:
            full_path = os.path.join(repo, doc)
            if not os.path.exists(full_path):
                data["missing_docs"].append(doc)
        
        return data
    
    def analyze(self, data: Dict[str, Any]) -> List[str]:
        findings = []
        
        findings.append(f"Total docs: {data['total_docs']}")
        
        if data["stale_docs"] > 0:
            findings.append(f"⚠️  {data['stale_docs']} docs stale (>30 days without update)")
        else:
            findings.append("✅ All docs fresh")
        
        if data["missing_docs"]:
            findings.append(f"❌ Missing docs: {', '.join(data['missing_docs'][:3])}")
        else:
            findings.append("✅ All required docs present")
        
        return findings
    
    def recommend(self, findings: List[str]) -> List[str]:
        recommendations = []
        if "Missing docs" in str(findings):
            recommendations.append("Create missing documentation files")
        if "stale" in str(findings):
            recommendations.append("Review and update stale documents")
        return recommendations
