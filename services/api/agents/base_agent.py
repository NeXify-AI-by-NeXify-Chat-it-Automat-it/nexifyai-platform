"""
NeXifyAI — Base Agent Class
All agents extend this class. Provides run(), observe(), decide(), act() loop.

Usage:
    from backend.agents.base_agent import BaseAgent
    class MyAgent(BaseAgent):
        ...
"""

import time
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from enum import Enum


class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentResult:
    """Standardized agent execution result."""
    agent_name: str
    status: AgentStatus = AgentStatus.IDLE
    findings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    actions_taken: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    duration_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ══════════════════════════════════════════════
# BASE AGENT
# ══════════════════════════════════════════════

class BaseAgent(ABC):
    """
    Base class for all NeXifyAI autonomous agents.
    
    Implements the OODA loop:
    1. Observe — Gather system state
    2. Orient — Analyze against policies/rules
    3. Decide — Choose action
    4. Act — Execute action
    
    Agents are stateless per run. Results are persisted to Brain.
    """
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.result = AgentResult(agent_name=name)
    
    @abstractmethod
    def observe(self) -> Dict[str, Any]:
        """Gather data from the system."""
        pass
    
    @abstractmethod
    def analyze(self, data: Dict[str, Any]) -> List[str]:
        """Analyze data against rules/policies. Returns findings."""
        pass
    
    @abstractmethod
    def recommend(self, findings: List[str]) -> List[str]:
        """Generate recommendations based on findings."""
        pass
    
    def run(self) -> AgentResult:
        """Execute the agent's OODA loop."""
        start = time.time()
        self.result.status = AgentStatus.RUNNING
        
        try:
            # 1. Observe
            data = self.observe()
            
            # 2. Analyze
            findings = self.analyze(data)
            self.result.findings = findings
            
            # 3. Recommend
            recommendations = self.recommend(findings)
            self.result.recommendations = recommendations
            
            self.result.status = AgentStatus.COMPLETED
            
        except Exception as e:
            self.result.status = AgentStatus.FAILED
            self.result.errors.append(str(e))
        
        self.result.duration_ms = (time.time() - start) * 1000
        return self.result
    
    def to_brain_entry(self) -> Dict:
        """Format result for Brain persistence."""
        return {
            "type": "agent_run",
            "agent": self.name,
            "status": self.result.status.value,
            "findings_count": len(self.result.findings),
            "recommendations_count": len(self.result.recommendations),
            "duration_ms": self.result.duration_ms,
            "timestamp": self.result.timestamp,
            "summary": {
                "findings": self.result.findings[:5],
                "recommendations": self.result.recommendations[:5],
            }
        }
