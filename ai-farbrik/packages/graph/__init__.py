"""
NeXifyAI — Knowledge Graph Backbone (Fabrik F2)

NOT: vector similarity only
BUT:  causal + operational semantic relationships

Relationship types:
  Skill → uses_connector → Connector
  Skill → requires_capability → CapabilityToken
  Skill → emits_event → EventType
  Skill → governed_by → Policy
  Skill → documented_in → KnowledgeDocument
  Skill → compensated_by → CompensationAction
  Skill → affects_resource → Resource

  Agent → executes_skill → Skill
  Agent → bound_by → CapabilityToken
  Agent → produces → Artifact

  Event → caused_by → Event
  Event → correlates_with → CorrelationGroup
  Event → triggers_compensation → CompensationAction

  Document → references → Document
  Document → defines → Skill/Policy/Event

This becomes the REASONING BACKBONE for the entire AI Fabrik.
"""
import json
import os
import sqlite3
import uuid
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
from collections import defaultdict


# ═══════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════

class NodeType(Enum):
    SKILL = "skill"
    CONNECTOR = "connector"
    CAPABILITY = "capability"
    EVENT = "event"
    POLICY = "policy"
    AGENT = "agent"
    DOCUMENT = "document"
    ARTIFACT = "artifact"
    COMPENSATION = "compensation"
    RESOURCE = "resource"
    RISK = "risk"
    SYSTEM = "system"

class RelationshipType(Enum):
    USES_CONNECTOR = "uses_connector"
    REQUIRES_CAPABILITY = "requires_capability"
    EMITS_EVENT = "emits_event"
    GOVERNED_BY = "governed_by"
    DOCUMENTED_IN = "documented_in"
    COMPENSATED_BY = "compensated_by"
    AFFECTS_RESOURCE = "affects_resource"
    EXECUTES_SKILL = "executes_skill"
    BOUND_BY = "bound_by"
    PRODUCES = "produces"
    CAUSED_BY = "caused_by"
    CORRELATES_WITH = "correlates_with"
    REFERENCES = "references"
    DEFINES = "defines"
    DEPENDS_ON = "depends_on"
    CONFLICTS_WITH = "conflicts_with"
    REPLACES = "replaces"

@dataclass
class GraphNode:
    """A node in the knowledge graph."""
    node_id: str
    node_type: NodeType
    label: str
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

@dataclass
class GraphEdge:
    """A directed relationship between two nodes."""
    edge_id: str = field(default_factory=lambda: f"edge_{uuid.uuid4().hex[:12]}")
    source_id: str = ""
    target_id: str = ""
    relationship: RelationshipType = RelationshipType.REFERENCES
    weight: float = 1.0
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)


# ═══════════════════════════════════════════════════
# KNOWLEDGE GRAPH
# ═══════════════════════════════════════════════════

class KnowledgeGraph:
    """
    Semantic knowledge graph — causal + operational relationships.

    Stores: nodes (typed entities), edges (directed relationships)
    Queries: traverse, find paths, discover dependencies, detect conflicts
    """

    def __init__(self, db_path: str = "/opt/ai-farbrik/ingestion/graph/knowledge_graph.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._nodes: Dict[str, GraphNode] = {}
        self._edges: List[GraphEdge] = []
        self._adjacency: Dict[str, List[Tuple[str, RelationshipType]]] = defaultdict(list)
        self._init_db()

    def _init_db(self):
        """Initialize the graph database."""
        db = sqlite3.connect(self.db_path)
        db.execute("""
            CREATE TABLE IF NOT EXISTS graph_nodes (
                node_id TEXT PRIMARY KEY,
                node_type TEXT NOT NULL,
                label TEXT NOT NULL,
                properties TEXT DEFAULT '{}',
                created_at REAL NOT NULL
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS graph_edges (
                edge_id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                relationship TEXT NOT NULL,
                weight REAL DEFAULT 1.0,
                properties TEXT DEFAULT '{}',
                created_at REAL NOT NULL
            )
        """)
        db.execute("CREATE INDEX IF NOT EXISTS idx_edges_source ON graph_edges(source_id)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_edges_target ON graph_edges(target_id)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_edges_rel ON graph_edges(relationship)")
        db.commit()
        db.close()

    # ── Node operations ──

    def add_node(self, node: GraphNode) -> GraphNode:
        """Add or update a node."""
        self._nodes[node.node_id] = node
        db = sqlite3.connect(self.db_path)
        db.execute("""
            INSERT OR REPLACE INTO graph_nodes (node_id, node_type, label, properties, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (node.node_id, node.node_type.value, node.label,
              json.dumps(node.properties), node.created_at))
        db.commit()
        db.close()
        return node

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Get a node by ID."""
        return self._nodes.get(node_id)

    def find_nodes(self, node_type: NodeType = None,
                   label_contains: str = "") -> List[GraphNode]:
        """Find nodes by type and/or label."""
        results = []
        for node in self._nodes.values():
            if node_type and node.node_type != node_type:
                continue
            if label_contains and label_contains.lower() not in node.label.lower():
                continue
            results.append(node)
        return results

    # ── Edge operations ──

    def add_edge(self, edge: GraphEdge) -> GraphEdge:
        """Add a relationship between two nodes."""
        self._edges.append(edge)
        self._adjacency[edge.source_id].append((edge.target_id, edge.relationship))
        self._adjacency[edge.target_id].append((edge.source_id, edge.relationship))

        db = sqlite3.connect(self.db_path)
        db.execute("""
            INSERT OR REPLACE INTO graph_edges (edge_id, source_id, target_id, relationship, weight, properties, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (edge.edge_id, edge.source_id, edge.target_id, edge.relationship.value,
              edge.weight, json.dumps(edge.properties), edge.created_at))
        db.commit()
        db.close()
        return edge

    def add_relationship(self, source: GraphNode, target: GraphNode,
                        relationship: RelationshipType,
                        weight: float = 1.0) -> GraphEdge:
        """Convenience: add a relationship between two existing nodes."""
        edge = GraphEdge(
            source_id=source.node_id,
            target_id=target.node_id,
            relationship=relationship,
            weight=weight,
        )
        return self.add_edge(edge)

    # ── Traversal ──

    def get_neighbors(self, node_id: str,
                      relationship: RelationshipType = None) -> List[Tuple[str, RelationshipType]]:
        """Get all neighbors of a node, optionally filtered by relationship type."""
        neighbors = self._adjacency.get(node_id, [])
        if relationship:
            neighbors = [(nid, rel) for nid, rel in neighbors if rel == relationship]
        return neighbors

    def traverse(self, start_id: str, max_depth: int = 3) -> Dict[str, Any]:
        """BFS traversal from a starting node, returning the subgraph."""
        visited = set()
        queue = [(start_id, 0)]
        subgraph_nodes = []
        subgraph_edges = []

        while queue:
            current, depth = queue.pop(0)
            if current in visited or depth > max_depth:
                continue
            visited.add(current)

            node = self._nodes.get(current)
            if node:
                subgraph_nodes.append(node)

            for neighbor_id, rel in self._adjacency.get(current, []):
                if neighbor_id not in visited:
                    queue.append((neighbor_id, depth + 1))
                    subgraph_edges.append({
                        "source": current,
                        "target": neighbor_id,
                        "relationship": rel.value,
                    })

        return {
            "start_node": start_id,
            "max_depth": max_depth,
            "nodes_found": len(subgraph_nodes),
            "edges_found": len(subgraph_edges),
            "nodes": [{"id": n.node_id, "type": n.node_type.value, "label": n.label}
                      for n in subgraph_nodes],
            "edges": subgraph_edges,
        }

    def find_paths(self, from_id: str, to_id: str,
                   max_depth: int = 5) -> List[List[Dict]]:
        """Find all paths between two nodes up to max_depth."""
        paths = []
        visited = set()

        def dfs(current, target, path, depth):
            if depth > max_depth or current in visited:
                return
            if current == target:
                paths.append(list(path))
                return

            visited.add(current)
            for neighbor_id, rel in self._adjacency.get(current, []):
                path.append({"node": neighbor_id, "relationship": rel.value})
                dfs(neighbor_id, target, path, depth + 1)
                path.pop()
            visited.remove(current)

        dfs(from_id, to_id, [], 0)
        return paths

    # ── Statistics ──

    def stats(self) -> Dict[str, Any]:
        """Get graph statistics."""
        node_types = defaultdict(int)
        for node in self._nodes.values():
            node_types[node.node_type.value] += 1

        edge_types = defaultdict(int)
        for edge in self._edges:
            edge_types[edge.relationship.value] += 1

        return {
            "total_nodes": len(self._nodes),
            "total_edges": len(self._edges),
            "node_types": dict(node_types),
            "edge_types": dict(edge_types),
            "density": len(self._edges) / max(1, len(self._nodes) * (len(self._nodes) - 1)),
        }


# ═══════════════════════════════════════════════════
# GRAPH BUILDER — auto-populate from Fabrik packages
# ═══════════════════════════════════════════════════

class GraphBuilder:
    """
    Auto-build the knowledge graph from Fabrik package definitions.

    Reads: skill manifests, event contracts, governance policies, ingestion registry
    Produces: fully linked semantic graph
    """

    def __init__(self, graph: KnowledgeGraph = None):
        self.graph = graph or KnowledgeGraph()

    def build_from_skill_manifest(self, manifest) -> List[GraphNode]:
        """Build graph nodes and edges from a SkillManifest."""
        # Skill node
        skill_node = self.graph.add_node(GraphNode(
            node_id=f"skill:{manifest.skill_id}",
            node_type=NodeType.SKILL,
            label=manifest.skill_id,
            properties={
                "version": manifest.version,
                "description": manifest.description,
                "risk_level": manifest.risk_level.value,
                "blast_radius": manifest.blast_radius,
            }
        ))

        nodes = [skill_node]

        # Capability nodes + edges
        for cap in manifest.capabilities:
            cap_node = self.graph.add_node(GraphNode(
                node_id=f"capability:{cap.name}",
                node_type=NodeType.CAPABILITY,
                label=cap.name,
                properties={"scope": cap.scope},
            ))
            nodes.append(cap_node)
            self.graph.add_relationship(skill_node, cap_node,
                                        RelationshipType.REQUIRES_CAPABILITY)

        # Connector node + edge
        if manifest.connector:
            conn_node = self.graph.add_node(GraphNode(
                node_id=f"connector:{manifest.connector}",
                node_type=NodeType.CONNECTOR,
                label=manifest.connector,
            ))
            nodes.append(conn_node)
            self.graph.add_relationship(skill_node, conn_node,
                                        RelationshipType.USES_CONNECTOR)

        # Compensation node + edge
        if manifest.compensation:
            comp_node = self.graph.add_node(GraphNode(
                node_id=f"compensation:{manifest.compensation.action}",
                node_type=NodeType.COMPENSATION,
                label=manifest.compensation.action,
            ))
            nodes.append(comp_node)
            self.graph.add_relationship(skill_node, comp_node,
                                        RelationshipType.COMPENSATED_BY)

        return nodes

    def build_from_sources(self, sources: List) -> List[GraphNode]:
        """Build graph nodes from knowledge sources."""
        nodes = []
        for source in sources:
            src_node = self.graph.add_node(GraphNode(
                node_id=f"source:{source.source_id}",
                node_type=NodeType.DOCUMENT,
                label=source.description,
                properties={"url": source.url, "source_type": source.source_type.value},
            ))
            nodes.append(src_node)
        return nodes

    def build_all(self) -> KnowledgeGraph:
        """Build the complete knowledge graph from all Fabrik components."""
        # Import manifests and sources
        try:
            from skill_runtime import STANDARD_SKILLS
            for skill in STANDARD_SKILLS.values():
                self.build_from_skill_manifest(skill)
        except ImportError:
            pass

        try:
            from ingestion import STANDARD_SOURCES
            self.build_from_sources(STANDARD_SOURCES)
        except ImportError:
            pass

        # Add System nodes for each connector
        for conn in ["github", "vercel", "supabase", "browser", "slack", "sandbox"]:
            self.graph.add_node(GraphNode(
                node_id=f"system:{conn}",
                node_type=NodeType.SYSTEM,
                label=conn,
            ))

        # Add Governance nodes
        for policy in ["no_stripe", "no_gpl_agpl_sspl", "rls_required", "blast_cap"]:
            self.graph.add_node(GraphNode(
                node_id=f"policy:{policy}",
                node_type=NodeType.POLICY,
                label=policy,
            ))

        return self.graph


# ═══════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════

_graph: Optional[KnowledgeGraph] = None

def get_graph() -> KnowledgeGraph:
    global _graph
    if _graph is None:
        _graph = KnowledgeGraph()
        builder = GraphBuilder(_graph)
        builder.build_all()
    return _graph
