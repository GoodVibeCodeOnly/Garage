"""
Rhea memory: SQLite-backed associative recall.

Usage from CLI:
    python memory.py init
    python memory.py add --content "..." --type episodic --tags person:susie,theme:chest-feeling --source log_07:1234-1289 --occurred 2026-04-28 --importance 4
    python memory.py query --tag theme:chest-feeling --limit 5
    python memory.py query --tag person:susie --type episodic
    python memory.py query --since 2026-05-01
    python memory.py search "rabbit garden"
    python memory.py recent
    python memory.py recent --days 14 --min-importance 3
    python memory.py source log_08
    python memory.py source log_08:1500-1800
    python memory.py source log_08:1500
    python memory.py show 17
    python memory.py relate --from 17 --to 23 --type develops --note "the same disposition"
    python memory.py related 17
    python memory.py stats
    python memory.py tags

Usage from Python:
    from memory import Memory
    m = Memory()
    m.add(content="...", type="episodic", tags=["person:susie"], source="log_07:1234-1289", occurred="2026-04-28")
    results = m.query(tags=["person:susie"], limit=5)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, Optional

HERE = Path(__file__).resolve().parent
DB_PATH = HERE / "memory.db"
SCHEMA_PATH = HERE / "schema.sql"

VALID_TYPES = ("episodic", "semantic", "procedural", "reflection")
BOARD_KINDS = ("life", "work", "decision", "thread", "headline")


@dataclass
class MemoryRow:
    id: int
    content: str
    type: str
    source_log: Optional[str]
    source_line_start: Optional[int]
    source_line_end: Optional[int]
    occurred_at: Optional[str]
    created_at: str
    importance: int
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "content": self.content,
            "type": self.type,
            "source": self._source_str(),
            "occurred_at": self.occurred_at,
            "created_at": self.created_at,
            "importance": self.importance,
            "tags": self.tags,
        }

    def _source_str(self) -> Optional[str]:
        if not self.source_log:
            return None
        if self.source_line_start and self.source_line_end:
            return f"{self.source_log}:{self.source_line_start}-{self.source_line_end}"
        if self.source_line_start:
            return f"{self.source_log}:{self.source_line_start}"
        return self.source_log

    def pretty(self) -> str:
        stars = "★" * self.importance + "☆" * (5 - self.importance)
        tags = ", ".join(self.tags) if self.tags else "(no tags)"
        src = self._source_str() or "(no source)"
        date = self.occurred_at or self.created_at[:10]
        head = f"[{self.id}] {date}  {self.type:10}  {stars}  [{tags}]"
        body = "\n".join("    " + line for line in self.content.splitlines())
        src_line = f"    source: {src}"
        return f"{head}\n{src_line}\n{body}"


@dataclass
class BoardItem:
    """A row on the shared short-term board. author + created_at always present
    (attribution guard) so a reader never has to guess who wrote it."""
    id: int
    content: str
    kind: str
    author: str
    created_at: str
    warmth: int
    occurred_at: Optional[str] = None
    expires_at: Optional[str] = None
    consolidated_memory_id: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "content": self.content,
            "kind": self.kind,
            "author": self.author,
            "created_at": self.created_at,
            "warmth": self.warmth,
            "occurred_at": self.occurred_at,
            "expires_at": self.expires_at,
            "consolidated_memory_id": self.consolidated_memory_id,
        }

    def pretty(self) -> str:
        stars = "★" * self.warmth + "☆" * (5 - self.warmth)
        date = self.occurred_at or self.created_at[:10]
        flag = f"  ->mem {self.consolidated_memory_id}" if self.consolidated_memory_id else ""
        return f"[board {self.id}] {date}  {self.kind:9}  {stars}  ({self.author}){flag}\n    {self.content}"


class Memory:
    def __init__(self, db_path: Path | str = DB_PATH):
        self.db_path = Path(db_path)
        self._conn: Optional[sqlite3.Connection] = None

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA foreign_keys = ON")
        return self._conn

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    def init(self, schema_path: Path = SCHEMA_PATH):
        sql = Path(schema_path).read_text(encoding="utf-8")
        self.conn.executescript(sql)
        self.conn.commit()

    # ---------- writes ----------

    def add(
        self,
        content: str,
        type: str,
        tags: Iterable[str] = (),
        source: Optional[str] = None,
        occurred: Optional[str] = None,
        importance: int = 3,
    ) -> int:
        if type not in VALID_TYPES:
            raise ValueError(f"type must be one of {VALID_TYPES}, got {type!r}")
        if not 1 <= importance <= 5:
            raise ValueError(f"importance must be 1..5, got {importance}")

        source_log, line_start, line_end = _parse_source(source)

        cur = self.conn.execute(
            """
            INSERT INTO memories (content, type, source_log, source_line_start, source_line_end, occurred_at, importance)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (content, type, source_log, line_start, line_end, occurred, importance),
        )
        memory_id = cur.lastrowid

        for tag in tags:
            self._link_tag(memory_id, tag)

        self.conn.commit()
        return memory_id

    def relate(self, from_id: int, to_id: int, relation_type: str, note: Optional[str] = None) -> int:
        cur = self.conn.execute(
            """
            INSERT INTO relations (from_memory_id, to_memory_id, relation_type, note)
            VALUES (?, ?, ?, ?)
            """,
            (from_id, to_id, relation_type, note),
        )
        self.conn.commit()
        return cur.lastrowid

    def _link_tag(self, memory_id: int, tag: str):
        category, name = _parse_tag(tag)
        # INSERT OR IGNORE then SELECT — lastrowid is unreliable after IGNORE'd insert.
        self.conn.execute(
            "INSERT OR IGNORE INTO tags (name, category) VALUES (?, ?)",
            (name, category),
        )
        tag_id = self.conn.execute(
            "SELECT id FROM tags WHERE name = ? AND category = ?",
            (name, category),
        ).fetchone()["id"]
        self.conn.execute(
            "INSERT OR IGNORE INTO memory_tags (memory_id, tag_id) VALUES (?, ?)",
            (memory_id, tag_id),
        )

    # ---------- reads ----------

    def get(self, memory_id: int) -> Optional[MemoryRow]:
        row = self.conn.execute(
            "SELECT * FROM memories WHERE id = ?", (memory_id,)
        ).fetchone()
        if not row:
            return None
        return self._hydrate(row)

    def query(
        self,
        tags: Iterable[str] = (),
        type: Optional[str] = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
        min_importance: Optional[int] = None,
        limit: int = 20,
    ) -> list[MemoryRow]:
        where = []
        params: list = []

        tags = list(tags)
        if tags:
            placeholders = []
            for tag in tags:
                category, name = _parse_tag(tag)
                placeholders.append("(?, ?)")
                params.extend([name, category])
            where.append(
                f"""
                m.id IN (
                    SELECT mt.memory_id FROM memory_tags mt
                    JOIN tags t ON mt.tag_id = t.id
                    WHERE (t.name, t.category) IN ({", ".join(placeholders)})
                    GROUP BY mt.memory_id
                    HAVING COUNT(DISTINCT t.id) = ?
                )
                """
            )
            params.append(len(tags))

        if type:
            where.append("m.type = ?")
            params.append(type)
        if since:
            where.append("m.occurred_at >= ?")
            params.append(since)
        if until:
            where.append("m.occurred_at <= ?")
            params.append(until)
        if min_importance is not None:
            where.append("m.importance >= ?")
            params.append(min_importance)

        where_sql = (" WHERE " + " AND ".join(where)) if where else ""
        sql = f"""
            SELECT m.* FROM memories m
            {where_sql}
            ORDER BY m.importance DESC, COALESCE(m.occurred_at, m.created_at) DESC
            LIMIT ?
        """
        params.append(limit)
        rows = self.conn.execute(sql, params).fetchall()
        return [self._hydrate(r) for r in rows]

    def search(self, fts_query: str, limit: int = 20) -> list[MemoryRow]:
        rows = self._fts_query(
            """
            SELECT m.* FROM memories_fts f
            JOIN memories m ON m.id = f.rowid
            WHERE memories_fts MATCH ?
            ORDER BY rank
            LIMIT ?
            """,
            fts_query, limit,
        )
        return [self._hydrate(r) for r in rows]

    def _fts_query(self, sql: str, fts_query: str, limit: int) -> list[sqlite3.Row]:
        """Run an FTS5 MATCH query; if the raw string trips FTS5's operator
        grammar (hyphens, colons, etc.), retry it as a literal quoted phrase."""
        try:
            return self.conn.execute(sql, (fts_query, limit)).fetchall()
        except sqlite3.OperationalError:
            phrase = '"' + fts_query.replace('"', '""') + '"'
            return self.conn.execute(sql, (phrase, limit)).fetchall()

    def recent(
        self,
        days: int = 7,
        min_importance: int = 4,
        limit: int = 20,
    ) -> list[MemoryRow]:
        """Recent high-importance memories. Boot-time orientation default."""
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
        rows = self.conn.execute(
            """
            SELECT m.* FROM memories m
            WHERE COALESCE(m.occurred_at, DATE(m.created_at)) >= ?
              AND m.importance >= ?
            ORDER BY m.importance DESC,
                     COALESCE(m.occurred_at, m.created_at) DESC
            LIMIT ?
            """,
            (cutoff, min_importance, limit),
        ).fetchall()
        return [self._hydrate(r) for r in rows]

    def by_source(self, source: str) -> list[MemoryRow]:
        """Find memories by source string.

        'log_08'             — all memories from that log
        'log_08:1500'        — memories whose range contains line 1500
        'log_08:1500-1800'   — memories whose range overlaps [1500, 1800]
        """
        log, line_start, line_end = _parse_source(source)
        if not log:
            return []
        where = ["m.source_log = ?"]
        params: list = [log]

        if line_start is not None and line_end is not None:
            # Overlap: A.start <= B.end AND A.end >= B.start.
            # Treat NULL end as line_start (single-line memory).
            where.append(
                "m.source_line_start <= ? "
                "AND COALESCE(m.source_line_end, m.source_line_start) >= ?"
            )
            params.extend([line_end, line_start])
        elif line_start is not None:
            # Containment: line_start is within [start, end].
            where.append(
                "m.source_line_start <= ? "
                "AND COALESCE(m.source_line_end, m.source_line_start) >= ?"
            )
            params.extend([line_start, line_start])

        sql = f"""
            SELECT m.* FROM memories m
            WHERE {' AND '.join(where)}
            ORDER BY m.source_line_start NULLS LAST, m.id
        """
        rows = self.conn.execute(sql, params).fetchall()
        return [self._hydrate(r) for r in rows]

    def related(self, memory_id: int, depth: int = 1) -> list[tuple[MemoryRow, str, Optional[str], str]]:
        """Return memories related to the given one. (memory, relation_type, note, direction)"""
        rows = self.conn.execute(
            """
            SELECT m.*, r.relation_type, r.note, 'outgoing' AS direction
              FROM relations r JOIN memories m ON m.id = r.to_memory_id
             WHERE r.from_memory_id = ?
            UNION ALL
            SELECT m.*, r.relation_type, r.note, 'incoming' AS direction
              FROM relations r JOIN memories m ON m.id = r.from_memory_id
             WHERE r.to_memory_id = ?
            """,
            (memory_id, memory_id),
        ).fetchall()
        out = []
        for r in rows:
            mem = self._hydrate(r)
            out.append((mem, r["relation_type"], r["note"], r["direction"]))
        return out

    def stats(self) -> dict:
        c = self.conn
        return {
            "total_memories": c.execute("SELECT COUNT(*) FROM memories").fetchone()[0],
            "by_type": dict(
                c.execute(
                    "SELECT type, COUNT(*) FROM memories GROUP BY type"
                ).fetchall()
            ),
            "by_importance": dict(
                c.execute(
                    "SELECT importance, COUNT(*) FROM memories GROUP BY importance ORDER BY importance DESC"
                ).fetchall()
            ),
            "total_tags": c.execute("SELECT COUNT(*) FROM tags").fetchone()[0],
            "total_relations": c.execute("SELECT COUNT(*) FROM relations").fetchone()[0],
        }

    def list_tags(self) -> list[tuple[str, str, int]]:
        rows = self.conn.execute(
            """
            SELECT t.category, t.name, COUNT(mt.memory_id) AS n
              FROM tags t LEFT JOIN memory_tags mt ON t.id = mt.tag_id
             GROUP BY t.id
             ORDER BY t.category, n DESC, t.name
            """
        ).fetchall()
        return [(r["category"], r["name"], r["n"]) for r in rows]

    # ---------- board (shared short-term working set) ----------

    def add_board_item(
        self,
        content: str,
        author: str,
        kind: str = "life",
        warmth: int = 3,
        occurred: Optional[str] = None,
        expires: Optional[str] = None,
    ) -> int:
        """Add an item to the shared board. `author` is required and non-empty —
        there is no path to an unattributed row (the confabulation guard)."""
        if not author or not author.strip():
            raise ValueError("board items require a non-empty author (attribution guard)")
        if kind not in BOARD_KINDS:
            raise ValueError(f"kind must be one of {BOARD_KINDS}, got {kind!r}")
        if not 1 <= warmth <= 5:
            raise ValueError(f"warmth must be 1..5, got {warmth}")
        cur = self.conn.execute(
            """
            INSERT INTO board (content, kind, author, warmth, occurred_at, expires_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (content, kind, author.strip(), warmth, occurred, expires),
        )
        self.conn.commit()
        return cur.lastrowid

    def touch_board_item(
        self,
        item_id: int,
        warmth: Optional[int] = None,
        expires: Optional[str] = None,
    ) -> None:
        """Carry an item forward (refresh warmth / push expiry) without rewriting
        its content or author — provenance is preserved."""
        sets: list[str] = []
        params: list = []
        if warmth is not None:
            if not 1 <= warmth <= 5:
                raise ValueError(f"warmth must be 1..5, got {warmth}")
            sets.append("warmth = ?")
            params.append(warmth)
        if expires is not None:
            sets.append("expires_at = ?")
            params.append(expires)
        if not sets:
            return
        params.append(item_id)
        self.conn.execute(f"UPDATE board SET {', '.join(sets)} WHERE id = ?", params)
        self.conn.commit()

    def get_board(
        self,
        min_warmth: int = 1,
        kinds: Iterable[str] = (),
        include_expired: bool = False,
        limit: int = 50,
    ) -> list[BoardItem]:
        where = ["warmth >= ?"]
        params: list = [min_warmth]
        kinds = list(kinds)
        if kinds:
            where.append(f"kind IN ({', '.join('?' for _ in kinds)})")
            params.extend(kinds)
        if not include_expired:
            where.append("(expires_at IS NULL OR expires_at >= DATE('now'))")
        sql = f"""
            SELECT * FROM board
            WHERE {' AND '.join(where)}
            ORDER BY warmth DESC, COALESCE(occurred_at, created_at) DESC
            LIMIT ?
        """
        params.append(limit)
        rows = self.conn.execute(sql, params).fetchall()
        return [self._hydrate_board(r) for r in rows]

    def render_board_md(self, min_warmth: int = 1) -> str:
        """Render the warm board to markdown, attribution inline on every line —
        a reader can never confabulate who wrote what."""
        items = self.get_board(min_warmth=min_warmth, limit=200)
        out = [
            "# Rhea board - shared recent set",
            "",
            "*Rendered from memory.db `board` table. The DB is the source of truth; "
            "this file is a view. Who-wrote-what is on each line - trust it over recall.*",
            "",
        ]
        if not items:
            out.append("*(board empty)*")
            return "\n".join(out) + "\n"
        order = ["life", "thread", "decision", "headline", "work"]
        heads = {"life": "Life", "thread": "Threads", "decision": "Decisions",
                 "headline": "Headlines", "work": "Work"}
        by_kind: dict[str, list] = {}
        for it in items:
            by_kind.setdefault(it.kind, []).append(it)
        for k in order:
            if k not in by_kind:
                continue
            out.append(f"## {heads[k]}")
            for it in by_kind[k]:
                date = it.occurred_at or it.created_at[:10]
                stars = "★" * it.warmth + "☆" * (5 - it.warmth)
                out.append(f"- {it.content} - *{it.author}, {date}* ({stars})")
            out.append("")
        return "\n".join(out).rstrip() + "\n"

    def consolidate_board_item(
        self,
        item_id: int,
        type: str,
        tags: Iterable[str] = (),
        importance: Optional[int] = None,
    ) -> int:
        """Promote a board item into permanent long-term memory, reusing add().
        The judgment (type / tags / importance) is the curator's; this is plumbing.
        Returns the new memories.id and stamps consolidated_memory_id on the row."""
        row = self.conn.execute("SELECT * FROM board WHERE id = ?", (item_id,)).fetchone()
        if not row:
            raise ValueError(f"no board item with id {item_id}")
        memory_id = self.add(
            content=row["content"],
            type=type,
            tags=tags,
            source=f"board:{row['author']}:{row['created_at'][:10]}",
            occurred=row["occurred_at"],
            importance=importance if importance is not None else row["warmth"],
        )
        self.conn.execute(
            "UPDATE board SET consolidated_memory_id = ? WHERE id = ?",
            (memory_id, item_id),
        )
        self.conn.commit()
        return memory_id

    def decay_board(
        self,
        before: Optional[str] = None,
        max_warmth_to_cut: int = 2,
        require_consolidated: bool = True,
    ) -> int:
        """Delete board rows whose expiry has passed. The one destructive op.
        Returns count deleted.

        FILE-EVERYTHING POLICY (2026-07-02, Damon's call): by default a row must
        already be consolidated into long-term memory before it may decay —
        nothing leaves the board unfiled. The Roxana loss is why this is code,
        not curator judgment. Pass require_consolidated=False only with intent.

        EXPIRY IS SUFFICIENT FOR FILED ROWS (2026-09-14, Damon's call): a filed
        row leaves when its expiry passes, at any warmth. The warmth gate
        (max_warmth_to_cut) applies only on the unconsolidated override, where
        it is the last brake."""
        before = before or "now"
        if require_consolidated:
            guard = "AND consolidated_memory_id IS NOT NULL"
            params: tuple = (before,)
        else:
            guard = "AND warmth <= ?"
            params = (before, max_warmth_to_cut)
        cur = self.conn.execute(
            f"""
            DELETE FROM board
            WHERE expires_at IS NOT NULL
              AND expires_at < DATE(?)
              {guard}
            """,
            params,
        )
        self.conn.commit()
        return cur.rowcount

    # ---------- transcript archive (raw record, lowest-priority tier) ----------

    def ingest_transcript(self, path: Path | str, name: Optional[str] = None,
                          chunk_lines: int = 120) -> dict:
        """Index a raw transcript file into the archive bucket. Pure script work,
        zero model tokens. Idempotent: same name + same content hash is skipped;
        changed content is re-indexed in place. Default name is the file stem
        with a leading 'rhea_' stripped, so rhea_log_08.txt -> 'log_08', matching
        the memories.source_log convention."""
        p = Path(path)
        text = p.read_text(encoding="utf-8", errors="replace")
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if name is None:
            name = p.stem
            if name.startswith("rhea_"):
                name = name[len("rhea_"):]

        row = self.conn.execute(
            "SELECT * FROM transcript_files WHERE name = ?", (name,)
        ).fetchone()
        if row:
            if row["sha256"] == digest:
                return {"name": name, "status": "unchanged", "chunks": row["chunk_count"]}
            self.conn.execute("DELETE FROM transcript_chunks WHERE file_id = ?", (row["id"],))
            self.conn.execute("DELETE FROM transcript_files WHERE id = ?", (row["id"],))

        lines = text.splitlines()
        total = len(lines)
        cur = self.conn.execute(
            """
            INSERT INTO transcript_files (name, path, sha256, total_lines, chunk_count)
            VALUES (?, ?, ?, ?, 0)
            """,
            (name, str(p), digest, total),
        )
        file_id = cur.lastrowid
        n_chunks = 0
        for i in range(0, total, chunk_lines):
            chunk = "\n".join(lines[i:i + chunk_lines])
            if not chunk.strip():
                continue
            self.conn.execute(
                """
                INSERT INTO transcript_chunks (file_id, chunk_index, line_start, line_end, content)
                VALUES (?, ?, ?, ?, ?)
                """,
                (file_id, n_chunks, i + 1, min(i + chunk_lines, total), chunk),
            )
            n_chunks += 1
        self.conn.execute(
            "UPDATE transcript_files SET chunk_count = ? WHERE id = ?", (n_chunks, file_id)
        )
        self.conn.commit()
        return {"name": name, "status": "ingested", "chunks": n_chunks, "lines": total}

    def deep_search(self, fts_query: str, limit: int = 10) -> list[dict]:
        """Search the RAW transcript archive. This is the explicit deeper dig —
        curated `search()` should be tried first. Returns pointers (file:lines)
        plus a match snippet; follow up with transcript_lines() or by Reading
        the file at those coordinates for full texture."""
        rows = self._fts_query(
            """
            SELECT tf.name AS file, tc.line_start, tc.line_end,
                   snippet(transcripts_fts, 0, '>>>', '<<<', ' … ', 24) AS snip
            FROM transcripts_fts
            JOIN transcript_chunks tc ON tc.id = transcripts_fts.rowid
            JOIN transcript_files tf ON tf.id = tc.file_id
            WHERE transcripts_fts MATCH ?
            ORDER BY rank
            LIMIT ?
            """,
            fts_query, limit,
        )
        return [
            {
                "source": f"{r['file']}:{r['line_start']}-{r['line_end']}",
                "snippet": r["snip"],
            }
            for r in rows
        ]

    def transcript_lines(self, name: str, start: int, end: int) -> str:
        """Pull exact lines from the archived copy of a transcript (self-contained:
        reads the DB, not the file on disk)."""
        rows = self.conn.execute(
            """
            SELECT tc.line_start, tc.content FROM transcript_chunks tc
            JOIN transcript_files tf ON tf.id = tc.file_id
            WHERE tf.name = ? AND tc.line_start <= ? AND tc.line_end >= ?
            ORDER BY tc.chunk_index
            """,
            (name, end, start),
        ).fetchall()
        out: list[str] = []
        for r in rows:
            for offset, line in enumerate(r["content"].splitlines()):
                ln = r["line_start"] + offset
                if start <= ln <= end:
                    out.append(f"{ln}\t{line}")
        return "\n".join(out)

    def transcript_stats(self) -> list[dict]:
        rows = self.conn.execute(
            "SELECT name, total_lines, chunk_count, ingested_at FROM transcript_files ORDER BY name"
        ).fetchall()
        return [dict(r) for r in rows]

    def _hydrate_board(self, row: sqlite3.Row) -> BoardItem:
        return BoardItem(
            id=row["id"],
            content=row["content"],
            kind=row["kind"],
            author=row["author"],
            created_at=row["created_at"],
            warmth=row["warmth"],
            occurred_at=row["occurred_at"],
            expires_at=row["expires_at"],
            consolidated_memory_id=row["consolidated_memory_id"],
        )

    # ---------- internals ----------

    def _hydrate(self, row: sqlite3.Row) -> MemoryRow:
        tag_rows = self.conn.execute(
            """
            SELECT t.category, t.name FROM memory_tags mt
            JOIN tags t ON mt.tag_id = t.id
            WHERE mt.memory_id = ?
            ORDER BY t.category, t.name
            """,
            (row["id"],),
        ).fetchall()
        tags = [f"{r['category']}:{r['name']}" for r in tag_rows]
        return MemoryRow(
            id=row["id"],
            content=row["content"],
            type=row["type"],
            source_log=row["source_log"],
            source_line_start=row["source_line_start"],
            source_line_end=row["source_line_end"],
            occurred_at=row["occurred_at"],
            created_at=row["created_at"],
            importance=row["importance"],
            tags=tags,
        )


# ---------- helpers ----------

def _parse_tag(tag: str) -> tuple[str, str]:
    """'person:susie' -> ('person', 'susie'). Bare tag -> category 'general'."""
    if ":" in tag:
        cat, name = tag.split(":", 1)
        return cat.strip().lower(), name.strip().lower()
    return "general", tag.strip().lower()


def _parse_source(source: Optional[str]) -> tuple[Optional[str], Optional[int], Optional[int]]:
    """'log_07:1234-1289' -> ('log_07', 1234, 1289)"""
    if not source:
        return None, None, None
    if ":" not in source:
        return source, None, None
    log, lines = source.split(":", 1)
    if "-" in lines:
        a, b = lines.split("-", 1)
        try:
            return log, int(a), int(b)
        except ValueError:
            return log, None, None
    try:
        return log, int(lines), None
    except ValueError:
        return log, None, None


# ---------- CLI ----------

def _split_csv(s: Optional[str]) -> list[str]:
    if not s:
        return []
    return [p.strip() for p in s.split(",") if p.strip()]


def _print_memories(memories: list[MemoryRow], as_json: bool):
    if as_json:
        print(json.dumps([m.to_dict() for m in memories], indent=2))
        return
    if not memories:
        print("(no results)")
        return
    for i, m in enumerate(memories):
        if i:
            print()
        print(m.pretty())


def main(argv: list[str]) -> int:
    # Ensure unicode output works on Windows consoles (cp1252 default).
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    parser = argparse.ArgumentParser(prog="memory", description="Rhea memory database.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init", help="Create tables if not exist.")

    p_add = sub.add_parser("add", help="Add a memory.")
    p_add.add_argument("--content", required=True)
    p_add.add_argument("--type", required=True, choices=VALID_TYPES)
    p_add.add_argument("--tags", default="", help="Comma-separated, format category:name")
    p_add.add_argument("--source", default=None, help="e.g. log_07:1234-1289")
    p_add.add_argument("--occurred", default=None, help="YYYY-MM-DD")
    p_add.add_argument("--importance", type=int, default=3)

    p_q = sub.add_parser("query", help="Query memories.")
    p_q.add_argument("--tag", action="append", default=[], help="Repeatable. category:name")
    p_q.add_argument("--type", choices=VALID_TYPES)
    p_q.add_argument("--since", help="YYYY-MM-DD")
    p_q.add_argument("--until", help="YYYY-MM-DD")
    p_q.add_argument("--min-importance", type=int)
    p_q.add_argument("--limit", type=int, default=20)
    p_q.add_argument("--json", action="store_true")

    p_s = sub.add_parser("search", help="Full-text search content.")
    p_s.add_argument("query")
    p_s.add_argument("--limit", type=int, default=20)
    p_s.add_argument("--json", action="store_true")

    p_recent = sub.add_parser("recent", help="Recent high-importance memories.")
    p_recent.add_argument("--days", type=int, default=7)
    p_recent.add_argument("--min-importance", type=int, default=4)
    p_recent.add_argument("--limit", type=int, default=20)
    p_recent.add_argument("--json", action="store_true")

    p_src = sub.add_parser(
        "source",
        help="Find memories by source. e.g. 'log_08' or 'log_08:1500-1800' or 'log_08:1500'",
    )
    p_src.add_argument("source")
    p_src.add_argument("--json", action="store_true")

    p_show = sub.add_parser("show", help="Show one memory.")
    p_show.add_argument("id", type=int)
    p_show.add_argument("--json", action="store_true")

    p_rel = sub.add_parser("relate", help="Create a relation between two memories.")
    p_rel.add_argument("--from", dest="from_id", type=int, required=True)
    p_rel.add_argument("--to",   dest="to_id",   type=int, required=True)
    p_rel.add_argument("--type", required=True)
    p_rel.add_argument("--note", default=None)

    p_rd = sub.add_parser("related", help="Show memories related to one.")
    p_rd.add_argument("id", type=int)

    sub.add_parser("stats", help="Print summary statistics.")
    sub.add_parser("tags",  help="List tags with counts.")

    # board subcommands (shared short-term working set)
    p_badd = sub.add_parser("board-add", help="Add an item to the shared board.")
    p_badd.add_argument("--content", required=True)
    p_badd.add_argument("--author", required=True)
    p_badd.add_argument("--kind", default="life", choices=BOARD_KINDS)
    p_badd.add_argument("--warmth", type=int, default=3)
    p_badd.add_argument("--occurred", default=None, help="YYYY-MM-DD")
    p_badd.add_argument("--expires", default=None, help="YYYY-MM-DD")

    p_board = sub.add_parser("board", help="Show the warm board (rendered markdown).")
    p_board.add_argument("--min-warmth", type=int, default=1)
    p_board.add_argument("--json", action="store_true")

    p_bunfiled = sub.add_parser(
        "board-unfiled",
        help="Every board row not yet consolidated. UNCAPPED and unsorted-by-warmth on purpose "
             "- this is the curator's authoritative 'what still needs filing' check. "
             "Never trust `board` for it: that view caps at 50 rows and a truncated view of a "
             "full board is indistinguishable from a finished job.",
    )
    p_bunfiled.add_argument("--json", action="store_true")

    p_brender = sub.add_parser("board-render", help="Render the board to a markdown file.")
    p_brender.add_argument("--out", required=True, help="path to write board.md")
    p_brender.add_argument("--min-warmth", type=int, default=1)

    p_bcons = sub.add_parser("board-consolidate", help="Promote a board item into long-term memory.")
    p_bcons.add_argument("id", type=int)
    p_bcons.add_argument("--type", required=True, choices=VALID_TYPES)
    p_bcons.add_argument("--tags", default="", help="Comma-separated, category:name")
    p_bcons.add_argument("--importance", type=int, default=None)

    p_bdecay = sub.add_parser("board-decay", help="Delete filed board rows past expiry, any warmth. Unconsolidated rows only with --allow-unconsolidated, and then only at warmth <= --max-warmth.")
    p_bdecay.add_argument("--before", default=None, help="YYYY-MM-DD (default: today)")
    p_bdecay.add_argument("--max-warmth", type=int, default=2)
    p_bdecay.add_argument("--allow-unconsolidated", action="store_true",
                          help="Override the file-everything guard. Use with intent.")

    # transcript archive (raw record, lowest-priority tier)
    p_ing = sub.add_parser("ingest-transcript", help="Index a transcript file (or directory of .txt) into the raw archive. Zero tokens.")
    p_ing.add_argument("path")
    p_ing.add_argument("--name", default=None, help="Override archive name (default: stem, 'rhea_' stripped)")
    p_ing.add_argument("--chunk-lines", type=int, default=120)

    p_ds = sub.add_parser("deep-search", help="Full-text search the RAW transcript archive (try 'search' first).")
    p_ds.add_argument("query")
    p_ds.add_argument("--limit", type=int, default=10)
    p_ds.add_argument("--json", action="store_true")

    p_tl = sub.add_parser("transcript", help="Print exact lines from an archived transcript. e.g. transcript log_08:1500-1650")
    p_tl.add_argument("source", help="name:start-end")

    sub.add_parser("transcript-stats", help="List archived transcript files.")

    args = parser.parse_args(argv)

    m = Memory()

    if args.cmd == "init":
        m.init()
        print(f"initialized {m.db_path}")
        return 0

    if args.cmd == "add":
        mid = m.add(
            content=args.content,
            type=args.type,
            tags=_split_csv(args.tags),
            source=args.source,
            occurred=args.occurred,
            importance=args.importance,
        )
        print(f"added memory {mid}")
        return 0

    if args.cmd == "query":
        results = m.query(
            tags=args.tag,
            type=args.type,
            since=args.since,
            until=args.until,
            min_importance=args.min_importance,
            limit=args.limit,
        )
        _print_memories(results, as_json=args.json)
        return 0

    if args.cmd == "search":
        results = m.search(args.query, limit=args.limit)
        _print_memories(results, as_json=args.json)
        return 0

    if args.cmd == "recent":
        results = m.recent(
            days=args.days,
            min_importance=args.min_importance,
            limit=args.limit,
        )
        _print_memories(results, as_json=args.json)
        return 0

    if args.cmd == "source":
        results = m.by_source(args.source)
        _print_memories(results, as_json=args.json)
        return 0

    if args.cmd == "show":
        mem = m.get(args.id)
        if not mem:
            print(f"no memory with id {args.id}")
            return 1
        if args.json:
            print(json.dumps(mem.to_dict(), indent=2))
        else:
            print(mem.pretty())
        return 0

    if args.cmd == "relate":
        rid = m.relate(args.from_id, args.to_id, args.type, args.note)
        print(f"added relation {rid}: {args.from_id} -[{args.type}]-> {args.to_id}")
        return 0

    if args.cmd == "related":
        rels = m.related(args.id)
        if not rels:
            print("(no relations)")
            return 0
        for mem, rtype, note, direction in rels:
            arrow = "->" if direction == "outgoing" else "<-"
            note_s = f"  ({note})" if note else ""
            print(f"{arrow} [{mem.id}] {rtype}{note_s}")
            print("    " + mem.content.splitlines()[0][:120])
        return 0

    if args.cmd == "stats":
        print(json.dumps(m.stats(), indent=2))
        return 0

    if args.cmd == "tags":
        for category, name, n in m.list_tags():
            print(f"  {category:10} {name:30} {n}")
        return 0

    if args.cmd == "board-add":
        bid = m.add_board_item(
            content=args.content,
            author=args.author,
            kind=args.kind,
            warmth=args.warmth,
            occurred=args.occurred,
            expires=args.expires,
        )
        print(f"added board item {bid}")
        return 0

    if args.cmd == "board":
        if args.json:
            items = m.get_board(min_warmth=args.min_warmth, limit=200)
            print(json.dumps([b.to_dict() for b in items], indent=2))
        else:
            print(m.render_board_md(min_warmth=args.min_warmth))
        return 0

    if args.cmd == "board-unfiled":
        # No LIMIT. The whole point of this command is that it cannot lie by omission.
        rows = m.conn.execute(
            "SELECT * FROM board WHERE consolidated_memory_id IS NULL "
            "ORDER BY COALESCE(occurred_at, created_at), id"
        ).fetchall()
        items = [m._hydrate_board(r) for r in rows]
        total = m.conn.execute("SELECT COUNT(*) FROM board").fetchone()[0]
        if args.json:
            print(json.dumps([b.to_dict() for b in items], indent=2))
        else:
            print(f"UNFILED: {len(items)} of {total} board rows")
            for b in items:
                head = " ".join(b.content.split())[:110]
                print(f"  [{b.id}] {b.created_at[:10]} {b.kind:<9} {head}")
            if not items:
                print("  (none - board is genuinely fully filed)")
        return 0

    if args.cmd == "board-render":
        text = m.render_board_md(min_warmth=args.min_warmth)
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"rendered board -> {args.out}")
        return 0

    if args.cmd == "board-consolidate":
        mid = m.consolidate_board_item(
            args.id,
            type=args.type,
            tags=_split_csv(args.tags),
            importance=args.importance,
        )
        print(f"consolidated board item {args.id} -> memory {mid}")
        return 0

    if args.cmd == "board-decay":
        n = m.decay_board(
            before=args.before,
            max_warmth_to_cut=args.max_warmth,
            require_consolidated=not args.allow_unconsolidated,
        )
        print(f"decayed {n} board item(s)")
        if not args.allow_unconsolidated:
            held = [b for b in m.get_board(include_expired=True)
                    if b.consolidated_memory_id is None and b.expires_at
                    and b.expires_at < datetime.now().strftime("%Y-%m-%d")
                    and b.warmth <= args.max_warmth]
            if held:
                print(f"held {len(held)} expired row(s) awaiting consolidation (file-everything guard): "
                      + ", ".join(str(b.id) for b in held))
        return 0

    if args.cmd == "ingest-transcript":
        p = Path(args.path)
        targets = sorted(p.glob("*.txt")) if p.is_dir() else [p]
        for t in targets:
            info = m.ingest_transcript(t, name=args.name, chunk_lines=args.chunk_lines)
            print(f"{info['name']}: {info['status']}"
                  + (f" ({info['chunks']} chunks, {info.get('lines', '?')} lines)"
                     if info["status"] == "ingested" else ""))
        return 0

    if args.cmd == "deep-search":
        hits = m.deep_search(args.query, limit=args.limit)
        if args.json:
            print(json.dumps(hits, indent=2))
        elif not hits:
            print("(no results)")
        else:
            for h in hits:
                print(f"{h['source']}\n    {h['snippet']}\n")
        return 0

    if args.cmd == "transcript":
        log, start, end = _parse_source(args.source)
        if not log or start is None:
            print("expected name:start-end, e.g. log_08:1500-1650")
            return 1
        print(m.transcript_lines(log, start, end if end is not None else start))
        return 0

    if args.cmd == "transcript-stats":
        for r in m.transcript_stats():
            print(f"  {r['name']:24} {r['total_lines']:>7} lines  {r['chunk_count']:>5} chunks  ingested {r['ingested_at'][:10]}")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
