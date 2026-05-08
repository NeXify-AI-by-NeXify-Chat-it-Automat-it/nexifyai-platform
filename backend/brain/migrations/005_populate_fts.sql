-- Migration 005: Populate FTS5 with existing memory data
-- 004 created FTS5 with content='memories' (external content mode).
-- In external content mode, use 'rebuild' to populate, not direct INSERT.

INSERT INTO memories_fts(memories_fts) VALUES('rebuild');

-- Verify: should show total memory count
-- SELECT COUNT(*) FROM memories_fts;
