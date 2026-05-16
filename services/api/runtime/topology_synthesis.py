"""
NeXifyAI — Operational Topology Synthesis (E6.5)
Pre-flight system model builder. MUST run before any major mutation.

Answers: "Do we understand the system well enough to change it?"

Usage:
    from backend.runtime.topology_synthesis import TopologySynthesizer
    synth = TopologySynthesizer()
    if not synth.preflight():
        raise Exception("System model incomplete — cannot mutate")

Produces: IST↔SOLL topology map with dependencies, observers, and drift vectors.
"""

import os
import json
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone


@dataclass
class TopologyModel:
    """Complete system model for a specific change."""
    change_id: str
    change_description: str
    
    # IST-Zustand
    services_affected: List[str] = field(default_factory=list)
    dependencies_graph: Dict[str, List[str]] = field(default_factory=dict)
    canonical_sources: Dict[str, str] = field(default_factory=dict)
    observers: Dict[str, List[str]] = field(default_factory=dict)
    
    # Constraints
    forbidden_patterns: List[str] = field(default_factory=list)
    required_validations: List[str] = field(default_factory=list)
    
    # Failure model
    failure_classes: Dict[str, str] = field(default_factory=dict)
    contradiction_vectors: List[str] = field(default_factory=list)
    
    # Rollback
    rollback_topology: Dict[str, str] = field(default_factory=dict)
    
    # Verification
    preflight_passed: bool = False
    preflight_issues: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class TopologySynthesizer:
    """
    Pre-flight system model builder.
    
    Before ANY mutation (deploy, restart, migration, config change):
    1. Build complete system model
    2. Verify all dependencies are known
    3. Identify failure modes
    4. Validate constraints
    5. Only THEN allow mutation
    """
    
    REQUIRED_SECTIONS = [
        "services_affected",
        "dependencies_graph", 
        "canonical_sources",
        "observers",
        "rollback_topology",
    ]
    
    def preflight(self, change_description: str = "") -> TopologyModel:
        """
        Build and validate a complete system model before a change.
        Returns model with preflight_passed=True if ready.
        """
        model = TopologyModel(
            change_id=f"CHG-{int(time.time())}",
            change_description=change_description,
        )
        
        # 1. Identify affected services
        model.services_affected = self._discover_affected_services(change_description)
        
        # 2. Build dependency graph
        model.dependencies_graph = self._build_dependency_graph(model.services_affected)
        
        # 3. Identify canonical sources
        model.canonical_sources = self._identify_canonical_sources(model.services_affected)
        
        # 4. Map observers
        model.observers = self._map_observers(model.services_affected)
        
        # 5. Load constraints
        model.forbidden_patterns = self._load_constraints()
        
        # 6. Model failure classes
        model.failure_classes = self._model_failures(model.services_affected)
        
        # 7. Identify contradiction vectors
        model.contradiction_vectors = self._identify_contradiction_vectors(model)
        
        # 8. Build rollback topology
        model.rollback_topology = self._build_rollback(model.services_affected)
        
        # Validate
        model.preflight_issues = self._validate(model)
        model.preflight_passed = len(model.preflight_issues) == 0
        
        return model
    
    def _discover_affected_services(self, description: str) -> List[str]:
        """Discover which services are affected by a change."""
        from backend.runtime.service_registry import CANONICAL_REGISTRY
        
        text = description.lower()
        affected = []
        
        for svc_id in CANONICAL_REGISTRY:
            if svc_id.replace("-", " ") in text or svc_id in text:
                affected.append(svc_id)
        
        # Always include dependencies
        for svc_id in list(affected):
            svc = CANONICAL_REGISTRY.get(svc_id)
            if svc:
                for dep in svc.depends_on:
                    if dep not in affected:
                        affected.append(dep)
        
        if not affected:
            affected = list(CANONICAL_REGISTRY.keys())[:3]  # Default: core services
        
        return affected
    
    def _build_dependency_graph(self, services: List[str]) -> Dict[str, List[str]]:
        """Build dependency graph for affected services."""
        from backend.runtime.service_registry import CANONICAL_REGISTRY
        
        graph = {}
        for svc_id in services:
            svc = CANONICAL_REGISTRY.get(svc_id)
            if svc:
                graph[svc_id] = svc.depends_on
        return graph
    
    def _identify_canonical_sources(self, services: List[str]) -> Dict[str, str]:
        """Identify canonical truth sources for each service."""
        from backend.runtime.service_registry import CANONICAL_REGISTRY
        
        sources = {}
        for svc_id in services:
            svc = CANONICAL_REGISTRY.get(svc_id)
            if svc:
                sources[svc_id] = svc.source_of_truth_command
        return sources
    
    def _map_observers(self, services: List[str]) -> Dict[str, List[str]]:
        """Map which observers can see which services."""
        from backend.runtime.service_registry import CANONICAL_REGISTRY
        
        observers = {}
        for svc_id in services:
            svc = CANONICAL_REGISTRY.get(svc_id)
            if svc:
                observers[svc_id] = list(set(
                    ep.observer.value for ep in svc.endpoints
                ))
        return observers
    
    def _load_constraints(self) -> List[str]:
        """Load operational constraints from the Constitution."""
        return [
            "No mutation without re-observation",
            "Projection != Reality",
            "Confidence decays without evidence",
            "Recovery requires convergence",
            "Contradictions are signals, not noise",
            "No deployment without post-deploy validation",
            "Design drift is an incident",
            "Method persistence > incident persistence",
        ]
    
    def _model_failures(self, services: List[str]) -> Dict[str, str]:
        """Model possible failure classes for each service."""
        failures = {}
        for svc_id in services:
            failures[svc_id] = "port_binding | network_isolation | service_unresponsive | auth_required | endpoint_missing"
        return failures
    
    def _identify_contradiction_vectors(self, model: TopologyModel) -> List[str]:
        """Identify possible contradiction vectors."""
        vectors = []
        for svc_id in model.services_affected:
            observers = model.observers.get(svc_id, [])
            if len(observers) >= 2:
                for i, o1 in enumerate(observers):
                    for o2 in observers[i+1:]:
                        vectors.append(f"{o1} vs {o2} for {svc_id}")
        return vectors
    
    def _build_rollback(self, services: List[str]) -> Dict[str, str]:
        """Build rollback topology."""
        from backend.runtime.service_registry import CANONICAL_REGISTRY
        
        rollback = {}
        for svc_id in services:
            svc = CANONICAL_REGISTRY.get(svc_id)
            if svc:
                rollback[svc_id] = svc.recovery_command
        return rollback
    
    def _validate(self, model: TopologyModel) -> List[str]:
        """Validate model completeness. Returns list of issues (empty = valid)."""
        issues = []
        
        if not model.services_affected:
            issues.append("No services identified — cannot assess blast radius")
        
        if not model.dependencies_graph:
            issues.append("No dependency graph — cascading failures unpredictable")
        
        if not model.canonical_sources:
            issues.append("No canonical sources — cannot verify truth after mutation")
        
        if not model.observers:
            issues.append("No observers mapped — cannot validate convergence")
        
        if not model.rollback_topology:
            issues.append("No rollback topology — cannot recover from failed mutation")
        
        return issues


# ══════════════════════════════════════════════
# QUICK PREFLIGHT
# ══════════════════════════════════════════════

def preflight_check(change_description: str) -> TopologyModel:
    """Quick preflight before any mutation. Raises if model incomplete."""
    synth = TopologySynthesizer()
    model = synth.preflight(change_description)
    
    if not model.preflight_passed:
        issues = "\n  - ".join(model.preflight_issues)
        raise PreflightFailed(
            f"Preflight failed for '{change_description}':\n  - {issues}"
        )
    
    return model


class PreflightFailed(Exception):
    """Raised when preflight validation fails."""
    pass
