"""Refactor Agent — Technical debt detection and refactoring suggestions."""

from backend.agents.base_agent import BaseAgent
from typing import Dict, List, Any
import os


class RefactorAgent(BaseAgent):
    
    def __init__(self):
        super().__init__("Refactor Agent", "Technical debt detection and refactoring")
    
    def observe(self) -> Dict[str, Any]:
        data = {
            "large_files": [],
            "todo_count": 0,
            "deprecated_apis": [],
            "duplicated_code_hint": False,
        }
        
        repo = "/opt/nexifyai-platform"
        
        # Find large files (>500 lines)
        for root, _, files in os.walk(repo):
            if 'node_modules' in root or '.git' in root:
                continue
            for f in files:
                if f.endswith(('.py', '.ts', '.tsx', '.js')):
                    filepath = os.path.join(root, f)
                    try:
                        with open(filepath) as fh:
                            lines = sum(1 for _ in fh)
                        if lines > 500:
                            rel_path = os.path.relpath(filepath, repo)
                            data["large_files"].append(f"{rel_path} ({lines} lines)")
                    except:
                        pass
        
        # Count TODO comments
        for root, _, files in os.walk(repo):
            if 'node_modules' in root or '.git' in root:
                continue
            for f in files:
                if f.endswith(('.py', '.ts', '.tsx')):
                    filepath = os.path.join(root, f)
                    try:
                        with open(filepath) as fh:
                            for line in fh:
                                if 'TODO' in line:
                                    data["todo_count"] += 1
                    except:
                        pass
        
        return data
    
    def analyze(self, data: Dict[str, Any]) -> List[str]:
        findings = []
        
        if data["large_files"]:
            findings.append(f"⚠️  {len(data['large_files'])} large files (>500 lines):")
            for f in data["large_files"][:3]:
                findings.append(f"   - {f}")
        else:
            findings.append("✅ No files >500 lines")
        
        if data["todo_count"] > 10:
            findings.append(f"⚠️  {data['todo_count']} TODOs in codebase")
        else:
            findings.append(f"✅ Only {data['todo_count']} TODOs")
        
        return findings
    
    def recommend(self, findings: List[str]) -> List[str]:
        recommendations = []
        for f in findings:
            if "large files" in f:
                recommendations.append("Split large files into modules (SRP)")
            if "TODO" in f:
                recommendations.append("Create tasks for outstanding TODOs")
        return recommendations
