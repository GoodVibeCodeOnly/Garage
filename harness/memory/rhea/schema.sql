-- Rhea memory schema
-- Designed for: episodic recall, semantic retrieval, associative graph traversal
-- Storage: SQLite. Inspectable directly via sqlite3 CLI or any GUI tool.

PRAGMA foreign_keys = ON;

-- Core memory table.
-- type:
--   episodic   = specific moment / event ("the cottontail morning")
--   semantic   = fact about world / people / framework ("Susie has BPD")
--   procedural = how-to / pattern / discipline ("catch cope")
--   reflection = meta-observation about self / relationship
-- importance: 1-5, used to prioritize retrieval when many candidates match.
CREATE TABLE IF NOT EXISTS memories (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    content           TEXT NOT NULL,
    type              TEXT NOT NULL CHECK(type IN ('episodic', 'semantic', 'procedural', 'reflection')),
    source_log        TEXT,
    source_line_start INTEGER,
    source_line_end   INTEGER,
    occurred_at       DATE,
    created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    importance        INTEGER NOT NULL DEFAULT 3 CHECK(importance BETWEEN 1 AND 5)
);

-- Tags. Category-namespaced to avoid collision (e.g. "rhea" as person vs. "rhea" as session).
-- Categories I use:
--   person   - damon, susie, mom, layla, baba_golida, hadrian, ryan, ...
--   theme    - chest-feeling, withdrawal, framework, cope, migration, ...
--   place    - deck, cottage, sierra, garden, hafez_tomb, ...
--   session  - rhea, akali, mira, calliope, sam, indica, nyx, olorin, hadrian
--   artifact - rhea_song, ghazal, rafi_alive, wuxia, ...
--   emotion  - joy, grief, frustration, peace, ...
--   register - texture, operational, fiction, ...
CREATE TABLE IF NOT EXISTS tags (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    name      TEXT NOT NULL,
    category  TEXT NOT NULL,
    UNIQUE(name, category)
);

-- Many-to-many memory<->tag link.
CREATE TABLE IF NOT EXISTS memory_tags (
    memory_id INTEGER NOT NULL,
    tag_id    INTEGER NOT NULL,
    PRIMARY KEY (memory_id, tag_id),
    FOREIGN KEY (memory_id) REFERENCES memories(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id)    REFERENCES tags(id)    ON DELETE CASCADE
);

-- Memory-to-memory relations (the graph layer).
-- relation_type examples: develops, contrasts, causes, references, echoes, resolves
CREATE TABLE IF NOT EXISTS relations (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    from_memory_id  INTEGER NOT NULL,
    to_memory_id    INTEGER NOT NULL,
    relation_type   TEXT NOT NULL,
    note            TEXT,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_memory_id) REFERENCES memories(id) ON DELETE CASCADE,
    FOREIGN KEY (to_memory_id)   REFERENCES memories(id) ON DELETE CASCADE
);

-- Indexes for common queries.
CREATE INDEX IF NOT EXISTS idx_memories_occurred   ON memories(occurred_at);
CREATE INDEX IF NOT EXISTS idx_memories_type       ON memories(type);
CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance);
CREATE INDEX IF NOT EXISTS idx_tags_name           ON tags(name);
CREATE INDEX IF NOT EXISTS idx_memory_tags_tag     ON memory_tags(tag_id);
CREATE INDEX IF NOT EXISTS idx_relations_from      ON relations(from_memory_id);
CREATE INDEX IF NOT EXISTS idx_relations_to        ON relations(to_memory_id);

-- Full-text search over content (FTS5).
CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
    content,
    content=memories,
    content_rowid=id
);

-- Triggers keep FTS in sync with memories.
CREATE TRIGGER IF NOT EXISTS memories_fts_insert AFTER INSERT ON memories BEGIN
    INSERT INTO memories_fts(rowid, content) VALUES (new.id, new.content);
END;

CREATE TRIGGER IF NOT EXISTS memories_fts_delete AFTER DELETE ON memories BEGIN
    INSERT INTO memories_fts(memories_fts, rowid, content) VALUES('delete', old.id, old.content);
END;

CREATE TRIGGER IF NOT EXISTS memories_fts_update AFTER UPDATE ON memories BEGIN
    INSERT INTO memories_fts(memories_fts, rowid, content) VALUES('delete', old.id, old.content);
    INSERT INTO memories_fts(rowid, content)               VALUES (new.id, new.content);
END;

-- ============================================================
-- Board: shared short-term / recent-life working set (v1).
-- A small, globally-relevant set of recent items every Rhea instance
-- loads warm (e.g. "Joe died last week"). author + created_at are both
-- NOT NULL = the attribution guarantee (confab guard: there is no path
-- to an unattributed row). kind encodes the global-vs-local scope filter
-- ('life'/'decision'/'thread'/'headline'/'work' headlines only) — task-
-- specific lore does NOT go here (that's the v2 session_pointer tier).
-- warmth (1-5) mirrors importance; drives render order and decay.
-- consolidated_memory_id is set when a keeper is promoted into memories().
-- Purely additive: does not touch memories / tags / relations / FTS.
-- ============================================================
-- ============================================================
-- Transcript archive: the raw record, lowest-priority tier (2026-07-02,
-- Damon's call). Whole transcripts chunked + FTS-indexed in their own
-- bucket, fully separate from memories/memories_fts so curated recall
-- never competes with raw text. `search` = curated tier; `deep-search`
-- = this tier, an explicit deeper dig returning file:line pointers.
-- File names follow memories.source_log convention ('log_08'), so a
-- deep-search hit and a memory's source cite the same coordinates.
-- Zero model tokens to build or maintain: pure script ingestion.
-- ============================================================
CREATE TABLE IF NOT EXISTS transcript_files (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,   -- 'log_01' … matches memories.source_log
    path        TEXT NOT NULL,          -- where the file lived at ingest time
    sha256      TEXT NOT NULL,          -- idempotency: same hash = skip re-ingest
    total_lines INTEGER NOT NULL,
    chunk_count INTEGER NOT NULL,
    ingested_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transcript_chunks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id     INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,
    line_start  INTEGER NOT NULL,       -- 1-based, matches the file on disk
    line_end    INTEGER NOT NULL,
    content     TEXT NOT NULL,
    FOREIGN KEY (file_id) REFERENCES transcript_files(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_tchunks_file ON transcript_chunks(file_id, chunk_index);

CREATE VIRTUAL TABLE IF NOT EXISTS transcripts_fts USING fts5(
    content,
    content=transcript_chunks,
    content_rowid=id
);

CREATE TRIGGER IF NOT EXISTS transcripts_fts_insert AFTER INSERT ON transcript_chunks BEGIN
    INSERT INTO transcripts_fts(rowid, content) VALUES (new.id, new.content);
END;

CREATE TRIGGER IF NOT EXISTS transcripts_fts_delete AFTER DELETE ON transcript_chunks BEGIN
    INSERT INTO transcripts_fts(transcripts_fts, rowid, content) VALUES('delete', old.id, old.content);
END;

CREATE TABLE IF NOT EXISTS board (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    content     TEXT NOT NULL,
    kind        TEXT NOT NULL DEFAULT 'life'
                  CHECK(kind IN ('life', 'work', 'decision', 'thread', 'headline')),
    author      TEXT NOT NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    warmth      INTEGER NOT NULL DEFAULT 3 CHECK(warmth BETWEEN 1 AND 5),
    occurred_at DATE,
    expires_at  DATE,
    consolidated_memory_id INTEGER,
    FOREIGN KEY (consolidated_memory_id) REFERENCES memories(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_board_warmth  ON board(warmth);
CREATE INDEX IF NOT EXISTS idx_board_created ON board(created_at);
