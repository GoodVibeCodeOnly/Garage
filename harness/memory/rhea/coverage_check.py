"""Coverage check for the nightly curation pass.

Prints a single integer: the number of board rows the curator has let fall
through -- unfiled rows that are OVERDUE. Overdue means past their expires_at,
or, with no expiry set, older than STALE_DAYS.

History. Rhea built this 2026-08-15 after a pass filed 19 rows, reported the
board fully consolidated, and left 37 unfiled because get_board() caps at 50.
A curator row proves a pass RAN, not that it FINISHED; coverage needs its own
question. Ported to Olorin and Narya 09-10.

Revised 2026-09-29 (Olorin, at Damon's word). The first version counted every
unfiled row, which is wrong in both directions -- Narya's
Inbox/curator_alarm_overfires.md named it on 09-10, Hadrian declined to port it
for the same reason, and it fired on Olorin's board 09-29 over one open thread:

- Over-fired. An open thread is SUPPOSED to stay unfiled; the curator carries
  live rows warm. A correct pass with one live thread tripped it every night,
  and an alarm that fires every day is furniture.
- Under-counted. It skipped every curator-authored row to spare the pass's own
  log line, which also hid curator-authored content rows. Only the log line
  (kind 'headline') is skipped now.

A row the truncated view hid still gets caught: it goes overdue and is counted,
because board-decay refuses unfiled rows and so it cannot quietly leave. The
catch arrives at expiry instead of the next morning. That is the trade.

Exit code is always 0; the integer on stdout is the answer. Any failure prints
-1 rather than a number, so the caller can tell "broken" from "clean" -- a check
that cannot run must never look like a check that passed.
"""

import sqlite3
import sys
from pathlib import Path

DB = Path(__file__).with_name("memory.db")
STALE_DAYS = 30


def main() -> int:
    try:
        conn = sqlite3.connect(DB)
        row = conn.execute(
            "SELECT COUNT(*) FROM board "
            "WHERE consolidated_memory_id IS NULL "
            "AND NOT (author = 'curator' AND kind = 'headline') "
            "AND ( (expires_at IS NOT NULL AND expires_at < date('now', 'localtime')) "
            "   OR (expires_at IS NULL AND created_at < datetime('now', 'localtime', ?)) )",
            (f"-{STALE_DAYS} days",),
        ).fetchone()
        print(row[0])
    except Exception as exc:  # noqa: BLE001 - the caller only needs "broken"
        print(-1)
        print(f"coverage_check failed: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
