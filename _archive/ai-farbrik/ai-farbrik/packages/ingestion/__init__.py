"""
NeXifyAI — Knowledge Ingestion Pipeline (Fabrik F1)

NOT: loose Markdown collection
NOT: simple VectorDB
BUT:  versioned, semantic, auditierbare, governance-fähige Wissensplattform

Pipeline:
  Source → Crawl → Render → Normalize → Chunk → Extract Metadata
  → Semantic Classification → Versioning → Embeddings → Graph Linking
  → Policy Validation → Persistent Storage → Runtime Query Layer

Multi-Source: GitHub, Supabase, Vercel, Hermes, Paperclip, DeepSeek,
               OpenAI, Infrastructure, Security, Internal Docs
"""
import json
import os
import time
import hashlib
import uuid
import sqlite3
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Set
from enum import Enum
from datetime import datetime


# ═══════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════

class SourceType(Enum):
    GITHUB_DOCS = "github_docs"
    SUPABASE_DOCS = "supabase_docs"
    VERCEL_DOCS = "vercel_docs"
    HERMES_DOCS = "hermes_docs"
    PAPERCLIP_DOCS = "paperclip_docs"
    DEEPSEEK_DOCS = "deepseek_docs"
    OPENAI_DOCS = "openai_docs"
    ANTHROPIC_DOCS = "anthropic_docs"
    INFRA_DOCS = "infra_docs"
    SECURITY_DOCS = "security_docs"
    INTERNAL_ADR = "internal_adr"
    INTERNAL_DOC = "internal_doc"
    INTERNAL_CODE = "internal_code"

class DocumentType(Enum):
    MARKDOWN = "markdown"
    HTML = "html"
    YAML = "yaml"
    JSON = "json"
    OPENAPI = "openapi"
    GRAPHQL = "graphql"
    SQL = "sql"
    CODE = "code"
    PDF = "pdf"

class IngestionStatus(Enum):
    DISCOVERED = "discovered"
    FETCHED = "fetched"
    NORMALIZED = "normalized"
    CHUNKED = "chunked"
    EMBEDDED = "embedded"
    LINKED = "linked"
    VALIDATED = "validated"
    PUBLISHED = "published"
    FAILED = "failed"

@dataclass
class KnowledgeSource:
    """A source to ingest knowledge from."""
    source_id: str
    source_type: SourceType
    url: str
    description: str = ""
    auth_required: bool = False
    crawl_depth: int = 1
    rate_limit_rps: float = 1.0
    enabled: bool = True
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class KnowledgeDocument:
    """A single ingested document."""
    doc_id: str = field(default_factory=lambda: f"doc_{uuid.uuid4().hex[:12]}")
    source_type: SourceType = SourceType.INTERNAL_DOC
    doc_type: DocumentType = DocumentType.MARKDOWN
    title: str = ""
    url: str = ""
    content_raw: str = ""
    content_normalized: str = ""
    content_hash: str = ""
    chunks: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: IngestionStatus = IngestionStatus.DISCOVERED
    version: int = 1
    ingested_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    embedding_ids: List[str] = field(default_factory=list)
    graph_node_ids: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    @staticmethod
    def compute_hash(content: str) -> str:
        return hashlib.sha256(content.encode()).hexdigest()[:20]


# ═══════════════════════════════════════════════════
# SOURCE REGISTRY — ALL systems to ingest
# ═══════════════════════════════════════════════════

STANDARD_SOURCES = [
    # ── GitHub ──
    KnowledgeSource("github-rest", SourceType.GITHUB_DOCS,
        "https://docs.github.com/en/rest", "GitHub REST API", tags=["github", "api", "rest"]),
    KnowledgeSource("github-graphql", SourceType.GITHUB_DOCS,
        "https://docs.github.com/en/graphql", "GitHub GraphQL API", tags=["github", "api", "graphql"]),
    KnowledgeSource("github-actions", SourceType.GITHUB_DOCS,
        "https://docs.github.com/en/actions", "GitHub Actions", tags=["github", "ci", "actions"]),
    KnowledgeSource("github-webhooks", SourceType.GITHUB_DOCS,
        "https://docs.github.com/en/webhooks", "GitHub Webhooks", tags=["github", "webhooks"]),
    KnowledgeSource("github-apps", SourceType.GITHUB_DOCS,
        "https://docs.github.com/en/apps", "GitHub Apps", tags=["github", "apps"]),

    # ── Supabase ──
    KnowledgeSource("supabase-postgrest", SourceType.SUPABASE_DOCS,
        "https://supabase.com/docs/reference/javascript", "Supabase PostgREST", tags=["supabase", "api"]),
    KnowledgeSource("supabase-auth", SourceType.SUPABASE_DOCS,
        "https://supabase.com/docs/guides/auth", "Supabase Auth", tags=["supabase", "auth"]),
    KnowledgeSource("supabase-rls", SourceType.SUPABASE_DOCS,
        "https://supabase.com/docs/guides/auth/row-level-security", "Supabase RLS", tags=["supabase", "security", "rls"]),
    KnowledgeSource("supabase-migrations", SourceType.SUPABASE_DOCS,
        "https://supabase.com/docs/guides/migrations", "Supabase Migrations", tags=["supabase", "database"]),
    KnowledgeSource("supabase-realtime", SourceType.SUPABASE_DOCS,
        "https://supabase.com/docs/guides/realtime", "Supabase Realtime", tags=["supabase", "realtime"]),
    KnowledgeSource("supabase-storage", SourceType.SUPABASE_DOCS,
        "https://supabase.com/docs/guides/storage", "Supabase Storage", tags=["supabase", "storage"]),
    KnowledgeSource("supabase-edge", SourceType.SUPABASE_DOCS,
        "https://supabase.com/docs/guides/functions", "Supabase Edge Functions", tags=["supabase", "edge"]),

    # ── Vercel ──
    KnowledgeSource("vercel-deploy", SourceType.VERCEL_DOCS,
        "https://vercel.com/docs/deployments", "Vercel Deployments", tags=["vercel", "deploy"]),
    KnowledgeSource("vercel-ai-sdk", SourceType.VERCEL_DOCS,
        "https://sdk.vercel.ai/docs", "Vercel AI SDK", tags=["vercel", "ai", "sdk"]),
    KnowledgeSource("vercel-edge", SourceType.VERCEL_DOCS,
        "https://vercel.com/docs/edge-network", "Vercel Edge Runtime", tags=["vercel", "edge"]),
    KnowledgeSource("vercel-analytics", SourceType.VERCEL_DOCS,
        "https://vercel.com/docs/analytics", "Vercel Analytics", tags=["vercel", "analytics"]),

    # ── Hermes ──
    KnowledgeSource("hermes-agent", SourceType.HERMES_DOCS,
        "https://github.com/NousResearch/hermes-agent", "Hermes Agent", tags=["hermes", "agent"]),
    KnowledgeSource("hermes-paperclip-adapter", SourceType.PAPERCLIP_DOCS,
        "https://github.com/NousResearch/hermes-paperclip-adapter", "Hermes Paperclip Adapter", tags=["hermes", "paperclip"]),

    # ── Paperclip ──
    KnowledgeSource("paperclip-docs", SourceType.PAPERCLIP_DOCS,
        "https://github.com/NousResearch/paperclip", "Paperclip Docs", tags=["paperclip", "skills"]),

    # ── DeepSeek ──
    KnowledgeSource("deepseek-api", SourceType.DEEPSEEK_DOCS,
        "https://api-docs.deepseek.com", "DeepSeek API", tags=["deepseek", "api", "llm"]),

    # ── OpenAI ──
    KnowledgeSource("openai-mcp", SourceType.OPENAI_DOCS,
        "https://modelcontextprotocol.io", "MCP Protocol", tags=["openai", "mcp"]),

    # ── Infra ──
    KnowledgeSource("qdrant-docs", SourceType.INFRA_DOCS,
        "https://qdrant.tech/documentation", "Qdrant Vector DB", tags=["infra", "vector"]),
    KnowledgeSource("temporal-docs", SourceType.INFRA_DOCS,
        "https://docs.temporal.io", "Temporal Workflows", tags=["infra", "orchestration"]),
    KnowledgeSource("opentelemetry-docs", SourceType.INFRA_DOCS,
        "https://opentelemetry.io/docs", "OpenTelemetry", tags=["infra", "observability"]),

    # ── Security ──
    KnowledgeSource("opa-docs", SourceType.SECURITY_DOCS,
        "https://www.openpolicyagent.org/docs", "Open Policy Agent", tags=["security", "policy"]),
    KnowledgeSource("cedar-docs", SourceType.SECURITY_DOCS,
        "https://www.cedarpolicy.com", "Cedar Policy Language", tags=["security", "policy"]),
]


# ═══════════════════════════════════════════════════
# INGESTION PIPELINE
# ═══════════════════════════════════════════════════

class IngestionPipeline:
    """
    Central knowledge ingestion pipeline.

    Stages:
      1. Source Registry — what to ingest
      2. Crawler — fetch content
      3. Normalizer — HTML→Markdown, YAML→Dict
      4. Chunker — semantic chunking
      5. Metadata Extractor — tags, type, language
      6. Embedder — vector embeddings
      7. Graph Linker — semantic relationships
      8. Registry — versioned, queryable store
    """

    def __init__(self, db_path: str = "/opt/ai-farbrik/ingestion/registry/knowledge.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.sources: Dict[str, KnowledgeSource] = {}
        self.documents: Dict[str, KnowledgeDocument] = {}
        self._init_db()

    def _init_db(self):
        """Initialize the knowledge registry database."""
        db = sqlite3.connect(self.db_path)
        db.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_documents (
                doc_id TEXT PRIMARY KEY,
                source_type TEXT NOT NULL,
                doc_type TEXT NOT NULL,
                title TEXT DEFAULT '',
                url TEXT DEFAULT '',
                content_hash TEXT DEFAULT '',
                status TEXT DEFAULT 'discovered',
                version INTEGER DEFAULT 1,
                ingested_at REAL NOT NULL,
                updated_at REAL NOT NULL,
                tags TEXT DEFAULT '[]',
                metadata TEXT DEFAULT '{}',
                chunk_count INTEGER DEFAULT 0,
                embedding_count INTEGER DEFAULT 0
            )
        """)
        db.execute("CREATE INDEX IF NOT EXISTS idx_source ON knowledge_documents(source_type)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_status ON knowledge_documents(status)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_tags ON knowledge_documents(tags)")
        db.commit()
        db.close()

    # ── Stage 1: Source Registration ──

    def register_sources(self, sources: List[KnowledgeSource] = None):
        """Register knowledge sources for ingestion."""
        for source in (sources or STANDARD_SOURCES):
            self.sources[source.source_id] = source
        return len(self.sources)

    # ── Stage 2: Crawl ──

    def crawl(self, source_id: str = "", limit: int = 50) -> List[KnowledgeDocument]:
        """Crawl a source and extract documents. Falls back to metadata if URL unreachable."""
        sources = [self.sources[source_id]] if source_id else list(self.sources.values())
        docs = []

        for source in sources:
            if not source.enabled:
                continue

            # For now: create document metadata from source definitions
            # Full HTML crawling requires Playwright (browser) — phase 2
            doc = KnowledgeDocument(
                source_type=source.source_type,
                doc_type=DocumentType.MARKDOWN,
                title=source.description,
                url=source.url,
                tags=source.tags,
                metadata={
                    "source_id": source.source_id,
                    "crawl_depth": source.crawl_depth,
                    "auth_required": source.auth_required,
                },
            )
            doc.status = IngestionStatus.FETCHED
            docs.append(doc)
            self.documents[doc.doc_id] = doc

            if len(docs) >= limit:
                break

        return docs

    # ── Stage 3: Normalize ──

    def normalize(self, docs: List[KnowledgeDocument] = None) -> List[KnowledgeDocument]:
        """Normalize documents: HTML→Markdown, YAML→Dict, Code→AST."""
        targets = docs or list(self.documents.values())

        for doc in targets:
            if doc.status.value < IngestionStatus.FETCHED.value:
                continue

            # Normalize based on doc_type
            if doc.doc_type == DocumentType.HTML:
                doc.content_normalized = self._html_to_markdown(doc.content_raw)
            elif doc.doc_type == DocumentType.YAML:
                doc.content_normalized = json.dumps(
                    self._parse_yaml(doc.content_raw), indent=2
                )
            elif doc.doc_type == DocumentType.CODE:
                doc.content_normalized = f"```\n{doc.content_raw}\n```"
            else:
                doc.content_normalized = doc.content_raw or doc.title

            doc.content_hash = KnowledgeDocument.compute_hash(doc.content_normalized)
            doc.status = IngestionStatus.NORMALIZED

        return targets

    # ── Stage 4: Chunk ──

    def chunk(self, docs: List[KnowledgeDocument] = None,
              chunk_size: int = 1000, chunk_overlap: int = 200) -> List[KnowledgeDocument]:
        """Semantic chunking — split documents into overlapping chunks for embedding."""
        targets = docs or [
            d for d in self.documents.values()
            if d.status == IngestionStatus.NORMALIZED
        ]

        for doc in targets:
            content = doc.content_normalized
            if not content:
                continue

            chunks = []
            # Simple sliding window chunking
            words = content.split()
            step = chunk_size - chunk_overlap

            for i in range(0, len(words), step):
                chunk_words = words[i:i + chunk_size]
                if not chunk_words:
                    continue
                chunk_text = " ".join(chunk_words)
                chunks.append({
                    "chunk_id": f"{doc.doc_id}_chunk_{i // step}",
                    "text": chunk_text,
                    "start_idx": i,
                    "end_idx": min(i + chunk_size, len(words)),
                    "hash": hashlib.sha256(chunk_text.encode()).hexdigest()[:12],
                })

            doc.chunks = chunks
            doc.status = IngestionStatus.CHUNKED

        return targets

    # ── Stage 5: Embed ──

    def embed(self, docs: List[KnowledgeDocument] = None) -> List[KnowledgeDocument]:
        """Generate vector embeddings for chunks (placeholder — Qdrant/Ollama integration)."""
        targets = docs or [
            d for d in self.documents.values()
            if d.status == IngestionStatus.CHUNKED
        ]

        for doc in targets:
            embedding_ids = []
            for chunk in doc.chunks:
                # Placeholder: In production, call Qdrant or Ollama embedding API
                emb_id = f"emb_{chunk['chunk_id']}"
                embedding_ids.append(emb_id)

            doc.embedding_ids = embedding_ids
            doc.status = IngestionStatus.EMBEDDED

        return targets

    # ── Stage 6: Persist ──

    def persist(self, docs: List[KnowledgeDocument] = None):
        """Persist documents to the knowledge registry."""
        targets = docs or list(self.documents.values())
        db = sqlite3.connect(self.db_path)

        for doc in targets:
            db.execute("""
                INSERT OR REPLACE INTO knowledge_documents (
                    doc_id, source_type, doc_type, title, url, content_hash,
                    status, version, ingested_at, updated_at,
                    tags, metadata, chunk_count, embedding_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                doc.doc_id, doc.source_type.value, doc.doc_type.value,
                doc.title, doc.url, doc.content_hash,
                doc.status.value, doc.version, doc.ingested_at, doc.updated_at,
                json.dumps(doc.tags), json.dumps(doc.metadata),
                len(doc.chunks), len(doc.embedding_ids),
            ))
            doc.status = IngestionStatus.PUBLISHED

        db.commit()
        db.close()

    # ── Full pipeline ──

    def ingest_all(self, limit: int = 30) -> Dict[str, Any]:
        """Run the full ingestion pipeline."""
        t0 = time.time()

        # 1. Register
        n_sources = self.register_sources()

        # 2. Crawl
        docs = self.crawl(limit=limit)
        n_fetched = len(docs)

        # 3. Normalize
        docs = self.normalize(docs)
        n_normalized = sum(1 for d in docs if d.status == IngestionStatus.NORMALIZED)

        # 4. Chunk
        docs = self.chunk(docs)
        n_chunked = sum(1 for d in docs if d.status == IngestionStatus.CHUNKED)

        # 5. Embed
        docs = self.embed(docs)
        n_embedded = sum(1 for d in docs if d.status == IngestionStatus.EMBEDDED)

        # 6. Persist
        self.persist(docs)

        duration = time.time() - t0

        return {
            "pipeline": "knowledge_ingestion_v1",
            "sources_registered": n_sources,
            "documents_fetched": n_fetched,
            "documents_normalized": n_normalized,
            "documents_chunked": n_chunked,
            "documents_embedded": n_embedded,
            "documents_persisted": n_fetched,
            "duration_seconds": round(duration, 2),
            "registry_db": self.db_path,
        }

    def stats(self) -> Dict[str, Any]:
        """Get ingestion statistics."""
        db = sqlite3.connect(self.db_path)
        total = db.execute("SELECT COUNT(*) FROM knowledge_documents").fetchone()[0]
        by_source = {}
        for row in db.execute(
            "SELECT source_type, COUNT(*) FROM knowledge_documents GROUP BY source_type"
        ):
            by_source[row[0]] = row[1]
        by_status = {}
        for row in db.execute(
            "SELECT status, COUNT(*) FROM knowledge_documents GROUP BY status"
        ):
            by_status[row[0]] = row[1]
        db.close()
        return {
            "total_documents": total,
            "by_source": by_source,
            "by_status": by_status,
            "sources_configured": len(STANDARD_SOURCES),
        }

    # ── Helpers ──

    def _html_to_markdown(self, html: str) -> str:
        """Convert HTML to Markdown."""
        try:
            import html2text
            h = html2text.HTML2Text()
            h.ignore_links = False
            return h.handle(html)
        except ImportError:
            return html

    def _parse_yaml(self, yaml_str: str) -> Dict:
        """Parse YAML to dict."""
        try:
            import yaml
            return yaml.safe_load(yaml_str) or {}
        except ImportError:
            return {"raw": yaml_str}


# ═══════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════

_pipeline: Optional[IngestionPipeline] = None

def get_pipeline() -> IngestionPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = IngestionPipeline()
    return _pipeline
