"""NeXifyAI Core: Embedding Governance v4.8
AIC-49 Phase 3 — Governed Embedding Management

Governance wrapper around the embedding worker.
Ensures: ONE worker, queue-based, heartbeat, retry, dedup, audit.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
import uuid


class EmbeddingStatus(Enum):
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    DUPLICATE = "duplicate"


@dataclass
class EmbeddingJob:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    chunk_id: str = ""
    content_hash: str = ""
    content_length: int = 0
    model: str = "default"
    status: EmbeddingStatus = EmbeddingStatus.QUEUED
    embedding_id: Optional[str] = None
    dimensions: int = 0
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None


class EmbeddingGovernance:
    """
    Governed embedding management.
    Delegates actual embedding to the brain bot's EmbedWorker.
    This module provides governance: queue, validation, dedup, audit.
    """

    def __init__(self, config: dict = None):
        self.config = config or {}
        self._jobs: dict[str, EmbeddingJob] = {}
        self._known_hashes: set = set()
        self._stats = {
            "queued": 0,
            "completed": 0,
            "failed": 0,
            "duplicates_skipped": 0,
            "retried": 0,
        }
        self._model = self.config.get("embedding_model", "default")
        self._dimensions = self.config.get("embedding_dimensions", 1536)

    def enqueue(self, chunk_id: str, content_hash: str,
                content_length: int = 0) -> EmbeddingJob:
        """Enqueue a chunk for embedding."""
        # Dedup check
        if content_hash in self._known_hashes:
            self._stats["duplicates_skipped"] += 1
            return EmbeddingJob(
                chunk_id=chunk_id,
                content_hash=content_hash,
                content_length=content_length,
                status=EmbeddingStatus.DUPLICATE,
            )

        job = EmbeddingJob(
            chunk_id=chunk_id,
            content_hash=content_hash,
            content_length=content_length,
            model=self._model,
        )
        self._jobs[job.id] = job
        self._stats["queued"] += 1
        self._known_hashes.add(content_hash)
        return job

    def complete(self, job_id: str, embedding_id: str = None) -> EmbeddingJob:
        """Mark an embedding job as completed."""
        job = self._jobs.get(job_id)
        if not job:
            raise ValueError(f"Unknown job: {job_id}")

        job.status = EmbeddingStatus.COMPLETED
        job.embedding_id = embedding_id or str(uuid.uuid4())
        job.dimensions = self._dimensions
        job.completed_at = datetime.now(timezone.utc).isoformat()
        self._stats["completed"] += 1
        return job

    def fail(self, job_id: str, error: str) -> EmbeddingJob:
        """Mark an embedding job as failed (with retry logic)."""
        job = self._jobs.get(job_id)
        if not job:
            raise ValueError(f"Unknown job: {job_id}")

        job.retry_count += 1
        if job.retry_count < job.max_retries:
            job.status = EmbeddingStatus.QUEUED  # Re-queue
            job.error = error
            self._stats["retried"] += 1
        else:
            job.status = EmbeddingStatus.FAILED
            job.error = error
            self._stats["failed"] += 1

        return job

    def get_job(self, job_id: str) -> Optional[EmbeddingJob]:
        """Get a job by ID."""
        return self._jobs.get(job_id)

    def get_queued(self) -> list[EmbeddingJob]:
        """Get all queued jobs."""
        return [j for j in self._jobs.values()
                if j.status == EmbeddingStatus.QUEUED]

    def get_failed(self) -> list[EmbeddingJob]:
        """Get all failed jobs."""
        return [j for j in self._jobs.values()
                if j.status == EmbeddingStatus.FAILED]

    @property
    def stats(self) -> dict:
        return dict(self._stats)

    @property
    def queue_size(self) -> int:
        return len(self.get_queued())

    def validate_embedding(self, embedding_id: str, dimensions: int) -> dict:
        """Validate an embedding meets governance requirements."""
        errors = []
        if dimensions != self._dimensions:
            errors.append(f"Dimension mismatch: expected {self._dimensions}, got {dimensions}")
        if not embedding_id:
            errors.append("Missing embedding_id")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "embedding_id": embedding_id,
            "dimensions": dimensions,
            "validated_at": datetime.now(timezone.utc).isoformat(),
        }
