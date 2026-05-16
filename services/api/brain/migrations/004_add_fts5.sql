-- Migration 004: SQLite FTS5 Full-Text Search
-- Creates a proper full-text index for hybrid search.
-- Uses triggers to keep FTS index in sync with memories table.

CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
    content,
    category,
    source,
    content='memories',
    content_rowid='rowid'
);

-- Trigger: INSERT → FTS
CREATE TRIGGER IF NOT EXISTS memories_fts_insert AFTER INSERT ON memories
BEGIN
    INSERT INTO memories_fts(content, category, source)
    VALUES (NEW.content, NEW.category, NEW.source);
END;

-- Trigger: DELETE → FTS
CREATE TRIGGER IF NOT EXISTS memories_fts_delete AFTER DELETE ON memories
BEGIN
    INSERT INTO memories_fts(memories_fts, content, category, source)
    VALUES ('delete', OLD.content, OLD.category, OLD.source);
END;

-- Trigger: UPDATE → FTS
CREATE TRIGGER IF NOT EXISTS memories_fts_update AFTER UPDATE ON memories
BEGIN
    INSERT INTO memories_fts(memories_fts, content, category, source)
    VALUES ('delete', OLD.content, OLD.category, OLD.source);
    INSERT INTO memories_fts(content, category, source)
    VALUES (NEW.content, NEW.category, NEW.source);
END;

-- Populate FTS with existing data (idempotent: skips already-indexed rows)
INSERT INTO memories_fts(content, category, source)
SELECT content, category, source FROM memories
WHERE rowid NOT IN (SELECT rowid FROM memories_fts);
