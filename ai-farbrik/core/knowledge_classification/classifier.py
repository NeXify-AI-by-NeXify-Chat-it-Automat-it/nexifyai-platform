"""
NeXifyAI Core: Knowledge Classification v4.8
AIC-49 Phase 1/2 — Enterprise Knowledge Classification

Classifies documents by type, domain, governance relevance, and priority.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
import json
import re


class KnowledgeDomain(Enum):
    ARCHITECTURE = "architecture"
    GOVERNANCE = "governance"
    RUNTIME = "runtime"
    SECURITY = "security"
    RECOVERY = "recovery"
    DEVELOPMENT = "development"
    OPERATIONS = "operations"
    LEGAL = "legal"
    BUSINESS = "business"
    UNKNOWN = "unknown"


class PriorityClass(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ClassificationResult:
    source_type: str
    domain: KnowledgeDomain = KnowledgeDomain.UNKNOWN
    priority: PriorityClass = PriorityClass.MEDIUM
    governance_tags: list = field(default_factory=list)
    requires_embedding: bool = True
    requires_reconciliation: bool = True
    sensitivity: str = "internal"
    confidence: float = 0.0
    metadata: dict = field(default_factory=dict)


class KnowledgeClassifier:
    """Governed knowledge classification engine."""

    # Domain detection patterns
    DOMAIN_PATTERNS = {
        KnowledgeDomain.ARCHITECTURE: [
            r'\b(architecture|system\s*design|component|ADR|decision\s*record)\b',
            r'\b(supabase|qdrant|redis|postgres|docker|kubernetes)\b',
        ],
        KnowledgeDomain.GOVERNANCE: [
            r'\b(governance|policy|compliance|rule|standard|directive)\b',
            r'\b(must|shall|required|mandatory|prohibited|forbidden)\b',
        ],
        KnowledgeDomain.SECURITY: [
            r'\b(security|vulnerability|CVE|exploit|threat|attack|breach)\b',
            r'\b(authentication|authorization|encryption|secret|token|key)\b',
        ],
        KnowledgeDomain.RUNTIME: [
            r'\b(runtime|execution|pipeline|queue|heartbeat|worker)\b',
            r'\b(embedding|retrieval|ingestion|chunking)\b',
        ],
        KnowledgeDomain.RECOVERY: [
            r'\b(recovery|rollback|restore|backup|disaster|incident)\b',
            r'\b(circuit\s*breaker|quarantine|failover|retry)\b',
        ],
        KnowledgeDomain.DEVELOPMENT: [
            r'\b(code|function|class|import|def\s|async\s|await)\b',
            r'\b(test|deploy|build|compile|lint|cicd|workflow)\b',
        ],
        KnowledgeDomain.OPERATIONS: [
            r'\b(monitoring|logging|metrics|alert|dashboard|health)\b',
            r'\b(deploy|scale|provision|orchestrate)\b',
        ],
    }

    # Priority detection patterns
    PRIORITY_PATTERNS = {
        PriorityClass.CRITICAL: [
            r'\b(CRITICAL|P0|EMERGENCY|IMMEDIATE|URGENT|BREAKING)\b',
            r'\b(critical|emergency|security\s*breach|data\s*loss|outage)\b',
        ],
        PriorityClass.HIGH: [
            r'\b(HIGH|P1|IMPORTANT|BLOCKER)\b',
            r'\b(high\s*priority|customer\s*impact|production\s*issue)\b',
        ],
        PriorityClass.LOW: [
            r'\b(LOW|P3|P4|NICE\s*TO\s*HAVE|COSMETIC)\b',
            r'\b(minor|cosmetic|documentation\s*only|typo)\b',
        ],
    }

    def __init__(self, config: dict = None):
        self.config = config or {}
        self._domain_patterns_compiled = {
            domain: [re.compile(p, re.IGNORECASE) for p in patterns]
            for domain, patterns in self.DOMAIN_PATTERNS.items()
        }
        self._priority_patterns_compiled = {
            prio: [re.compile(p, re.IGNORECASE) for p in patterns]
            for prio, patterns in self.PRIORITY_PATTERNS.items()
        }

    def classify(self, content: str, source: str, source_type: str,
                 title: str = "") -> ClassificationResult:
        """Classify a piece of knowledge."""
        result = ClassificationResult(source_type=source_type)

        # Domain classification
        domain_scores = self._score_domains(content, title)
        if domain_scores:
            best_domain = max(domain_scores, key=domain_scores.get)
            if domain_scores[best_domain] > 1:
                result.domain = best_domain
                result.confidence = min(domain_scores[best_domain] / 5.0, 1.0)

        # Priority classification
        result.priority = self._detect_priority(content, title)

        # Governance tags
        result.governance_tags = self._derive_tags(result, content)

        # Sensitivity
        result.sensitivity = self._detect_sensitivity(content)

        # Embedding requirement
        result.requires_embedding = len(content) > 100

        # Reconciliation requirement
        result.requires_reconciliation = result.priority in (
            PriorityClass.CRITICAL, PriorityClass.HIGH
        )

        result.metadata = {
            "content_length": len(content),
            "classified_at": datetime.now(timezone.utc).isoformat(),
            "classifier_version": "4.8",
        }

        return result

    def _score_domains(self, content: str, title: str) -> dict:
        """Score each domain based on pattern matches."""
        scores = {}
        text = f"{title}\n{content}"
        for domain, patterns in self._domain_patterns_compiled.items():
            score = sum(1 for p in patterns if p.search(text))
            if score > 0:
                scores[domain] = score
        return scores

    def _detect_priority(self, content: str, title: str) -> PriorityClass:
        """Detect priority from content."""
        text = f"{title}\n{content}"

        for prio, patterns in self._priority_patterns_compiled.items():
            for p in patterns:
                if p.search(text):
                    return prio

        return PriorityClass.MEDIUM

    def _derive_tags(self, result: ClassificationResult, content: str) -> list:
        """Derive governance tags from classification."""
        tags = [result.domain.value, result.source_type]

        if result.priority == PriorityClass.CRITICAL:
            tags.append("p0-critical")
        if result.sensitivity != "internal":
            tags.append(result.sensitivity)

        # Content-based tags
        if re.search(r'\b(ISO\s*27001|SOC2|DSGVO|GDPR|OWASP)\b', content, re.IGNORECASE):
            tags.append("compliance")
        if re.search(r'\b(incident|outage|breach|failure)\b', content, re.IGNORECASE):
            tags.append("incident-related")
        if re.search(r'\b(architecture|design|pattern)\b', content, re.IGNORECASE):
            tags.append("architecture")

        return tags

    def _detect_sensitivity(self, content: str) -> str:
        """Detect content sensitivity level."""
        if re.search(r'\b(password|secret|token|api_key|private_key)\b', content, re.IGNORECASE):
            return "confidential"
        if re.search(r'\b(customer|client|personal\s*data|PII)\b', content, re.IGNORECASE):
            return "restricted"
        return "internal"
