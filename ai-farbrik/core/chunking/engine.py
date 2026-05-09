"""NeXifyAI Core: Chunking Engine v4.8
AIC-49 Phase 1/3 — Governed Document Chunking

Semantic + structural chunking with overlap and governance validation.
"""

from dataclasses import dataclass, field
from typing import Any, Optional
import hashlib
import re


@dataclass
class Chunk:
    index: int
    content: str
    hash: str = ""
    token_estimate: int = 0
    chunk_strategy: str = "semantic"
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.hash:
            self.hash = hashlib.sha256(self.content.encode()).hexdigest()[:16]
        if not self.token_estimate:
            self.token_estimate = len(self.content) // 4


class ChunkingEngine:
    """Governed chunking with multiple strategies."""

    STRATEGIES = ["semantic", "fixed", "sentence", "markdown_header"]

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.default_strategy = self.config.get("chunk_strategy", "semantic")
        self.chunk_size = self.config.get("chunk_size", 1000)
        self.chunk_overlap = self.config.get("chunk_overlap", 200)
        self.min_chunk_size = self.config.get("min_chunk_size", 50)

    def chunk(self, content: str, strategy: str = None,
              metadata: dict = None) -> list[Chunk]:
        """Chunk a document using the specified strategy."""
        strategy = strategy or self.default_strategy
        metadata = metadata or {}

        if strategy == "semantic":
            chunks = self._chunk_semantic(content)
        elif strategy == "fixed":
            chunks = self._chunk_fixed(content)
        elif strategy == "sentence":
            chunks = self._chunk_sentence(content)
        elif strategy == "markdown_header":
            chunks = self._chunk_markdown_header(content)
        else:
            raise ValueError(f"Unknown chunking strategy: {strategy}")

        # Filter out chunks below minimum size
        chunks = [c for c in chunks if len(c.content) >= self.min_chunk_size]

        # Apply metadata
        for chunk in chunks:
            chunk.metadata.update(metadata)

        return chunks

    def _chunk_semantic(self, content: str) -> list[Chunk]:
        """Chunk by semantic boundaries (paragraphs, sections)."""
        # Split by double newlines (paragraph boundaries)
        paragraphs = re.split(r'\n\s*\n', content)
        chunks = []
        current = ""
        idx = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            if len(current) + len(para) > self.chunk_size and current:
                chunks.append(Chunk(
                    index=idx,
                    content=current.strip(),
                    chunk_strategy="semantic",
                ))
                idx += 1
                # Overlap
                overlap = current[-self.chunk_overlap:] if len(current) > self.chunk_overlap else ""
                current = overlap + "\n\n" + para
            else:
                current += ("\n\n" if current else "") + para

        if current.strip():
            chunks.append(Chunk(
                index=idx,
                content=current.strip(),
                chunk_strategy="semantic",
            ))

        return chunks

    def _chunk_fixed(self, content: str) -> list[Chunk]:
        """Chunk by fixed character size with overlap."""
        chunks = []
        start = 0
        idx = 0

        while start < len(content):
            end = min(start + self.chunk_size, len(content))
            chunk_text = content[start:end]
            chunks.append(Chunk(
                index=idx,
                content=chunk_text.strip(),
                chunk_strategy="fixed",
            ))
            idx += 1
            start = end - self.chunk_overlap

        return chunks

    def _chunk_sentence(self, content: str) -> list[Chunk]:
        """Chunk by sentences, grouping up to chunk_size."""
        sentences = re.split(r'(?<=[.!?])\s+', content)
        chunks = []
        current = ""
        idx = 0

        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue

            if len(current) + len(sent) > self.chunk_size and current:
                chunks.append(Chunk(
                    index=idx,
                    content=current.strip(),
                    chunk_strategy="sentence",
                ))
                idx += 1
                current = sent
            else:
                current += (" " if current else "") + sent

        if current.strip():
            chunks.append(Chunk(
                index=idx,
                content=current.strip(),
                chunk_strategy="sentence",
            ))

        return chunks

    def _chunk_markdown_header(self, content: str) -> list[Chunk]:
        """Chunk by markdown headers (##, ###)."""
        # Split by H2 headers
        sections = re.split(r'\n(?=## )', content)
        chunks = []
        idx = 0

        for section in sections:
            section = section.strip()
            if not section:
                continue

            # If section is too long, sub-chunk semantically
            if len(section) > self.chunk_size:
                sub_chunks = self._chunk_semantic(section)
                for sub in sub_chunks:
                    sub.index = idx
                    sub.chunk_strategy = "markdown_header"
                    chunks.append(sub)
                    idx += 1
            else:
                chunks.append(Chunk(
                    index=idx,
                    content=section,
                    chunk_strategy="markdown_header",
                ))
                idx += 1

        return chunks

    def validate_chunks(self, chunks: list[Chunk]) -> dict:
        """Validate chunk quality."""
        if not chunks:
            return {"valid": False, "error": "No chunks produced"}

        sizes = [len(c.content) for c in chunks]
        hashes = [c.hash for c in chunks]

        return {
            "valid": True,
            "chunk_count": len(chunks),
            "avg_size": sum(sizes) / len(sizes),
            "min_size": min(sizes),
            "max_size": max(sizes),
            "unique_hashes": len(set(hashes)),
            "duplicate_hashes": len(hashes) - len(set(hashes)),
            "total_content": sum(sizes),
        }
