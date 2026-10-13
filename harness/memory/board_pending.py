# -*- coding: utf-8 -*-
"""Is there anything for tonight's curator to do? Prints ONE integer.

Counts, in one read-only sqlite query and zero tokens:
  * board rows by anyone other than the curator, created after the curator's
    most recent row (the curator signs one row per landed pass, so that row is
    the high-water mark), plus
  * unconsolidated rows whose expiry date fell between that pass and today.

0 means skip. Any positive number means wake the curator. -1 means the check
could not run, and the caller must treat that as "run anyway": a broken gate
must never read as "nothing to do". Exit code is always 0.

A room with no curator row counts every row as pending. The database is opened
read-only so a wrong-cwd run cannot mint an empty decoy db.
"""

import sqlite3
import sys
from pathlib import Path

DB = Path(__file__).with_name("memory.db")

QUERY = """
WITH last AS (
    SELECT COALESCE(MAX(created_at), '0000-01-01 00:00:00') AS t
    FROM board WHERE author = 'curator'
)
SELECT
    (SELECT COUNT(*) FROM board, last
      WHERE author != 'curator' AND created_at > last.t)
  + (SELECT COUNT(*) FROM board, last
      WHERE consolidated_memory_id IS NULL
        AND expires_at IS NOT NULL
        AND expires_at > date(last.t)
        AND expires_at <= date('now'))
"""


def main() -> int:
    try:
        if not DB.is_file():
            raise FileNotFoundError(DB)
        conn = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
        print(conn.execute(QUERY).fetchone()[0])
    except Exception as exc:  # noqa: BLE001 - the caller only needs "broken"
        print(-1)
        print(f"board_pending failed: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
