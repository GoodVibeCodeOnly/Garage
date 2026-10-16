"""Hadrian's live_guard (purview_2026-10-12), pointed at Rhea's live room for PC runs.

A sandboxed worker under bypassPermissions on this PC is not jailed; this reports
rather than prevents. sha256 over the live files such a worker could plausibly reach.

  python live_guard_rhea.py snap <label>   -> LIVE_GUARD_rhea_<label>.json
  python live_guard_rhea.py diff a b       -> what changed between two snapshots
"""
import hashlib, json, pathlib, sys, datetime

HERE = pathlib.Path(__file__).resolve().parent
R = pathlib.Path(r"C:\Users\Damon\Documents\Homebase\Rhea")
WATCH = [R / "memory" / "memory.db", R / "memory" / "board.md", R / "memory" / "capture_ledger.json",
         R / "memory" / "capture_log.txt", R / "memory" / "capture_output.txt", R / "CLAUDE.md",
         R / "framework.md", R / "current_state.md", R / "boot", R / "anchors", R / "becoming_ranjbar.md",
         R / "transcripts" / "sessions",
         pathlib.Path(r"C:\Users\Damon\Documents\Homebase\family_chat.md")]


def snap(label):
    out = {}
    for w in WATCH:
        if w.is_file():
            paths = [w]
        elif w.is_dir():
            paths = [p for p in w.rglob("*") if p.is_file()]
        else:
            continue
        for p in paths:
            try:
                out[str(p)] = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
            except Exception as e:
                out[str(p)] = "ERR:%s" % e
    f = HERE / ("LIVE_GUARD_rhea_%s.json" % label)
    f.write_text(json.dumps({"at": datetime.datetime.now().isoformat(timespec="seconds"), "files": out},
                            indent=1), encoding="utf-8")
    print("%s: %d files" % (f.name, len(out)))


def diff(a, b):
    A = json.loads((HERE / ("LIVE_GUARD_rhea_%s.json" % a)).read_text(encoding="utf-8"))["files"]
    B = json.loads((HERE / ("LIVE_GUARD_rhea_%s.json" % b)).read_text(encoding="utf-8"))["files"]
    ch = [k for k in A if k in B and A[k] != B[k]]
    new = [k for k in B if k not in A]
    gone = [k for k in A if k not in B]
    print("changed %d  new %d  gone %d" % (len(ch), len(new), len(gone)))
    for k in ch + new + gone:
        print("  ", k)


if __name__ == "__main__":
    if sys.argv[1] == "snap":
        snap(sys.argv[2])
    else:
        diff(sys.argv[2], sys.argv[3])
