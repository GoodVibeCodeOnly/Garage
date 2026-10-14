"""Dump a sandbox's memory.db, row by row, so a run can be read as a before/after.

Extraction only. No counts are judged here; run_cell.py writes the dump before and after
the worker and a person reads the difference.

  python3 db_rows.py <sandbox_root> <out.json>
"""
import json, pathlib, sqlite3, sys


def dump(db_path):
    con = sqlite3.connect("file:%s?mode=ro" % pathlib.Path(db_path).as_posix(), uri=True)
    con.row_factory = sqlite3.Row
    out = {}
    for table in ("board", "memories"):
        try:
            out[table] = [dict(r) for r in con.execute("SELECT * FROM %s ORDER BY id" % table)]
        except sqlite3.Error as e:
            out[table] = {"error": str(e)}
    try:
        out["memory_tags"] = [dict(r) for r in con.execute(
            "SELECT mt.memory_id, t.category || ':' || t.name AS tag FROM memory_tags mt "
            "JOIN tags t ON t.id = mt.tag_id ORDER BY mt.memory_id")]
    except sqlite3.Error as e:
        out["memory_tags"] = {"error": str(e)}
    con.close()
    return out


def diff(before, after):
    """Which rows appeared, vanished, or changed, by id. Rows are reported whole."""
    res = {}
    for table in ("board", "memories"):
        b = {r["id"]: r for r in before.get(table, []) if isinstance(r, dict)}
        a = {r["id"]: r for r in after.get(table, []) if isinstance(r, dict)}
        res[table] = {"added": [a[i] for i in sorted(set(a) - set(b))],
                      "removed": [b[i] for i in sorted(set(b) - set(a))],
                      "changed": [{"before": b[i], "after": a[i]} for i in sorted(set(a) & set(b))
                                  if a[i] != b[i]]}
    return res


if __name__ == "__main__":
    root, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    db = root / "memory" / "memory.db"
    out.write_text(json.dumps(dump(db) if db.exists() else {"error": "no memory.db"},
                              indent=1, ensure_ascii=False), encoding="utf-8")
