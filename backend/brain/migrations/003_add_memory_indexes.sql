-- Migration 003: Add memory search indexes (SQLite-native)
-- Optimizes hybrid search performance WITHOUT PostgreSQL-specific syntax.

-- Regular B-tree index on content for prefix/substring matching
CREATE INDEX IF NOT EXISTS idx_memories_content ON memories(content);

-- Regular index on tags (SQLite does not support GIN)
CREATE INDEX IF NOT EXISTS idx_memories_tags ON memories(tags);

-- Add memory_meta table for key-value metadata
CREATE TABLE IF NOT EXISTS memory_meta (
    memory_id TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT,
    PRIMARY KEY (memory_id, key),
    FOREIGN KEY (memory_id) REFERENCES memories(id) ON DELETE CASCADE
);
