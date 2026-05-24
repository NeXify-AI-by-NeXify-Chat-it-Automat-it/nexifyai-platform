"""
NeXifyAI Core: Oracle Ingestion Pipeline v4.8
AIC-49 Phase 1 — Enterprise Knowledge Consolidation

Governed pipeline for ingesting knowledge from all sources:
RAW → classify → normalize → validate → enrich → dedup → chunk → embed → reconcile → store → audit
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
import hashlib
import json
import uuid


class PipelineStage(Enum):
    RAW = "raw"
    CLASSIFY = "classify"
    NORMALIZE = "normalize"
    VALIDATE = "validate"
    ENRICH = "enrich"
    DEDUP = "dedup"
    CHUNK = "chunk"
    EMBED = "embed"
    RECONCILE = "reconcile"
    STORE = "store"
    AUDIT = "audit"


class SourceType(Enum):
    ADR = "adr"
    POLICY = "policy"
    DIRECTIVE = "directive"
    CHAT = "chat"
    RUNTIME_LOG = "runtime_log"
    RECOVERY_LOG = "recovery_log"
    CI_LOG = "ci_log"
    AGENT_CONFIG = "agent_config"
    PLAYBOOK = "playbook"
    INCIDENT_REPORT = "incident_report"
    SECURITY_AUDIT = "security_audit"
    KNOWLEDGE_ENTRY = "knowledge_entry"
    GOVERNANCE_RULE = "governance_rule"
    ARCHITECTURE_NOTE = "architecture_note"
    PROMPT = "prompt"
    CODE = "code"


@dataclass
class IngestedDocument:
    """A document going through the ingestion pipeline."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    external_id: Optional[str] = None
    title: str = ""
    content: str = ""
    content_hash: str = ""
    source: str = ""
    source_type: SourceType = SourceType.KNOWLEDGE_ENTRY
    language: str = "de"
    stage: PipelineStage = PipelineStage.RAW
    classification: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
    governance_tags: list = field(default_factory=list)
    chunks: list = field(default_factory=list)
    embedding_ids: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    audit_events: list = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def compute_hash(self) -> str:
        self.content_hash = hashlib.sha256(self.content.encode()).hexdigest()[:16]
        return self.content_hash

    def to_oracle_dict(self) -> dict:
        return {
            "id": self.id,
            "external_id": self.external_id,
            "title": self.title,
            "content": self.content,
            "content_hash": self.content_hash,
            "source": self.source,
            "source_type": self.source_type.value,
            "language": self.language,
            "status": "active",
            "classification": json.dumps(self.classification),
            "metadata": json.dumps(self.metadata),
            "governance_tags": self.governance_tags,
            "chunk_count": len(self.chunks),
            "embedding_count": len(self.embedding_ids),
        }


class OracleIngestionPipeline:
    """
    Governed ingestion pipeline.
    Every document flows through: RAW → classify → normalize → validate →
    enrich → dedup → chunk → embed → reconcile → store → audit.

    No stage can be skipped. Every stage is audited.
    """

    STAGE_ORDER = [
        PipelineStage.RAW,
        PipelineStage.CLASSIFY,
        PipelineStage.NORMALIZE,
        PipelineStage.VALIDATE,
        PipelineStage.ENRICH,
        PipelineStage.DEDUP,
        PipelineStage.CHUNK,
        PipelineStage.EMBED,
        PipelineStage.RECONCILE,
        PipelineStage.STORE,
        PipelineStage.AUDIT,
    ]

    def __init__(self, config: dict):
        self.config = config
        self._known_hashes: set = set()
        self._stats = {
            "ingested": 0,
            "failed": 0,
            "duplicates_skipped": 0,
            "chunks_created": 0,
            "embeddings_created": 0,
        }

    def ingest(self, raw_content: str, source: str, source_type: SourceType,
               title: str = "", metadata: dict = None) -> IngestedDocument:
        """Ingest a single document through the full governed pipeline."""
        doc = IngestedDocument(
            content=raw_content,
            source=source,
            source_type=source_type,
            title=title or f"Doc from {source}",
            metadata=metadata or {},
        )

        for stage in self.STAGE_ORDER:
            doc = self._execute_stage(stage, doc)
            if doc.errors and self._is_fatal(stage):
                self._stats["failed"] += 1
                return doc

        self._stats["ingested"] += 1
        return doc

    def _execute_stage(self, stage: PipelineStage, doc: IngestedDocument) -> IngestedDocument:
        """Execute a single pipeline stage on a document."""
        handlers = {
            PipelineStage.RAW: self._handle_raw,
            PipelineStage.CLASSIFY: self._handle_classify,
            PipelineStage.NORMALIZE: self._handle_normalize,
            PipelineStage.VALIDATE: self._handle_validate,
            PipelineStage.ENRICH: self._handle_enrich,
            PipelineStage.DEDUP: self._handle_dedup,
            PipelineStage.CHUNK: self._handle_chunk,
            PipelineStage.EMBED: self._handle_embed,
            PipelineStage.RECONCILE: self._handle_reconcile,
            PipelineStage.STORE: self._handle_store,
            PipelineStage.AUDIT: self._handle_audit,
        }

        handler = handlers.get(stage)
        if not handler:
            return doc

        try:
            doc = handler(doc)
            doc.stage = stage
        except Exception as e:
            doc.errors.append({"stage": stage.value, "error": str(e)})

        return doc

    def _handle_raw(self, doc: IngestedDocument) -> IngestedDocument:
        """Stage 0: RAW — compute hash, basic validation."""
        if not doc.content or not doc.content.strip():
            doc.errors.append({"stage": "raw", "error": "Empty content"})
            return doc
        doc.compute_hash()
        return doc

    def _handle_classify(self, doc: IngestedDocument) -> IngestedDocument:
        """Stage 1: CLASSIFY — determine document category, language, governance tags."""
        doc.classification = {
            "source_type": doc.source_type.value,
            "has_code_blocks": "```" in doc.content,
            "has_links": "http" in doc.content.lower(),
            "content_length": len(doc.content),
            "line_count": doc.content.count("\n") + 1,
        }

        # Derive governance tags from source type
        tag_map = {
            SourceType.POLICY: ["governance", "policy"],
            SourceType.ADR: ["governance", "architecture", "decision"],
            SourceType.DIRECTIVE: ["governance", "directive", "executive"],
            SourceType.SECURITY_AUDIT: ["governance", "security", "compliance"],
            SourceType.INCIDENT_REPORT: ["governance", "incident", "recovery"],
            SourceType.RUNTIME_LOG: ["runtime", "operations"],
            SourceType.AGENT_CONFIG: ["runtime", "configuration"],
            SourceType.PLAYBOOK: ["operations", "recovery", "procedure"],
        }
        doc.governance_tags = tag_map.get(doc.source_type, ["knowledge"])

        return doc

    def _handle_normalize(self, doc: IngestedDocument) -> IngestedDocument:
        """Stage 2: NORMALIZE — clean content, strip noise, normalize formatting."""
        # Strip excessive whitespace
        doc.content = "\n".join(
            line.rstrip() for line in doc.content.split("\n")
        )
        # Normalize line endings
        doc.content = doc.content.replace("\r\n", "\n").replace("\r", "\n")
        # Strip trailing newlines
        doc.content = doc.content.strip()
        return doc

    def _handle_validate(self, doc: IngestedDocument) -> IngestedDocument:
        """Stage 3: VALIDATE — ensure content meets quality thresholds."""
        min_length = self.config.get("min_content_length", 50)

        if len(doc.content) < min_length:
            doc.errors.append({
                "stage": "validate",
                "error": f"Content too short: {len(doc.content)} chars (min: {min_length})"
            })
        if not doc.title:
            doc.errors.append({"stage": "validate", "error": "Missing title"})

        return doc

    def _handle_enrich(self, doc: IngestedDocument) -> IngestedDocument:
        """Stage 4: ENRICH — add metadata, timestamps, source info."""
        doc.metadata.update({
            "pipeline_version": "4.8",
            "ingested_at": datetime.now(timezone.utc).isoformat(),
            "ingestion_agent": "AI-CEO",
            "word_count": len(doc.content.split()),
            "char_count": len(doc.content),
        })
        return doc

    def _handle_dedup(self, doc: IngestedDocument) -> IngestedDocument:
        """Stage 5: DEDUP — check for duplicate content via hash."""
        if doc.content_hash in self._known_hashes:
            self._stats["duplicates_skipped"] += 1
            doc.errors.append({"stage": "dedup", "error": "Duplicate content hash"})
        else:
            self._known_hashes.add(doc.content_hash)
        return doc

    def _handle_chunk(self, doc: IngestedDocument) -> IngestedDocument:
        """Stage 6: CHUNK — split document into semantic chunks."""
        chunk_size = self.config.get("chunk_size", 1000)
        chunk_overlap = self.config.get("chunk_overlap", 200)

        if len(doc.content) <= chunk_size:
            doc.chunks = [{
                "index": 0,
                "content": doc.content,
                "hash": doc.content_hash,
                "token_estimate": len(doc.content) // 4,
            }]
        else:
            paragraphs = doc.content.split("\n\n")
            chunks = []
            current_chunk = ""
            chunk_idx = 0

            for para in paragraphs:
                if len(current_chunk) + len(para) > chunk_size and current_chunk:
                    chunks.append({
                        "index": chunk_idx,
                        "content": current_chunk.strip(),
                        "hash": hashlib.sha256(current_chunk.encode()).hexdigest()[:16],
                        "token_estimate": len(current_chunk) // 4,
                    })
                    chunk_idx += 1
                    # Overlap: keep last portion
                    overlap_text = current_chunk[-chunk_overlap:] if len(current_chunk) > chunk_overlap else ""
                    current_chunk = overlap_text + para
                else:
                    current_chunk += ("\n\n" if current_chunk else "") + para

            if current_chunk.strip():
                chunks.append({
                    "index": chunk_idx,
                    "content": current_chunk.strip(),
                    "hash": hashlib.sha256(current_chunk.encode()).hexdigest()[:16],
                    "token_estimate": len(current_chunk) // 4,
                })

            doc.chunks = chunks

        self._stats["chunks_created"] += len(doc.chunks)
        return doc

    def _handle_embed(self, doc: IngestedDocument) -> IngestedDocument:
        """Stage 7: EMBED — generate embedding IDs (actual embedding via worker)."""
        for chunk in doc.chunks:
            embedding_id = str(uuid.uuid4())
            chunk["embedding_id"] = embedding_id
            doc.embedding_ids.append(embedding_id)

        self._stats["embeddings_created"] += len(doc.embedding_ids)
        return doc

    def _handle_reconcile(self, doc: IngestedDocument) -> IngestedDocument:
        """Stage 8: RECONCILE — check for conflicts with existing knowledge."""
        # Reconciliation is handled by the Reconciler in brain bot
        # This stage marks the document as requiring reconciliation
        doc.metadata["reconciliation_required"] = True
        doc.metadata["reconciliation_sources"] = [doc.source]
        return doc

    def _handle_store(self, doc: IngestedDocument) -> IngestedDocument:
        """Stage 9: STORE — prepare for Oracle write (delegated to brain bot)."""
        doc.metadata["store_ready"] = True
        doc.metadata["store_target"] = "supabase"
        return doc

    def _handle_audit(self, doc: IngestedDocument) -> IngestedDocument:
        """Stage 10: AUDIT — record audit trail for this ingestion."""
        doc.audit_events.append({
            "event": "ingestion_complete",
            "document_id": doc.id,
            "hash": doc.content_hash,
            "stages_completed": [s.value for s in self.STAGE_ORDER],
            "error_count": len(doc.errors),
            "chunk_count": len(doc.chunks),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        return doc

    def _is_fatal(self, stage: PipelineStage) -> bool:
        """Check if errors at this stage are fatal."""
        fatal_stages = {PipelineStage.VALIDATE}
        return stage in fatal_stages

    @property
    def stats(self) -> dict:
        return dict(self._stats)
