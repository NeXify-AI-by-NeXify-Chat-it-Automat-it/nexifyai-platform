-- Migration 003: Add memory search indexes
-- Optimizes hybrid search performance.

CREATE INDEX IF NOT EXISTS idx_memories_content_fts ON memories(content);
CREATE INDEX IF NOT EXISTS idx_memories_tags_gin ON memories(tags);

-- Add memory_meta table for key-value metadata
CREATE TABLE IF NOT EXISTS memory_meta (
    memory_id TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT,
    PRIMARY KEY (memory_id, key),
    FOREIGN KEY (memory_id) REFERENCES memories(id) ON DELETE CASCADE
);
