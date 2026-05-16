"""
NeXifyAI — Incremental Propagation Engine (R1.1)
O(k) not O(N). Only recomputes affected subgraphs.

Like Bazel/Turborepo/Nx: dirty-node tracking + topological invalidation.

Usage:
    engine = IncrementalPropagationEngine()
    engine.set_confidence('supabase-db', 0.30)  # Marks dirty
    engine.propagate_incremental()                # Only recomputes affected nodes
    # vs old: engine.propagate() recomputes ALL nodes every time
"""

import time
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple
from collections import deque


@dataclass
class IncrementalNode:
    """A node in the incremental propagation graph."""
    service: str
    local_confidence: float = 1.0
    effective_confidence: float = 1.0
    parents: Dict[str, float] = field(default_factory=dict)
    children: List[str] = field(default_factory=list)
    
    # Incremental tracking
    dirty: bool = False           # Needs recomputation
    version: int = 0              # Monotonic version counter
    last_computed_at: float = 0.0
    computation_count: int = 0    # How many times recomputed (cost metric)


class IncrementalPropagationEngine:
    """
    Incremental confidence propagation with dirty-tracking.
    
    Only recomputes nodes whose inputs have changed.
    Uses topological ordering to ensure parents are computed before children.
    
    Performance:
      Old (full): O(N) every time, even if 1 node changed
      New (incr): O(k) where k = size of affected subgraph
      
    Typical case: 1 service degrades → 2-5 dependents affected, not all 9+
    """
    
    DECAY_RATE = 0.95
    DEFAULT_EDGE_WEIGHT = 0.8
    
    def __init__(self):
        self.nodes: Dict[str, IncrementalNode] = {}
        self._computation_log: List[Dict] = []
        self._total_computations_saved: int = 0
        self._cache: Dict[str, float] = {}  # Memoization cache
        self._cache_hits: int = 0
        self._epoch: int = 0  # Incremented on topology change
        self._load_topology()
    
    def _load_topology(self):
        """Load topology from canonical registry."""
        from backend.runtime.service_registry import CANONICAL_REGISTRY
        for svc_id, svc in CANONICAL_REGISTRY.items():
            node = IncrementalNode(service=svc_id)
            for dep_id in svc.depends_on:
                node.parents[dep_id] = self.DEFAULT_EDGE_WEIGHT
            self.nodes[svc_id] = node
        for svc_id, node in self.nodes.items():
            for parent_id in node.parents:
                if parent_id in self.nodes:
                    self.nodes[parent_id].children.append(svc_id)
    
    def set_confidence(self, service: str, confidence: float):
        """
        Set local confidence and mark node + downstream as dirty.
        Does NOT propagate yet — just marks what needs recomputation.
        """
        if service not in self.nodes:
            self.nodes[service] = IncrementalNode(service=service)
        
        node = self.nodes[service]
        old = node.local_confidence
        node.local_confidence = max(0.0, min(1.0, confidence))
        
        if abs(old - node.local_confidence) > 0.001:
            self._mark_dirty_downstream(service)
    
    def _mark_dirty_downstream(self, service: str):
        """Mark a node and all its transitive children as dirty."""
        queue = deque([service])
        marked = set()
        
        while queue:
            svc = queue.popleft()
            if svc in marked:
                continue
            marked.add(svc)
            
            node = self.nodes.get(svc)
            if node:
                node.dirty = True
                for child in node.children:
                    if child not in marked:
                        queue.append(child)
        
        return len(marked)
    
    def propagate_incremental(self) -> Dict[str, float]:
        """
        Incremental propagation: only recompute dirty nodes.
        
        1. Find all dirty nodes
        2. Order them topologically (parents before children)
        3. Recompute only dirty nodes
        4. Clear dirty flags
        
        Returns {service: effective_confidence}.
        """
        start = time.time()
        
        # Find dirty nodes
        dirty_nodes = {svc for svc, n in self.nodes.items() if n.dirty}
        
        if not dirty_nodes:
            return {svc: n.effective_confidence for svc, n in self.nodes.items()}
        
        # Topological sort: parents come before children
        ordered = self._topological_sort(dirty_nodes)
        
        # Recompute only dirty nodes
        recomputed = 0
        for svc in ordered:
            node = self.nodes.get(svc)
            if not node or not node.dirty:
                continue
            
            self._recompute_node(node)
            node.dirty = False
            node.version += 1
            node.last_computed_at = time.time()
            node.computation_count += 1
            recomputed += 1
        
        # Log performance
        total_nodes = len(self.nodes)
        saved = total_nodes - recomputed
        self._total_computations_saved += saved
        
        self._computation_log.append({
            "timestamp": time.time(),
            "dirty_nodes": len(dirty_nodes),
            "recomputed": recomputed,
            "skipped": saved,
            "total_nodes": total_nodes,
            "savings_pct": round(saved / max(1, total_nodes) * 100, 1),
            "duration_ms": round((time.time() - start) * 1000, 1),
        })
        
        return {svc: n.effective_confidence for svc, n in self.nodes.items()}
    
    def _topological_sort(self, dirty: Set[str]) -> List[str]:
        """
        Topological sort of dirty nodes.
        Parents must be computed before children.
        Uses Kahn's algorithm on the subgraph.
        """
        # Build subgraph in-degree map
        in_degree = {}
        subgraph = {}
        
        for svc in dirty:
            node = self.nodes.get(svc)
            if not node:
                continue
            subgraph[svc] = [c for c in node.children if c in dirty]
            if svc not in in_degree:
                in_degree[svc] = 0
        
        for svc, children in subgraph.items():
            for child in children:
                in_degree[child] = in_degree.get(child, 0) + 1
        
        # Kahn's algorithm
        queue = deque([svc for svc, deg in in_degree.items() if deg == 0])
        result = []
        
        while queue:
            svc = queue.popleft()
            result.append(svc)
            for child in subgraph.get(svc, []):
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    queue.append(child)
        
        # Any remaining nodes have cycles — just append them
        for svc in dirty:
            if svc not in result:
                result.append(svc)
        
        return result
    
    def _recompute_node(self, node: IncrementalNode):
        """Recompute effective confidence with memoization."""
        # Build cache key: (local, parent versions, epoch)
        parent_versions = tuple(
            (pid, self.nodes[pid].version if pid in self.nodes else 0)
            for pid in sorted(node.parents.keys())
        )
        cache_key = f"{node.service}:{node.local_confidence:.4f}:{parent_versions}:{self._epoch}"
        
        if cache_key in self._cache:
            node.effective_confidence = self._cache[cache_key]
            self._cache_hits += 1
            return
        
        parent_product = 1.0
        for parent_id, edge_weight in node.parents.items():
            parent_node = self.nodes.get(parent_id)
            if parent_node:
                temporal = self.DECAY_RATE ** ((time.time() - parent_node.last_computed_at) / 3600)
                contribution = parent_node.effective_confidence * edge_weight * temporal
                parent_product *= max(0.3, contribution)
        
        result = round(node.local_confidence * parent_product, 2)
        self._cache[cache_key] = result
        node.effective_confidence = result
    
    def propagate_full(self) -> Dict[str, float]:
        """Full propagation (fallback). Use only when topology changes."""
        for node in self.nodes.values():
            node.dirty = True
        return self.propagate_incremental()
    
    def stats(self) -> Dict:
        """Performance statistics."""
        total = sum(n.computation_count for n in self.nodes.values())
        
        return {
            "total_propagations": len(self._computation_log),
            "total_computations_saved": self._total_computations_saved,
            "cache_hits": self._cache_hits,
            "cache_size": len(self._cache),
            "average_savings_pct": round(
                sum(l["savings_pct"] for l in self._computation_log) / max(1, len(self._computation_log)), 1
            ),
            "per_node_computations": {
                svc: n.computation_count
                for svc, n in sorted(self.nodes.items(), key=lambda x: -x[1].computation_count)
            },
            "most_recomputed": max(
                self.nodes.values(), key=lambda n: n.computation_count
            ).service if self.nodes else "none",
        }
