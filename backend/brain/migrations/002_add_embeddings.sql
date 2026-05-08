-- Migration 002: Add embeddings metadata column
-- Supports embedding versioning and confidence tracking.

ALTER TABLE memories ADD COLUMN embedding_version TEXT DEFAULT '1.0.0';
ALTER TABLE memories ADD COLUMN confidence REAL DEFAULT 0.5;
ALTER TABLE memories ADD COLUMN tags TEXT DEFAULT '[]';
ALTER TABLE memories ADD COLUMN expires_at TEXT;

CREATE INDEX IF NOT EXISTS idx_memories_expires ON memories(expires_at);
